from django.shortcuts import render, redirect
from .models import Cliente, Destino, Encomienda
## Para añadir los alert bonitos 
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.utils import timezone
# Create your views here.

def inicio(request):
    #Presentando en pantalla el contenidp de
    return render(request, 'inicio.html')


def newcliente(request):
    return render(request, 'newcliente.html')

def newencomienda(request):
    clientes = Cliente.objects.all()
    return render(request, 'newencomienda.html', {
        'clientes': clientes
    })

def guardar_Cliente(request):
    nombre_f=request.POST.get('nombre')
    apellido_f=request.POST.get('apellido')
    cedula_f=request.POST.get('cedula')
    email_f=request.POST.get('email')
    telefono_f=request.POST.get('telefono')
    cliente_f=Cliente.objects.create(
        nombre=nombre_f,
        apellido=apellido_f,
        cedula=cedula_f,
        email=email_f,
        telefono=telefono_f
    )
    messages.success(request ,f'{cliente_f.nombre } {cliente_f.apellido} ha sido ingresado al sistema correctamente')
    return redirect('/showclientes')

def showclientes(request):
    clientes=Cliente.objects.all()
    return render(request, 'showclientes.html',
                  {'misclientes':clientes})

def eliminarcliente(request,id):
    ##Capturar el ID
    #El primer parametro id es el de la BDD
    #El segundo es el que acompaña a request osea la vbaribla
    clienteElimado=Cliente.objects.get(id=id)
    clienteElimado.delete()
    messages.success(request,f'Cliente {clienteElimado.nombre} {clienteElimado.apellido} eliminado exitosamente')
    messages.warning(request,"Estas seguro de eliminar")
    return redirect('/showclientes')
##Como eliminar las imagenes e archivos 


## Encomiendas y Destinos

def showencomiendas(request):
    encomiendas = Encomienda.objects.select_related('cliente', 'destino').all().order_by('-fecha_envio')

    return render(request, 'showencomiendas.html', {
        'encomiendas': encomiendas
    })

def guardar_encomienda(request):
    # -------- CLIENTE --------
    cliente_id = request.POST.get('cliente')
    cliente = Cliente.objects.get(id=cliente_id)

    # -------- DESTINO + DESTINATARIO --------
    ciudad_f = request.POST.get('ciudad')
    direccion_f = request.POST.get('direccion')
    codigo_postal_f = request.POST.get('codigo_postal')
    nombre_destinatario_f = request.POST.get('nombre_destinatario')
    cedula_destinatario_f = request.POST.get('cedula_destinatario')
    email_destinatario_f = request.POST.get('email_destinatario')
    telefono_destinatario_f = request.POST.get('telefono_destinatario')

    destino_f = Destino.objects.create(
        ciudad=ciudad_f,
        direccion=direccion_f,
        codigo_postal=codigo_postal_f,
        nombre_destinatario=nombre_destinatario_f,
        cedula_destinatario=cedula_destinatario_f,
        email_destinatario=email_destinatario_f,
        telefono_destinatario=telefono_destinatario_f
    )
    # -------- ENCOMIENDA --------
    descripcion_f = request.POST.get('descripcion')
    peso_f = request.POST.get('peso')
    precio_f = request.POST.get('precio')
    transporte_f = request.POST.get('transporte')
    fecha_estimada_f = request.POST.get('fecha_estimada')

    encomienda_f = Encomienda.objects.create(
        cliente=cliente,
        destino=destino_f,
        descripcion=descripcion_f,
        peso=peso_f,
        precio=precio_f,
        transporte=transporte_f,
        fecha_estimada=fecha_estimada_f
    )

    messages.success(request, f'Encomienda registrada correctamente para {cliente.nombre}')
    return redirect('/showencomiendas')



def eliminarencomienda(request, id):
    encomienda = Encomienda.objects.get(id=id)
    encomienda.delete()

    messages.success(request, "Encomienda eliminada correctamente")
    return redirect('/showencomiendas')


def rastrear_encomienda(request):
    encomienda = None
    buscado = False

    if request.method == 'POST':
        codigo_ingresado = request.POST.get('codigo', '').strip()
        buscado = True

        try:
            # Busca por coincidencia parcial del UUID (ya que el cliente
            # solo tiene el código corto tipo LE-A3F8B2C1)
            encomienda = Encomienda.objects.select_related('cliente', 'destino').get(
                codigo__istartswith=codigo_ingresado.replace('LE-', '').replace('LE', '')
            )
        except Encomienda.DoesNotExist:
            encomienda = None
        except Encomienda.MultipleObjectsReturned:
            # Si el código corto coincide con más de una encomienda,
            # toma la primera coincidencia
            encomienda = Encomienda.objects.select_related('cliente', 'destino').filter(
                codigo__istartswith=codigo_ingresado.replace('LE-', '').replace('LE', '')
            ).first()

    return render(request, 'rastrear.html', {
        'encomienda': encomienda,
        'buscado': buscado
    })


