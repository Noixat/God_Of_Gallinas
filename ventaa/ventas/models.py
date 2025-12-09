from django.db import models
from django.apps import apps
from django.utils import timezone

def Hotel_default():
    Hotel = apps.get_model('ventas', 'hotel')
    obj, created = Hotel.objects.get_or_create(nombre="Hotel Azapa Engineer")
    return obj.idhotel

class hotel(models.Model):
    idhotel = models.AutoField(primary_key=True )
    nombre = models.CharField(max_length=20)

    def __str__(self):
        return self.nombre

class pro_huevo(models.Model):
    idhuevo = models.AutoField(primary_key=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    nombre = models.CharField(max_length=20)

class pro_gallina(models.Model):
    idgallina = models.AutoField(primary_key=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    nombre = models.CharField(max_length=20)
    hotel = models.ForeignKey('hotel', on_delete=models.CASCADE, default=Hotel_default)
    check_in = models.DateTimeField(default=timezone.now)
    disponible = models.BooleanField(default=True)
    check_out = models.DateTimeField(null=True, blank=True)

    def realizar_check_out(self):
        self.check_out = timezone.now()
        self.disponible = False 
        self.save()

class billetera_cli(models.Model):
    dinero = models.DecimalField(max_digits=12, decimal_places=2)
    idbillcli = models.AutoField(primary_key=True)

class billetera_tien(models.Model):
    dinero = models.DecimalField(max_digits=20, decimal_places=3)
    idbilltien = models.AutoField(primary_key=True)

class venta(models.Model):
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=15, decimal_places=2)
    idventa = models.AutoField(primary_key=True)

class detalleventa(models.Model):
    pro_gallina = models.ForeignKey(pro_gallina, on_delete=models.CASCADE, null=True, blank=True)
    pro_huevo = models.ForeignKey(pro_huevo, on_delete=models.CASCADE, null=True, blank=True)
    venta = models.ForeignKey(venta, on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio_unitario = models.DecimalField(max_digits=15, decimal_places=2)

class boleta(models.Model):
    venta = models.OneToOneField(venta, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=15, decimal_places=2)
    tipo = models.CharField(max_length=10, choices=[('gallina', 'Gallina'), ('huevo', 'Huevo')])
