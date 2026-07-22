from django.shortcuts import render, redirect
from .models import Cliente, Destino, Encomienda
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import user_passes_test
# Para añadir los alert bonitos 
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from datetime import datetime
from django.utils import timezone
from django.core.mail import EmailMessage
# Create your views here.


def es_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='admin').exists()
    )


def es_transportista(user):
    return user.is_authenticated and user.groups.filter(name='transportista').exists()


def requiere_admin(view_func):
    return user_passes_test(es_admin, login_url='/login/')(view_func)


def requiere_admin_o_transportista(view_func):
    return user_passes_test(
        lambda user: es_admin(user) or es_transportista(user),
        login_url='/login/'
    )(view_func)


def login_view(request):
    if request.user.is_authenticated:
        return redireccion_por_rol(request.user)

    if request.method == 'POST':
        usuario = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if usuario is not None:
            login(request, usuario)
            return redireccion_por_rol(usuario)
        messages.error(request, 'Usuario o contraseña incorrectos.')

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    return redirect('/login/')


def redireccion_por_rol(user):
    if es_transportista(user) and not es_admin(user):
        return redirect('/actualizar_estados/')
    return redirect('/showclientes/')

def inicio(request):
    #Presentando en pantalla el contenidp de
    return render(request, 'inicio.html')


@requiere_admin
def newcliente(request):
    return render(request, 'newcliente.html')

@requiere_admin
def newencomienda(request):
    clientes = Cliente.objects.all()
    return render(request, 'newencomienda.html', {
        'clientes': clientes
    })
#Para ver detalle de la encomienda mas bonito
def detalle_encomienda(request, id):
    encomienda = Encomienda.objects.select_related('cliente', 'destino').get(id=id)

    return render(request, 'detalle_encomienda.html', {
        'encomienda': encomienda
    })

@requiere_admin
def guardar_Cliente(request):
    nombre_f = request.POST.get('nombre')
    apellido_f = request.POST.get('apellido')
    cedula_f = request.POST.get('cedula')
    email_f = request.POST.get('email')
    telefono_f = request.POST.get('telefono')

    if Cliente.objects.filter(cedula=cedula_f).exists():
        messages.error(request, f'Ya existe un cliente registrado con la cédula {cedula_f}')
        return render(request, 'newcliente.html', {
            'datos': request.POST  # le devolvemos lo que ya escribió
        })

    cliente_f = Cliente.objects.create(
        nombre=nombre_f,
        apellido=apellido_f,
        cedula=cedula_f,
        email=email_f,
        telefono=telefono_f
    )
    messages.success(request, f'{cliente_f.nombre} {cliente_f.apellido} ha sido ingresado al sistema correctamente')
    return redirect('/showclientes')

@requiere_admin
def showclientes(request):
    clientes=Cliente.objects.all()
    return render(request, 'showclientes.html',
                  {'misclientes':clientes})

@requiere_admin
def eliminarcliente(request,id):
    ##Capturar el ID, el primer parametro id es el de la BDD y el segundo es el que acompaña a request osea la variable
    clienteElimado=Cliente.objects.get(id=id)
    clienteElimado.delete()
    messages.success(request,f'Cliente {clienteElimado.nombre} {clienteElimado.apellido} eliminado exitosamente')
    messages.warning(request,"Cliente eliminado exitosamente")
    return redirect('/showclientes')

#Encomiendas y Destinos

@requiere_admin
def showencomiendas(request):
    encomiendas = Encomienda.objects.select_related('cliente', 'destino').all().order_by('-fecha_envio')

    return render(request, 'showencomiendas.html', {
        'encomiendas': encomiendas
    })

