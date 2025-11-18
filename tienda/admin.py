from django.contrib import admin
from .models import (
    Genero, 
    Autor, 
    Libro, 
    BibliotecaUsuario, 
    ContenidoLibro, 
    Pedido, 
    DetallePedido
)


#Géneros y Autores
admin.site.register(Genero)
admin.site.register(Autor)

# ver Libros
admin.site.register(Libro)

# ver qué usuarios tienen qué libros
admin.site.register(BibliotecaUsuario)

#contenido de cada libro
admin.site.register(ContenidoLibro)

# pedidos
admin.site.register(Pedido)
admin.site.register(DetallePedido)