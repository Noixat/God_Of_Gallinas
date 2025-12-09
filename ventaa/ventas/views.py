from django.shortcuts import render
from .models import venta, detalleventa, pro_gallina, pro_huevo, billetera_cli, billetera_tien, boleta
from django.db import transaction

def home(request):
   
    gallinas_disponibles = pro_gallina.objects.filter(disponible=True)
    huevos_disponibles = pro_huevo.objects.filter(stock__gt=0)
    context = {
        'gallinas': gallinas_disponibles,
        'huevos': huevos_disponibles,
    }
    return render(request, 'ventas/home.html', context)

def crear_venta_rapida(request):
    mensaje = ""
    detalles_venta = []

    gallinas_disponibles = pro_gallina.objects.filter(disponible=True)
    huevos_disponibles = pro_huevo.objects.filter(stock__gt=0)

    if request.method == 'POST':
        try:
            with transaction.atomic():
            
                cantidad_gallinas = int(request.POST.get('cantidad_gallinas', 0))
                cantidad_huevos = int(request.POST.get('cantidad_huevos', 0))

                if cantidad_gallinas <= 0 and cantidad_huevos <= 0:
                    raise ValueError("No se ha seleccionado ningún producto para la venta.")

                cliente = billetera_cli.objects.first()
                granjero = billetera_tien.objects.first()

                if not cliente or not granjero:
                    raise ValueError("Billeteras no configuradas.")

                total_venta = 0
                detalles_para_crear = []

          
                gallinas_a_vender = []
                if cantidad_gallinas > 0:
                    gallinas_a_vender = list(pro_gallina.objects.select_for_update().filter(disponible=True)[:cantidad_gallinas])
                    
                    if len(gallinas_a_vender) < cantidad_gallinas:
                        raise ValueError(f"No hay suficientes gallinas disponibles. Se solicitaron {cantidad_gallinas} pero solo hay {len(gallinas_a_vender)}.")

                    for gallina in gallinas_a_vender:
                        total_venta += gallina.precio
                        detalles_para_crear.append({'tipo': 'gallina', 'producto': gallina, 'cantidad': 1, 'precio': gallina.precio})

               
                huevo_a_vender = None
                if cantidad_huevos > 0:
                    huevo_a_vender = pro_huevo.objects.select_for_update().filter(stock__gt=0).first()
                    if not huevo_a_vender:
                        raise ValueError("No hay huevos disponibles para la venta.")
                    if huevo_a_vender.stock < cantidad_huevos:
                        raise ValueError("No hay suficientes huevos en stock.")
                    
                    total_venta += huevo_a_vender.precio * cantidad_huevos
                    detalles_para_crear.append({'tipo': 'huevo', 'producto': huevo_a_vender, 'cantidad': cantidad_huevos, 'precio': huevo_a_vender.precio})

         
                if cliente.dinero < total_venta:
                    raise ValueError(f"Fondos insuficientes. Se necesita ${total_venta:.2f} y solo tiene ${cliente.dinero:.2f}.")

                cliente.dinero -= total_venta
                granjero.dinero += total_venta
                cliente.save()
                granjero.save()

       
                for gallina in gallinas_a_vender:
                    gallina.realizar_check_out() 
                
                if huevo_a_vender and cantidad_huevos > 0:
                    huevo_a_vender.stock -= cantidad_huevos
                    huevo_a_vender.save()

        
                nueva_venta = venta.objects.create(total=total_venta)
                for detalle in detalles_para_crear:
                    dv = detalleventa.objects.create(
                        venta=nueva_venta,
                        pro_gallina=detalle['producto'] if detalle['tipo'] == 'gallina' else None,
                        pro_huevo=detalle['producto'] if detalle['tipo'] == 'huevo' else None,
                        cantidad=detalle['cantidad'],
                        precio_unitario=detalle['precio']
                    )
                  
                    if detalle['tipo'] == 'gallina':
                        nombre = dv.pro_gallina.nombre
                        pid = dv.pro_gallina.idgallina
                        tipo = 'Gallina'
                    else:
                        nombre = dv.pro_huevo.nombre
                        pid = dv.pro_huevo.idhuevo
                        tipo = 'Huevo'
                    detalles_venta.append({
                        'producto_nombre': nombre,
                        'producto_id': pid,
                        'tipo': tipo,
                        'cantidad': dv.cantidad,
                        'precio_unitario': dv.precio_unitario,
                        'subtotal': dv.cantidad * dv.precio_unitario,
                    })

                mensaje = f"Venta realizada con éxito. Total: ${total_venta:.2f}"

        except ValueError as e:
            mensaje = str(e)
        except Exception as e:
            mensaje = f"Ocurrió un error inesperado: {e}"

    context = {
        'mensaje': mensaje,
        'gallinas': gallinas_disponibles,
        'huevos': huevos_disponibles,
        'detalles_venta': detalles_venta,
    }
    return render(request, 'ventas/venta_form.html', context)

