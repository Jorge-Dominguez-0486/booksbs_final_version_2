

from django.db import models
from django.contrib.auth.models import User  




class Genero(models.Model):
    nombre_genero = models.CharField(max_length=100, unique=True)
    descripcion_genero = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_genero


class Autor(models.Model):
    nombre_autor = models.CharField(max_length=150, unique=True)
    biografia = models.TextField(blank=True, null=True)
    
    # Campo de imagen
    foto = models.ImageField(upload_to='autores/', blank=True, null=True)

    def __str__(self):
        return self.nombre_autor


class Libro(models.Model):
    ESTADO_CHOICES = [
        ('disponible', 'Disponible'),
        ('proximamente', 'Próximamente'),
    ]
    FORMATO_CHOICES = [
        ('ebook', 'Ebook'),
        ('audiobook', 'Audiobook'),
    ]

    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    portada = models.ImageField(upload_to='portadas/')

    estado_publicacion = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='disponible')
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default='ebook')
    fecha_lanzamiento = models.DateField(blank=True, null=True)
    duracion_minutos = models.IntegerField(blank=True, null=True)

    autores = models.ManyToManyField(Autor, related_name="libros")
    generos = models.ManyToManyField(Genero, related_name="libros")

    def __str__(self):
        return self.titulo




class PaginaLibro(models.Model):
    libro = models.ForeignKey("Libro", on_delete=models.CASCADE, related_name="paginas")
    imagen = models.ImageField(upload_to="paginas_libro/")
    numero = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.libro.titulo} - Página {self.numero}"

    class Meta:
        ordering = ['numero']





class BibliotecaUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    fecha_adquisicion = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('usuario', 'libro')

    def __str__(self):
        return f"{self.usuario.username} posee {self.libro.titulo}"


class ContenidoLibro(models.Model):
    TIPO_CHOICES = [
        ('imagen', 'Página (Imagen)'),
        ('audio', 'Audio (MP3)'),
    ]

    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, related_name="contenido")
    tipo_contenido = models.CharField(max_length=10, choices=TIPO_CHOICES)
    archivo = models.FileField(upload_to='contenido/')
    orden = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['orden']

    def __str__(self):
        return f"{self.libro.titulo} - {self.tipo_contenido} {self.orden}"




class Pedido(models.Model):
    ESTADO_PAGO_CHOICES = [
        ('completado', 'Completado'),
        ('pendiente', 'Pendiente'),
        ('fallido', 'Fallido'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total_pagado = models.DecimalField(max_digits=10, decimal_places=2)
    estado_pago = models.CharField(max_length=15, choices=ESTADO_PAGO_CHOICES, default='pendiente')

    def __str__(self):
        return f"Pedido {self.id} - {self.usuario.username}"


class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="detalles")
    libro = models.ForeignKey(Libro, on_delete=models.SET_NULL, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.libro.titulo} en Pedido {self.pedido.id}"
