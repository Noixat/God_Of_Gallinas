from django.contrib import admin
from .models import pro_huevo, pro_gallina, billetera_cli, billetera_tien, venta, hotel, detalleventa

admin.site.register(pro_huevo)
admin.site.register(pro_gallina)
admin.site.register(billetera_cli)
admin.site.register(billetera_tien)
admin.site.register(venta)
admin.site.register(hotel)
admin.site.register(detalleventa)