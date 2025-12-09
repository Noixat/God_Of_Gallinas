from django.db import models
from django.utils import timezone
import uuid

def generar_numero_seguimiento():
    return str(uuid.uuid4().hex)[:12].upper()

class Envio(models.Model):

    class Estado(models.TextChoices):
        INGRESADO = 'INGRESADO', 'Ingresado en Sucursal'
        EN_TRANSITO = 'EN_TRANSITO', 'En Tránsito a Centro de Distribución'
        EN_REPARTO = 'EN_REPARTO', 'En Reparto a Domicilio'
        ENTREGADO = 'ENTREGADO', 'Entregado'
        ENTREGA_FALLIDA = 'ENTREGA_FALLIDA', 'Entrega Fallida'
        DEVUELTO = 'DEVUELTO', 'Devuelto al Remitente'

    numero_seguimiento = models.CharField(
        max_length=12, unique=True, default=generar_numero_seguimiento, editable=False
    )
    remitente_nombre = models.CharField(max_length=100)
    destinatario_nombre = models.CharField(max_length=100)
    destinatario_direccion = models.TextField()
    
    peso_kg = models.DecimalField(max_digits=6, decimal_places=2, help_text="Peso en kilogramos (kg)")
    
    estado_actual = models.CharField(
        max_length=20, choices=Estado.choices, default=Estado.INGRESADO
    )
    fecha_creacion = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Envío {self.numero_seguimiento} - {self.get_estado_actual_display()}"

    def registrar_evento(self, ubicacion, estado_evento, nuevo_estado_envio):
        EventoTrazabilidad.objects.create(
            envio=self,
            ubicacion=ubicacion,
            estado=estado_evento
        )
        self.estado_actual = nuevo_estado_envio
        self.save()

class EventoTrazabilidad(models.Model):
    envio = models.ForeignKey(Envio, on_delete=models.CASCADE, related_name='eventos')
    fecha_hora = models.DateTimeField(default=timezone.now)
    ubicacion = models.CharField(max_length=100, help_text="Ej: Sucursal Providencia, Hub Santiago, En ruta a Valparaíso")
    estado = models.CharField(max_length=100, help_text="Ej: Envío ingresado por cliente, En centro de clasificación")

    class Meta:
        ordering = ['-fecha_hora']

    def __str__(self):
        return f"{self.envio.numero_seguimiento} @ {self.fecha_hora.strftime('%Y-%m-%d %H:%M')}: {self.estado}"



