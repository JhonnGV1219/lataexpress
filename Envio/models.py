from django.db import models
##Libreria para generar codigos mediante los datos del cliente y destino 
import uuid

class Cliente(models.Model):
    nombre = models.CharField(max_length=100)
    apellido= models.CharField(max_length=100)
    cedula = models.CharField(max_length=10, unique=True)
    email = models.EmailField()
    telefono = models.CharField(max_length=10)

    def __str__(self):
        return self.nombre
    


class Destino(models.Model):
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)
    codigo_postal = models.CharField(max_length=6) 

    nombre_destinatario = models.CharField(max_length=100, null=True, blank=True)
    cedula_destinatario = models.CharField(max_length=10, null=True, blank=True)
    email_destinatario = models.EmailField(null=True, blank=True)
    telefono_destinatario = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.ciudad} - {self.direccion}"
    

class Encomienda(models.Model):
    ESTADOS = [
        ('OFICINA', 'En oficina'),
        ('TRANSPORTE', 'En transporte'),
        ('ENTREGADO', 'Entregado'),
    ]

    TRANSPORTE = [
        ('BUS', 'Bus'),
        ('CAMIONETA', 'Camioneta'),
        ('MOTO', 'Moto'),
    ]

    codigo = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE)

    descripcion = models.TextField()
    peso = models.FloatField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)

    estado = models.CharField(max_length=20, choices=ESTADOS, default='OFICINA')
    transporte = models.CharField(max_length=20, choices=TRANSPORTE)
    fecha_envio = models.DateTimeField(auto_now_add=True)
    fecha_estimada = models.DateTimeField()

    def __str__(self):
        return f"{self.codigo} - {self.estado}"

