from django.urls import path
from . import views

urlpatterns = [
    path('', views.vista_dashboard_home, name='dash_home'),
    path('pedidos/', views.vista_ver_pedidos, name='dash_ver_pedidos'),
    path('pedidos/editar/<int:id_pedido>/', views.vista_editar_pedido, name='dash_editar_pedido'),
    
    path('libros/', views.vista_ver_libros, name='dash_ver_libros'),
    path('libros/agregar/', views.vista_agregar_libro, name='dash_agregar_libro'),
    path('libros/editar/<int:id_libro>/', views.vista_editar_libro, name='dash_editar_libro'),

    path('libros/borrar/<int:id_libro>/', views.vista_borrar_libro, name='dash_borrar_libro'),
    path('libros/editar/<int:id_libro>/borrar_contenido/<int:id_contenido>/', views.vista_borrar_contenido, name='dash_borrar_contenido'),
    path('contenido/', views.vista_ver_contenido, name='dash_ver_contenido'),

    path('usuarios/', views.vista_ver_usuarios, name='dash_ver_usuarios'),
    path('usuarios/agregar/', views.vista_agregar_usuario, name='dash_agregar_usuario'),
    path('usuarios/editar/<int:id_usuario>/', views.vista_editar_usuario, name='dash_editar_usuario'),
    path('usuarios/borrar/<int:id_usuario>/', views.vista_borrar_usuario, name='dash_borrar_usuario'),

    path('generos/', views.vista_ver_generos, name='dash_ver_generos'),
    path('generos/agregar/', views.vista_agregar_genero, name='dash_agregar_genero'),
    path('generos/editar/<int:id_genero>/', views.vista_editar_genero, name='dash_editar_genero'),
    path('generos/borrar/<int:id_genero>/', views.vista_borrar_genero, name='dash_borrar_genero'),

    path('autores/', views.vista_ver_autores, name='dash_ver_autores'),
    path('autores/agregar/', views.vista_agregar_autor, name='dash_agregar_autor'),
    path('autores/editar/<int:id_autor>/', views.vista_editar_autor, name='dash_editar_autor'),
    path('autores/borrar/<int:id_autor>/', views.vista_borrar_autor, name='dash_borrar_autor'),
    path('relaciones/generos/', views.vista_ver_rel_generos, name='dash_ver_rel_generos'),
    path('relaciones/autores/', views.vista_ver_rel_autores, name='dash_ver_rel_autores'),
    path('relaciones/generos/borrar/<int:id_relacion>/', views.vista_borrar_rel_genero, name='dash_borrar_rel_genero'),
    path('relaciones/autores/borrar/<int:id_relacion>/', views.vista_borrar_rel_autor, name='dash_borrar_rel_autor'),
]