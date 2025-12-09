from django import forms
from .models import Envio

class EnvioForm(forms.ModelForm):
    class Meta:
        model = Envio
        fields = [
            'remitente_nombre', 
            'destinatario_nombre', 
            'destinatario_direccion', 
            'peso_kg'
        ]
