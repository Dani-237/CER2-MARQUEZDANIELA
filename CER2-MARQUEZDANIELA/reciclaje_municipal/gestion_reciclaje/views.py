from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Material, SolicitudRetiro, Ciudadano
from .forms import RegistroForm, SolicitudForm, OperarioSolicitudForm
from django.db.models import Count, Avg, F, ExpressionWrapper, DurationField
from django.db.models.functions import TruncMonth
from datetime import datetime
from django.db import models
from django.http import HttpResponseForbidden
from django.contrib.auth import login as auth_login, authenticate
from django.contrib import messages
from django.utils import timezone

def index(request):
    return render(request, 'gestion_reciclaje/index.html')

def lista_materiales(request):
    materiales = Material.objects.all()
    return render(request, 'gestion_reciclaje/materiales.html', {'materiales': materiales})

def metricas(request):
    # Solicitudes por mes
    solicitudes_por_mes = (
        SolicitudRetiro.objects.annotate(mes=TruncMonth('fecha_solicitud'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('mes')
    )

    # Materiales más reciclados
    materiales_mas_reciclados = (
        SolicitudRetiro.objects.values('material__nombre')
        .annotate(total=Count('id'))
        .order_by('-total')[:5]
    )

    # Tiempo promedio entre solicitud y fecha estimada
    tiempo_promedio_dias = SolicitudRetiro.objects.annotate(
        diferencia=ExpressionWrapper(
            F('fecha_estimada') - F('fecha_solicitud'),
            output_field=DurationField()
        )
    ).aggregate(promedio=Avg('diferencia'))['promedio']

    return render(request, 'gestion_reciclaje/metricas.html', {
        'solicitudes_por_mes': solicitudes_por_mes,
        'materiales_mas_reciclados': materiales_mas_reciclados,
        'tiempo_promedio_dias': tiempo_promedio_dias.days if tiempo_promedio_dias else None,
    })

@login_required
def lista_solicitudes(request):
    if request.user.is_staff:
        solicitudes = SolicitudRetiro.objects.all()
    elif hasattr(request.user, 'operario'):
        solicitudes = SolicitudRetiro.objects.filter(operario=request.user.operario)
    else:
        if hasattr(request.user, 'ciudadano'):
            solicitudes = SolicitudRetiro.objects.filter(ciudadano=request.user.ciudadano)
        else:
            solicitudes = SolicitudRetiro.objects.none()
    
    return render(request, 'gestion_reciclaje/solicitudes.html', {'solicitudes': solicitudes})

@login_required
def nueva_solicitud(request):
    if not hasattr(request.user, 'ciudadano'):
        messages.error(request, 'Debes tener un perfil de ciudadano para crear solicitudes')
        return redirect('index')
    
    if request.method == 'POST':
        form = SolicitudForm(request.POST)
        if form.is_valid():
            solicitud = form.save(commit=False)
            solicitud.ciudadano = request.user.ciudadano
            solicitud.save()
            messages.success(request, 'Solicitud creada exitosamente')
            return redirect('solicitudes')
    else:
        form = SolicitudForm()
    return render(request, 'gestion_reciclaje/nueva_solicitud.html', {'form': form})

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            Ciudadano.objects.create(
                usuario=user,
                direccion=form.cleaned_data['direccion'],
                telefono=form.cleaned_data['telefono']
            )
            
            auth_login(request, user)
            return redirect('index')
    else:
        form = RegistroForm()
    
    return render(request, 'gestion_reciclaje/registro.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Usuario o contraseña incorrectos')
    
    return render(request, 'gestion_reciclaje/login.html')

@login_required
def detalle_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudRetiro, pk=pk)
    
    if not (request.user.is_staff or 
            (hasattr(request.user, 'operario') and solicitud.operario == request.user.operario) or
            (hasattr(request.user, 'ciudadano') and solicitud.ciudadano == request.user.ciudadano)):
        return HttpResponseForbidden("No tienes permiso para ver esta solicitud")
    
    return render(request, 'gestion_reciclaje/detalle_solicitud.html', {'solicitud': solicitud})

def puntos_limpios(request):
    return render(request, 'gestion_reciclaje/puntos_limpios.html')

def recomendaciones(request):
    return render(request, 'gestion_reciclaje/recomendaciones.html')

@login_required
def editar_solicitud_operario(request, pk):

    # Obtengo la solicitud o devuelvo 404 si no existe
    solicitud = get_object_or_404(SolicitudRetiro, pk=pk)

    # Verifico que el usuario autenticado tenga perfil de operario
    if not hasattr(request.user, 'operario'):
        # Si no tiene perfil Operario, prohibo el acceso
        return HttpResponseForbidden("No tienes permiso para acceder a esta página.")

    # Verifico que esta solicitud esté asignada a este operario
    if solicitud.operario != request.user.operario:
        return HttpResponseForbidden("Esta solicitud no está asignada a ti.")

    # Si la solicitud ya está completada, no permitir edición adicional
    if solicitud.estado == 'COM':
        messages.info(request, "Esta solicitud ya se encuentra completada y no se puede modificar.")
        return redirect('lista_solicitudes')

    if request.method == 'POST':
        form = OperarioSolicitudForm(request.POST, instance=solicitud)
        if form.is_valid():
            actual = form.save(commit=False)
            # Si cambió a 'COM', registro la fecha de completado
            if actual.estado == 'COM' and solicitud.estado != 'COM':
                actual.fecha_completada = timezone.now()
            actual.save()
            messages.success(request, "Solicitud actualizada correctamente.")
            return redirect('lista_solicitudes')
    else:
        form = OperarioSolicitudForm(instance=solicitud)

    return render(request, 'gestion_reciclaje/editar_solicitud_operario.html', {
        'form': form,
        'solicitud': solicitud,
    })
