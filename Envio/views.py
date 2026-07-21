from django.shortcuts import render, redirect
from .models import Cliente, Destino, Encomienda
## Para añadir los alert bonitos 
from django.contrib import messages

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