@requiere_admin
def guardar_encomienda(request):
    # Cliente
    cliente_id = request.POST.get('cliente')
    cliente = Cliente.objects.get(id=cliente_id)

    #Destino y Destinatario
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
    #Encomienda
    descripcion_f = request.POST.get('descripcion')
    peso_f = request.POST.get('peso')
    precio_f = request.POST.get('precio')
    estado_f = request.POST.get('estado')
    transporte_f = request.POST.get('transporte')
    fecha_estimada_str = request.POST.get('fecha_estimada')
    fecha_estimada_dt = datetime.strptime(
        fecha_estimada_str,
        '%Y-%m-%dT%H:%M'
    )
    fecha_estimada_f = timezone.make_aware(fecha_estimada_dt)

    encomienda_f = Encomienda.objects.create(
        cliente=cliente,
        destino=destino_f,
        descripcion=descripcion_f,
        peso=peso_f,
        precio=precio_f,
        nombre_destinatario=nombre_destinatario_f,
        cedula_destinatario=cedula_destinatario_f,
        email_destinatario=email_destinatario_f,
        telefono_destinatario=telefono_destinatario_f,
        estado=estado_f,
        transporte=transporte_f,
        fecha_estimada=fecha_estimada_f
    )
    enviar_correo_encomienda(encomienda_f)
    messages.success(request, f'Encomienda registrada correctamente para {cliente.nombre}')
    return redirect('/showencomiendas')


def enviar_correo_encomienda(encomienda):

    fecha_estimada = encomienda.fecha_estimada

    #Convertir si viene como string
    if isinstance(fecha_estimada, str):
        try:
            fecha_estimada = datetime.fromisoformat(fecha_estimada)
        except:
            fecha_estimada = datetime.strptime(fecha_estimada, "%Y-%m-%d %H:%M:%S")
    #Correo para el cliente (remitente)
    if encomienda.cliente.email:
        mensaje_cliente = (
            f'Hola {encomienda.cliente.nombre} {encomienda.cliente.apellido},\n\n'
            f'Tu encomienda ha sido registrada exitosamente en LataExpress.\n\n'
            f'Código de rastreo: LE-{str(encomienda.codigo)}\n'
            f'Destinatario: {encomienda.destino.nombre_destinatario}\n'
            f'Destino: {encomienda.destino.ciudad} - {encomienda.destino.direccion}\n'
            f'Descripción: {encomienda.descripcion}\n'
            f'Estado actual: {encomienda.get_estado_display()}\n'
            f'Fecha estimada de entrega: {fecha_estimada.strftime("%d/%m/%Y %H:%M")}\n\n'
            f'Puedes rastrear tu encomienda ingresando el código en nuestro sistema.\n\n'
            f'Saludos,\nEquipo LataExpress'
        )

        EmailMessage(
            subject='Tu encomienda ha sido registrada',
            body=mensaje_cliente,
            to=[encomienda.cliente.email],
        ).send()

    #Correo para el destinatario
    if encomienda.destino.email_destinatario:
        mensaje_destinatario = (
            f'Hola {encomienda.destino.nombre_destinatario},\n\n'
            f'Se ha actualizado la encomienda de la cual eres destinatario en LataExpress.\n\n'
            f'Código de rastreo: LE-{str(encomienda.codigo)}\n'
            f'Cliente remitente: {encomienda.cliente.nombre} {encomienda.cliente.apellido}\n'
            f'Destino: {encomienda.destino.ciudad} - {encomienda.destino.direccion}\n'
            f'Descripción: {encomienda.descripcion}\n'
            f'Estado actual: {encomienda.get_estado_display()}\n'
            f'Fecha estimada de entrega: {encomienda.fecha_estimada.strftime("%d/%m/%Y %H:%M")}\n\n'
            f'Puedes rastrear tu encomienda ingresando el código en nuestro sistema.\n\n'
            f'Saludos,\nEquipo LataExpress'
        )

        EmailMessage(
            subject='Detalle de su encomienda',
            body=mensaje_destinatario,
            to=[encomienda.destino.email_destinatario],
        ).send()

def enviar_encomienda_correo(request, id):
    try:
        encomienda = Encomienda.objects.select_related('cliente', 'destino').get(id=id)
    except Encomienda.DoesNotExist:
        messages.error(request, "Encomienda no encontrada")
        return redirect('/showencomiendas')

    enviar_correo_encomienda(encomienda)

    messages.success(request, f"Correo enviado a {encomienda.email_destinatario}")
    return redirect('/showencomiendas')
