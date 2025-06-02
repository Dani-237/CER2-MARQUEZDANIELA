from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Material, Ciudadano, Operario, SolicitudRetiro
from django.utils.html import format_html
from django.urls import reverse
from django import forms

# 1. Configuración extendida para User en el Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'tipo_usuario')
    list_filter = ('is_staff', 'is_superuser', 'groups')
    
    def tipo_usuario(self, obj):
        if hasattr(obj, 'operario'):
            return "Operario"
        elif hasattr(obj, 'ciudadano'):
            return "Ciudadano"
        return "Staff/Superuser"
    tipo_usuario.short_description = 'Rol'

# 2. Admin para Materiales
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'nombre', 'descripcion_corta')
    search_fields = ('nombre', 'codigo')
    
    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + '...' if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = 'Descripción'

# 3. Admin para Ciudadanos
class CiudadanoAdmin(admin.ModelAdmin):
    list_display = ('usuario_link', 'direccion', 'telefono', 'fecha_registro')
    search_fields = ('usuario__username', 'direccion')
    raw_id_fields = ('usuario',)
    
    def usuario_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.usuario.id])
        return format_html('<a href="{}">{}</a>', url, obj.usuario.username)
    usuario_link.short_description = 'Usuario'
    usuario_link.admin_order_field = 'usuario__username'

# 4. Admin para Operarios
class OperarioAdmin(admin.ModelAdmin):
    list_display = ('usuario_link', 'telefono', 'fecha_contratacion', 'capacidad_diaria')
    list_editable = ('capacidad_diaria',)
    search_fields = ('usuario__username', 'telefono')
    
    def usuario_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.usuario.id])
        return format_html('<a href="{}">{}</a>', url, obj.usuario.username)
    usuario_link.short_description = 'Usuario'
    usuario_link.admin_order_field = 'usuario__username'

# 5. Formulario personalizado para asignar operarios
class AsignarOperarioForm(forms.Form):
    operario = forms.ModelChoiceField(
        queryset=Operario.objects.all(),
        label="Seleccionar operario"
    )

# 6. Admin para Solicitudes de Retiro
class SolicitudRetiroAdmin(admin.ModelAdmin):
    list_display = (
        'id_formateado', 
        'ciudadano_link', 
        'material_link', 
        'cantidad', 
        'fecha_solicitud', 
        'estado_badge',
        'operario_link'
    )
    list_filter = ('estado', 'material', 'fecha_solicitud')
    search_fields = ('ciudadano__usuario__username', 'material__nombre')
    actions = ['asignar_operario']
    readonly_fields = ('fecha_solicitud',)
    
    # Campos calculados para mejor visualización
    def id_formateado(self, obj):
        return f"SR-{obj.id:04d}"
    id_formateado.short_description = 'ID'
    
    def ciudadano_link(self, obj):
        url = reverse('admin:gestion_reciclaje_ciudadano_change', args=[obj.ciudadano.id])
        return format_html('<a href="{}">{}</a>', url, obj.ciudadano)
    ciudadano_link.short_description = 'Ciudadano'
    
    def material_link(self, obj):
        url = reverse('admin:gestion_reciclaje_material_change', args=[obj.material.codigo])
        return format_html('<a href="{}">{}</a>', url, obj.material)
    material_link.short_description = 'Material'
    
    def operario_link(self, obj):
        if obj.operario:
            url = reverse('admin:gestion_reciclaje_operario_change', args=[obj.operario.id])
            return format_html('<a href="{}">{}</a>', url, obj.operario)
        return "Sin asignar"
    operario_link.short_description = 'Operario'
    
    def estado_badge(self, obj):
        color = {
            'PEN': 'orange',
            'RUT': 'blue',
            'COM': 'green',
            'CAN': 'red'
        }.get(obj.estado, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 4px;">{}</span>',
            color,
            obj.get_estado_display()
        )
    estado_badge.short_description = 'Estado'
    
    # Acción para asignar operarios
    def asignar_operario(self, request, queryset):
        from django.shortcuts import render
        
        if 'apply' in request.POST:
            form = AsignarOperarioForm(request.POST)
            if form.is_valid():
                operario = form.cleaned_data['operario']
                count = queryset.update(operario=operario, estado='RUT')
                self.message_user(request, f"{count} solicitudes asignadas al operario {operario}")
                return
        else:
            form = AsignarOperarioForm()
        
        return render(request, 'admin/asignar_operario.html', {
            'solicitudes': queryset,
            'form': form,
            'opts': self.model._meta
        })
    asignar_operario.short_description = "Asignar operario a solicitudes seleccionadas"

# Registro de modelos
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Material, MaterialAdmin)
admin.site.register(Ciudadano, CiudadanoAdmin)
admin.site.register(Operario, OperarioAdmin)
admin.site.register(SolicitudRetiro, SolicitudRetiroAdmin)

# Personalización del Admin
admin.site.site_header = "Administración de Reciclaje Municipal"
admin.site.site_title = "Sistema de Gestión de Reciclaje"
admin.site.index_title = "Panel de Control"