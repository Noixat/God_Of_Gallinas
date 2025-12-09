from django.contrib import admin
from .models import Envio, EventoTrazabilidad

class EventoTrazabilidadInline(admin.TabularInline):
    model = EventoTrazabilidad
    extra = 1
    readonly_fields = ('fecha_hora',)

@admin.register(Envio)
class EnvioAdmin(admin.ModelAdmin):
    list_display = ('numero_seguimiento', 'remitente_nombre', 'destinatario_nombre', 'estado_actual', 'fecha_creacion')
    list_filter = ('estado_actual', 'fecha_creacion')
    readonly_fields = ('numero_seguimiento', 'fecha_creacion')
    inlines = [EventoTrazabilidadInline]

admin.site.register(EventoTrazabilidad)