def venta_automatica(request): 
    mensaje = ""
    venta_realizada = None
    detalles_venta_realizada = []

    if request.method == 'POST':
        try:
            with transaction.atomic():
                cliente = billetera_cli.objects.select_for_update().first() 
                granjero = billetera_tien.objects.select_for_update().first() 
                gallina = pro_gallina.objects.select_for_update().filter(disponible=True).first() 
                huevo = pro_huevo.objects.select_for_update().filter(stock__gt=0).first() 

                if not all([cliente, granjero, gallina, huevo]):
                    raise ValueError("No hay suficientes productos o billeteras para la venta automática.")

                cantidad_huevos = 5
                if huevo.stock < cantidad_huevos:
                    raise ValueError(f"No hay suficientes huevos en stock para la venta automática (se requieren {cantidad_huevos}).")

                total_gallina = gallina.precio
                total_huevos = huevo.precio * cantidad_huevos
                total_venta = total_gallina + total_huevos

                if cliente.dinero < total_venta:
                    raise ValueError(f"Fondos del cliente insuficientes. Se necesitan ${total_venta:.2f}.")

                
                cliente.dinero -= total_venta
                granjero.dinero += total_venta
                
        
                gallina.realizar_check_out()
                huevo.stock -= cantidad_huevos
                
             
                cliente.save()
                granjero.save()
                huevo.save()
         

          
                nueva_venta = venta.objects.create(total=total_venta)
                detalle_gallina = detalleventa.objects.create(venta=nueva_venta, pro_gallina=gallina, cantidad=1, precio_unitario=gallina.precio)
                detalle_huevo = detalleventa.objects.create(venta=nueva_venta, pro_huevo=huevo, cantidad=cantidad_huevos, precio_unitario=huevo.precio)
                
                venta_realizada = nueva_venta
                detalles_venta_realizada = [
                    {'producto_nombre': detalle_gallina.pro_gallina.nombre, 'producto_id': detalle_gallina.pro_gallina.idgallina, 'tipo': 'Gallina', 'cantidad': detalle_gallina.cantidad, 'precio_unitario': detalle_gallina.precio_unitario, 'subtotal': detalle_gallina.cantidad * detalle_gallina.precio_unitario},
                    {'producto_nombre': detalle_huevo.pro_huevo.nombre, 'producto_id': detalle_huevo.pro_huevo.idhuevo, 'tipo': 'Huevo', 'cantidad': detalle_huevo.cantidad, 'precio_unitario': detalle_huevo.precio_unitario, 'subtotal': detalle_huevo.cantidad * detalle_huevo.precio_unitario}
                ]

                mensaje = f"Venta automática procesada con éxito. Total: ${total_venta:.2f}"

        except ValueError as e:
            mensaje = str(e)
            venta_realizada = None
            detalles_venta_realizada = []
        except Exception as e:
            mensaje = f"Ocurrió un error inesperado: {e}"
            venta_realizada = None
            detalles_venta_realizada = []

    context = {
        'mensaje': mensaje,
        'venta_realizada': venta_realizada,
        'detalles_venta_realizada': detalles_venta_realizada,
    }
    return render(request, 'ventas/venta_automatica.html', context)


def gallina_movimientos(request):
    """Vista que lista check_in y check_out de las gallinas."""
    gallinas = pro_gallina.objects.all().order_by('-check_in')
    context = {
        'gallinas': gallinas,
    }
    return render(request, 'ventas/gallina_movimientos.html', context)