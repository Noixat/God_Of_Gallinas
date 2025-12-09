from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('crear/', views.crear_venta_rapida, name='crear_venta_rapida'),
    path('gallinas/', views.gallina_movimientos, name='gallina_movimientos'),
    path('venta_automatica/', views.venta_automatica, name='venta_automatica'),
]