from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import SolicitudRetiro, Material 

class RegistroForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    direccion = forms.CharField(max_length=200)
    telefono = forms.CharField(max_length=15)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'direccion', 'telefono')

class SolicitudForm(forms.ModelForm):
    class Meta:
        model = SolicitudRetiro
        fields = ['material', 'cantidad', 'fecha_estimada']
        widgets = {
            'fecha_estimada': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['material'].queryset = Material.objects.all()

class OperarioSolicitudForm(forms.ModelForm):
    class Meta:
        model = SolicitudRetiro
        fields = ['estado', 'comentarios']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-select'}),
            'comentarios': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Escribe aquí tus observaciones o comentarios...'
            }),
        }
        labels = {
            'estado': 'Estado de la solicitud',
            'comentarios': 'Comentarios adicionales',
        }
