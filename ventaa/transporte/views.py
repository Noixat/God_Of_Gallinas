from django.shortcuts import render, redirect, get_object_or_404
from django.db import transaction
from .models import Envio
from .forms import EnvioForm

def crear_envio(request):
    if request.method == 'POST':
        form = EnvioForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    nuevo_envio = form.save(commit=False)
                    nuevo_envio.save() 
                    nuevo_envio.registrar_evento(
                        ubicacion="Sucursal de Origen",
                        estado_evento="Envío ingresado y etiquetado en sucursal.",
                        nuevo_estado_envio=Envio.Estado.INGRESADO
                    )
                
                return redirect('seguimiento_envio', numero_seguimiento=nuevo_envio.numero_seguimiento)
            except Exception as e:
                form.add_error(None, f"Error inesperado al crear el envío: {e}")

    else:
        form = EnvioForm()

    return render(request, 'transporte/crear_envio.html', {'form': form})

def seguimiento_envio(request, numero_seguimiento):
    envio = get_object_or_404(Envio, numero_seguimiento=numero_seguimiento)
    
    context = {
        'envio': envio,
    }
    return render(request, 'transporte/seguimiento_envio.html', context)

