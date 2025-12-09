from django.urls import path
from . import views

urlpatterns = [
    path('envio/nuevo/', views.crear_envio, name='crear_envio'),
    path('seguimiento/<str:numero_seguimiento>/', views.seguimiento_envio, name='seguimiento_envio'),
]