@requiere_admin
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
            # Busca por coincidencia parcial del UUID
            encomienda = Encomienda.objects.select_related('cliente', 'destino').get(
                codigo__istartswith=codigo_ingresado.replace('LE-', '').replace('LE', '')
            )
        except Encomienda.DoesNotExist:
            encomienda = None
        except Encomienda.MultipleObjectsReturned:
            # Si el código corto coincide con más de una encomienda,toma la primera coincidencia
            encomienda = Encomienda.objects.select_related('cliente', 'destino').filter(
                codigo__istartswith=codigo_ingresado.replace('LE-', '').replace('LE', '')
            ).first()

    return render(request, 'rastrear.html', {
        'encomienda': encomienda,
        'buscado': buscado
    })

#Edición de Cliente

@requiere_admin
def editcliente(request, id):
    #Capturar el cliente a editar
    cliente = Cliente.objects.get(id=id)
    return render(request, 'editCliente.html', {
        'cliente': cliente
    })

@requiere_admin
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
@requiere_admin
def editencomienda(request, id):
    #Capturar la encomienda a editar
    encomienda = Encomienda.objects.select_related('cliente', 'destino').get(id=id)
    clientes = Cliente.objects.all()

    return render(request, 'editEncomienda.html', {
        'encomienda': encomienda,
        'clientes': clientes
    })

@requiere_admin
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

    #Se actualiza
    enviar_correo_actualizacion(encomienda)

    messages.success(request, f'Encomienda actualizada correctamente para {cliente.nombre}')
    return redirect('/showencomiendas')


@requiere_admin_o_transportista
def actualizar_estados(request):
    encomiendas = Encomienda.objects.select_related('cliente', 'destino').all().order_by('-fecha_envio')

    if request.method == 'POST':
        encomienda_id = request.POST.get('encomienda')
        nuevo_estado = request.POST.get('estado')
        estados_validos = {valor for valor, _ in Encomienda.ESTADOS}

        if nuevo_estado not in estados_validos:
            messages.error(request, 'El estado seleccionado no es válido.')
        else:
            encomienda = Encomienda.objects.get(id=encomienda_id)
            encomienda.estado = nuevo_estado
            encomienda.save(update_fields=['estado'])
            messages.success(request, 'Estado de la encomienda actualizado correctamente.')
            return redirect('/actualizar_estados/')

    return render(request, 'actualizar_estados.html', {
        'encomiendas': encomiendas,
        'estados': Encomienda.ESTADOS,
    })

def enviar_correo_actualizacion(encomienda):

    # Correo para el cliente (remitente)
    if encomienda.cliente.email:
        asunto_cliente = f'Actualización de tu envío LE-{str(encomienda.codigo)}'
        mensaje_cliente = (
            f'Hola {encomienda.cliente.nombre} {encomienda.cliente.apellido},\n\n'
            f'Tu encomienda ha sido actualizada.\n\n'
            f'Código de rastreo: LE-{str(encomienda.codigo)}\n'
            f'Destinatario: {encomienda.destino.nombre_destinatario}\n'
            f'Destino: {encomienda.destino.ciudad} - {encomienda.destino.direccion}\n'
            f'Descripción: {encomienda.descripcion}\n'
            f'Estado actual: {encomienda.get_estado_display()}\n'
            f'Fecha estimada de entrega: {fecha_estimada.strftime("%d/%m/%Y %H:%M")}\n\n'
            f'Puedes rastrear tu encomienda ingresando el código en nuestro sistema.\n\n'
            f'Saludos,\nEquipo LataExpress'
        )

        send_mail(
            asunto_cliente,
            mensaje_cliente,
            settings.DEFAULT_FROM_EMAIL,
            [encomienda.cliente.email],
            fail_silently=False,
        )

    #Correo para el destinatario
    if encomienda.destino.email_destinatario:
        asunto_destinatario = f'Actualización de tu envío LE-{str(encomienda.codigo)}'
        mensaje_destinatario = (
            f'Hola {encomienda.destino.nombre_destinatario},\n\n'
            f'Se ha actualizado la encomienda de la cual eres destinatario en LataExpress.\n\n'
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
            asunto_destinatario,
            mensaje_destinatario,
            settings.DEFAULT_FROM_EMAIL,
            [encomienda.destino.email_destinatario],
            fail_silently=False,
        )

def about(request):
    return render(request, 'about.html')