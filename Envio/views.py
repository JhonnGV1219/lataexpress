from django.shortcuts import render, redirect
from .models import Cliente, Destino, Encomienda
## Para añadir los alert bonitos 
from django.contrib import messages
from django.core.mail import EmailMessage

# Create your views here.

# Create your models here.
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

##Para ver detalle de la encomienda mas bonito
def detalle_encomienda(request, id):
    encomienda = Encomienda.objects.select_related('cliente', 'destino').get(id=id)

    return render(request, 'detalle_encomienda.html', {
        'encomienda': encomienda
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

    # -------- DESTINO --------
    ciudad_f = request.POST.get('ciudad')
    direccion_f = request.POST.get('direccion')
    codigo_postal_f = request.POST.get('codigo_postal')

    destino_f = Destino.objects.create(
        ciudad=ciudad_f,
        direccion=direccion_f,
        codigo_postal=codigo_postal_f
    )

    # -------- DESTINATARIO --------
    nombre_destinatario_f = request.POST.get('nombre_destinatario')
    cedula_destinatario_f = request.POST.get('cedula_destinatario')
    email_destinatario_f = request.POST.get('email_destinatario')
    telefono_destinatario_f = request.POST.get('telefono_destinatario')
    direccion_destino_f = request.POST.get('direccion_destino')

    # -------- ENCOMIENDA --------
    descripcion_f = request.POST.get('descripcion')
    peso_f = request.POST.get('peso')
    precio_f = request.POST.get('precio')
    estado_f = request.POST.get('estado')
    transporte_f = request.POST.get('transporte')
    fecha_estimada_f = request.POST.get('fecha_estimada')

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


def enviar_correo_encomienda(encomienda):
    mensaje = f"""
    📦 DETALLE DE SU ENCOMIENDA

    Código: {str(encomienda.codigo)}
    Estado: {encomienda.get_estado_display()}

    👤 Remitente:
    {encomienda.cliente.nombre} {encomienda.cliente.apellido}

    👤 Destinatario:
    {encomienda.nombre_destinatario}
    Teléfono: {encomienda.telefono_destinatario}
    Correo: {encomienda.email_destinatario}

    📍 Destino:
    {encomienda.destino.ciudad}
    {encomienda.destino.direccion}

    🚚 Transporte:
    {encomienda.get_transporte_display()}

    📦 Descripción:
    {encomienda.descripcion}

    ⚖ Peso: {encomienda.peso} kg
    💰 Precio: ${encomienda.precio}

    📅 Fecha envío: {encomienda.fecha_envio}
    📅 Fecha estimada: {encomienda.fecha_estimada}
    """

    email = EmailMessage(
        subject='Detalle de su encomienda',
        body=mensaje,
        to=[encomienda.email_destinatario],
    )

    email.send()

def enviar_encomienda_correo(request, id):
    try:
        encomienda = Encomienda.objects.select_related('cliente', 'destino').get(id=id)
    except Encomienda.DoesNotExist:
        messages.error(request, "Encomienda no encontrada")
        return redirect('/showencomiendas')

    enviar_correo_encomienda(encomienda)

    messages.success(request, f"Correo enviado a {encomienda.email_destinatario}")
    return redirect('/showencomiendas')