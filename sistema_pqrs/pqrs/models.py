from django.db import models

# Create your models here.

class Cliente(models.Model):
    TIPO_ID = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        # Agrega más si lo deseas
    ]
    tipo_id = models.CharField(max_length=2, choices=TIPO_ID)
    numero_id = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=15)
    contraseña = models.CharField(max_length=128)  # Se almacenará en forma cifrada
    activo = models.BooleanField(default=True)  # Permite desactivarlo sin borrarlo


    def __str__(self):
        return f"{self.nombre} ({self.numero_id})"

class PQRS(models.Model):
    TIPO_PQRS = [
        ('P', 'Petición'),
        ('Q', 'Queja'),
        ('R', 'Reclamo'),
        ('S', 'Sugerencia'),
    ]

    ESTADO = [
        ('NUEVO', 'Nuevo'),
        ('PROCESO', 'En proceso'),
        ('RESUELTO', 'Resuelto'),
        ('RECHAZADO', 'Rechazado'),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=1, choices=TIPO_PQRS)
    comentarios = models.TextField()
    archivo = models.FileField(upload_to='pqrs/', blank=True, null=True)
    fecha_radicado = models.DateTimeField(auto_now_add=True)
    numero_radicado = models.CharField(max_length=15, unique=True)
    estado = models.CharField(max_length=10, choices=ESTADO, default='NUEVO')
    justificacion = models.TextField(blank=True, null=True)
    correo_enviado = models.BooleanField(default=False)


    def __str__(self):
        return f"{self.numero_radicado} - {self.get_tipo_display()}"
    
class Gestor(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    # Si luego deseas activar/desactivar gestores
    activo = models.BooleanField(default=True)


    def __str__(self):
        return self.username

class Administrador(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.username
    
class LogCambio(models.Model):
    pqrs = models.ForeignKey(PQRS, on_delete=models.CASCADE)
    gestor = models.ForeignKey(Gestor, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    campo_modificado = models.CharField(max_length=50)
    valor_anterior = models.TextField(null=True, blank=True)
    valor_nuevo = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Cambio en {self.pqrs.numero_radicado} - {self.campo_modificado}"


    