#Edición de Cliente

def editcliente(request, id):
    #Capturar el cliente a editar
    cliente = Cliente.objects.get(id=id)
    return render(request, 'editCliente.html', {
        'cliente': cliente
    })

def actualizar_cliente(request, id):
    cliente = Cliente.objects.get(id=id)

    cliente.nombre = request.POST.get('nombre')
    cliente.apellido = request.POST.get('apellido')
    cliente.cedula = request.POST.get('cedula')
    cliente.email = request.POST.get('email')
    cliente.telefono = request.POST.get('telefono')
    cliente.save()

    messages.success(request, f'{cliente.nombre} {cliente.apellido} ha sido actualizado correctamente')
    return redirect('/showclientes')


# Edición de Encomienda
def editencomienda(request, id):
    #Capturar la encomienda a editar
    encomienda = Encomienda.objects.select_related('cliente', 'destino').get(id=id)
    clientes = Cliente.objects.all()

    return render(request, 'editEncomienda.html', {
        'encomienda': encomienda,
        'clientes': clientes
    })

def actualizar_encomienda(request, id):
    encomienda = Encomienda.objects.select_related('destino').get(id=id)

    #Cliente
    cliente_id = request.POST.get('cliente')
    cliente = Cliente.objects.get(id=cliente_id)

    #Guardamos el email anterior antes de sobreescribirlo
    email_anterior = encomienda.destino.email_destinatario
    email_nuevo = request.POST.get('email_destinatario')

    #Destino + Destinatario
    encomienda.destino.ciudad = request.POST.get('ciudad')
    encomienda.destino.direccion = request.POST.get('direccion')
    encomienda.destino.codigo_postal = request.POST.get('codigo_postal')
    encomienda.destino.nombre_destinatario = request.POST.get('nombre_destinatario')
    encomienda.destino.cedula_destinatario = request.POST.get('cedula_destinatario')
    encomienda.destino.email_destinatario = email_nuevo
    encomienda.destino.telefono_destinatario = request.POST.get('telefono_destinatario')
    encomienda.destino.save()

    #Encomienda
    encomienda.cliente = cliente
    encomienda.descripcion = request.POST.get('descripcion')
    encomienda.peso = request.POST.get('peso')
    encomienda.precio = request.POST.get('precio')
    encomienda.estado = request.POST.get('estado')
    encomienda.transporte = request.POST.get('transporte')
    fecha_estimada_str = request.POST.get('fecha_estimada')
    fecha_estimada_dt = datetime.strptime(fecha_estimada_str, '%Y-%m-%dT%H:%M')
    encomienda.fecha_estimada = timezone.make_aware(fecha_estimada_dt)
    encomienda.save()

    #Si el correo del destinatario cambió, le enviamos los datos actualizados
    if email_nuevo and email_nuevo != email_anterior:
        enviar_correo_actualizacion(encomienda)

    messages.success(request, f'Encomienda actualizada correctamente para {cliente.nombre}')
    return redirect('/showencomiendas')

def enviar_correo_actualizacion(encomienda):
    asunto = f'Actualización de tu envío LE-{str(encomienda.codigo)[:8].upper()}'
    mensaje = (
        f'Hola {encomienda.destino.nombre_destinatario},\n\n'
        f'Se ha registrado tu correo como destinatario de una encomienda de LataExpress.\n\n'
        f'Código de rastreo: LE-{str(encomienda.codigo)}\n'
        f'Cliente remitente: {encomienda.cliente.nombre} {encomienda.cliente.apellido}\n'
        f'Destino: {encomienda.destino.ciudad} - {encomienda.destino.direccion}\n'
        f'Descripción: {encomienda.descripcion}\n'
        f'Estado actual: {encomienda.get_estado_display()}\n'
        f'Fecha estimada de entrega: {encomienda.fecha_estimada.strftime("%d/%m/%Y %H:%M")}\n\n'
        f'Puedes rastrear tu encomienda ingresando el código en nuestro sistema.\n\n'
        f'Saludos,\nEquipo LataExpress'
    )

    send_mail(
        asunto,
        mensaje,
        settings.DEFAULT_FROM_EMAIL,
        [encomienda.destino.email_destinatario],
        fail_silently=False,
    )