from django.urls import path
from . import views  

urlpatterns = [
    # Principales y Catálogo
    path('', views.pagina_index, name='index'),
    path('proximos/', views.pagina_proximos, name='proximos'),
    path('bookstore/', views.pagina_bookstore, name='bookstore'),
    
    # URLs Detalle SEPARADAS
    path('proximo/<int:id_libro>/', views.pagina_proximo_detalle, name='proximo_detalle'),
    path('libro/<int:id_libro>/', views.pagina_libro_detalle, name='libro_detalle'),

    # Autenticación
    path('login/', views.pagina_login, name='login'),
    path('registro/', views.pagina_registro, name='registro'),
    path('logout/', views.pagina_logout, name='logout'),

    # Vistas usuario
    path('cuenta/', views.pagina_cuenta, name='cuenta'),
    path('mis-libros/', views.pagina_mis_libros, name='mis_libros'),
    
   
    path('leer/<int:id_libro>/<int:pagina>/', views.pagina_leer_libro, name='leer_libro'),

   

    # URLs del Carrito (NUEVAS)
    path('carrito/', views.pagina_carrito, name='pagina_carrito'),
    path('carrito/agregar/<int:id_libro>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/eliminar/<int:id_libro>/', views.eliminar_carrito, name='eliminar_carrito'),
    
    path('carrito/limpiar/', views.limpiar_carrito, name='limpiar_carrito'),
    path('carrito/confirmar/', views.pagina_confirmar_carrito, name='confirmar_carrito'),
    path('carrito/procesar_compra/', views.procesar_carrito_compra, name='procesar_carrito_compra'),
    path('stream/audio/<int:id_contenido>/', views.servir_audio, name='servir_audio'),
    path('factura/<int:id_pedido>/', views.descargar_factura, name='descargar_factura'),
    
    # ... aquí siguen las de compra ...
    
]