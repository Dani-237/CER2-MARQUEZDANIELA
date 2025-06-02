from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('registro/', views.registro, name='registro'),
    path('materiales/', views.lista_materiales, name='materiales'),
    path('metricas/', views.metricas, name='metricas'),
    path('solicitudes/', views.lista_solicitudes, name='solicitudes'),
    path('solicitudes/nueva/', views.nueva_solicitud, name='nueva_solicitud'),
    path('solicitudes/<int:pk>/', views.detalle_solicitud, name='detalle_solicitud'),
    path('login/', auth_views.LoginView.as_view(template_name='gestion_reciclaje/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('puntos-limpios/', views.puntos_limpios, name='puntos_limpios'),
    path('recomendaciones/', views.recomendaciones, name='recomendaciones'),
    path('solicitudes/<int:pk>/editar/', views.editar_solicitud_operario, name='editar_solicitud_operario')

]
