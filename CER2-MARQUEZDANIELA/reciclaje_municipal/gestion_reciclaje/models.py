from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator

class Material(models.Model):
    codigo = models.CharField(max_length=4, primary_key=True, verbose_name="Código")
    nombre = models.CharField(max_length=50, verbose_name="Nombre del material")
    descripcion = models.TextField(verbose_name="Descripción")
    
    class Meta:
        verbose_name = "Material"
        verbose_name_plural = "Materiales"
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"

class Ciudadano(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    direccion = models.CharField(max_length=200, verbose_name="Dirección completa")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono de contacto")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")

    class Meta:
        verbose_name = "Ciudadano"
        verbose_name_plural = "Ciudadanos"

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username}"

class Operario(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Usuario")
    telefono = models.CharField(max_length=15, verbose_name="Teléfono de contacto")
    fecha_contratacion = models.DateField(auto_now_add=True, verbose_name="Fecha de contratación")  # Auto_now_add para simplificar
    capacidad_diaria = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1)],
        verbose_name="Capacidad diaria de retiros"
    )
    
    class Meta:
        verbose_name = "Operario"
        verbose_name_plural = "Operarios"
        ordering = ['usuario__username']

    def __str__(self):
        return f"{self.usuario.get_full_name() or self.usuario.username}"
    
class SolicitudRetiro(models.Model):
    ESTADOS = [
        ('PEN', 'Pendiente'),
        ('RUT', 'En ruta'),
        ('COM', 'Completada'),
        ('CAN', 'Cancelada'),
    ]
    
    ciudadano = models.ForeignKey(Ciudadano, on_delete=models.CASCADE, verbose_name="Ciudadano solicitante")
    material = models.ForeignKey(Material, on_delete=models.PROTECT, verbose_name="Material a retirar")
    cantidad = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Cantidad estimada"
    )
    fecha_solicitud = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de solicitud")
    fecha_estimada = models.DateField(verbose_name="Fecha estimada de retiro")
    estado = models.CharField(
        max_length=3,
        choices=ESTADOS,
        default='PEN',
        verbose_name="Estado actual"
    )
    operario = models.ForeignKey(
        Operario,  # Cambiado de User a Operario (consistencia con tu modelo)
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Operario asignado"
    )
    comentarios = models.TextField(blank=True, verbose_name="Observaciones")

    class Meta:
        verbose_name = "Solicitud de retiro"
        verbose_name_plural = "Solicitudes de retiro"
        ordering = ['-fecha_solicitud']
        permissions = [
            ("can_assign_request", "Puede asignar solicitudes a operarios"),
        ]

    def get_codigo(self):
        return f"SR-{self.id:04d}"

    def __str__(self):
        return f"{self.get_codigo()} | {self.get_estado_display()} | {self.material.nombre}"