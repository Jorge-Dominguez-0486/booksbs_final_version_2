from django.shortcuts import render, get_object_or_404, redirect
from .models import Libro, Genero, Autor, BibliotecaUsuario, ContenidoLibro, Pedido, DetallePedido
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.db import transaction
from .carrito import Carrito
from django.http import FileResponse, Http404
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
from django.db.models import Q  # 



def pagina_index(request):
    libros_nuevos = Libro.objects.filter(estado_publicacion='disponible').order_by('-id')[:4]
    contexto = {
        'libros': libros_nuevos,
    }
    return render(request, 'index.html', contexto)

def pagina_proximos(request):
    ebooks_proximos = Libro.objects.filter(estado_publicacion='proximamente', formato='ebook').order_by('fecha_lanzamiento')
    audiobooks_proximos = Libro.objects.filter(estado_publicacion='proximamente', formato='audiobook').order_by('fecha_lanzamiento')
    contexto = {
        'ebooks': ebooks_proximos,
        'audiobooks': audiobooks_proximos,
    }
    return render(request, 'proximos.html', contexto)

def pagina_bookstore(request):
    # Obtenemos los parámetros de la URL
    genero_id = request.GET.get('genero_id')
    search_query = request.GET.get('q')  # <--- Capturamos la búsqueda
    
    # Empezamos con todos los libros disponibles
    libros_disponibles = Libro.objects.filter(estado_publicacion='disponible').order_by('-id')

    # 1. Filtro por Género (si existe)
    if genero_id:
        try:
            genero_id = int(genero_id)
            libros_disponibles = libros_disponibles.filter(generos__id=genero_id)
        except ValueError:
            genero_id = None

    # 2. Filtro por Búsqueda (si existe)
    if search_query:
        # Buscamos por Título O por Nombre de Autor
        libros_disponibles = libros_disponibles.filter(
            Q(titulo__icontains=search_query) | 
            Q(autores__nombre_autor__icontains=search_query)
        )

    generos = Genero.objects.all()
    libros_adquiridos_ids = []
    
    if request.user.is_authenticated:
        libros_adquiridos_ids = BibliotecaUsuario.objects.filter(usuario=request.user).values_list('libro__id', flat=True)
        
    contexto = {
        'libros': libros_disponibles,
        'generos': generos,
        'libros_adquiridos_ids': libros_adquiridos_ids,
        'genero_id_activo': genero_id,
        'search_query': search_query # <--- Lo pasamos al template para que no se borre de la cajita
    }
    return render(request, 'bookstore.html', contexto)

def pagina_proximo_detalle(request, id_libro):
    libro = get_object_or_404(Libro, id=id_libro, estado_publicacion='proximamente')
    contexto = {
        'libro': libro,
    }
    return render(request, 'proximo-detalle.html', contexto)

def pagina_libro_detalle(request, id_libro):
    libro = get_object_or_404(Libro, id=id_libro, estado_publicacion='disponible')
    
    ya_adquirido = False
    if request.user.is_authenticated:
        if BibliotecaUsuario.objects.filter(usuario=request.user, libro=libro).exists():
            ya_adquirido = True
            
    contexto = {
        'libro': libro,
        'ya_adquirido': ya_adquirido,
    }
    return render(request, 'libro_detalle.html', contexto)




def pagina_login(request):
    
    if request.user.is_authenticated:
        messages.info(request, "Ya has iniciado sesión.")
        if request.user.is_staff:
             return redirect('dash_home') 
        return redirect('mis_libros')            
    
  
    if request.method == 'POST':
        email = request.POST.get('email')
        contrasena = request.POST.get('password')
        usuario = authenticate(request, username=email, password=contrasena)
        
        if usuario is not None:
            login(request, usuario)
            
            if usuario.is_staff:
                return redirect('dash_home') 
            else:
                return redirect('mis_libros')       
            
        else:
            messages.error(request, 'Correo o contraseña incorrectos.')
            return render(request, 'login.html')
            
    return render(request, 'login.html')

def pagina_registro(request):
    if request.user.is_authenticated:
        messages.info(request, "Ya tienes una cuenta y has iniciado sesión.")
        return redirect('mis_libros')
    
    if request.method == 'POST':
        nombre_completo = request.POST.get('nombre_completo')
        email = request.POST.get('email')
        contrasena = request.POST.get('password')
        confirm_contrasena = request.POST.get('confirm_password')
        if contrasena != confirm_contrasena:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'registro.html')
        if User.objects.filter(username=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return render(request, 'registro.html')
        usuario = User.objects.create_user(username=email, email=email, password=contrasena)
        usuario.first_name = nombre_completo 
        usuario.save()
        login(request, usuario)
        return redirect('index')
    return render(request, 'registro.html')


def pagina_logout(request):
    logout(request)
    return redirect('login') 


@login_required
def pagina_cuenta(request):
    conteo_libros = BibliotecaUsuario.objects.filter(usuario=request.user).count()
    
  
    mis_pedidos = Pedido.objects.filter(usuario=request.user).order_by('-fecha_pedido')
    
    contexto = {
        'conteo_libros': conteo_libros,
        'pedidos': mis_pedidos,
    }
    return render(request, 'cuenta.html', contexto)

@login_required
def pagina_mis_libros(request):
    biblioteca = BibliotecaUsuario.objects.filter(usuario=request.user)
    ids_libros_usuario = biblioteca.values_list('libro__id', flat=True)
    ebooks = Libro.objects.filter(id__in=ids_libros_usuario, formato='ebook')
    audiobooks = Libro.objects.filter(id__in=ids_libros_usuario, formato='audiobook')
    contexto = {
        'ebooks': ebooks,
        'audiobooks': audiobooks,
    }
    return render(request, 'mis-libros.html', contexto)

@login_required
def pagina_leer_libro(request, id_libro, pagina):
    libro = get_object_or_404(Libro, id=id_libro)
    
    contexto = {
        'libro': libro,
        'pagina_actual': None,
        'pista_audio': None,
        'pagina_num': 1,
        'total_paginas': 0,
    }

    if libro.formato == 'ebook':
        contenido = ContenidoLibro.objects.filter(libro=libro, tipo_contenido='imagen').order_by('orden')
        total_paginas = contenido.count()

        try:
            pagina_num = int(pagina)
        except (ValueError, TypeError):
            pagina_num = 1

        if pagina_num < 1:
            pagina_num = 1
        elif pagina_num > total_paginas and total_paginas > 0:
            pagina_num = total_paginas
        elif total_paginas == 0:
            pagina_num = 1

        if total_paginas > 0:
            contexto['pagina_actual'] = contenido[pagina_num-1]
        
        contexto['pagina_num'] = pagina_num
        contexto['total_paginas'] = total_paginas

    elif libro.formato == 'audiobook':
        pista = ContenidoLibro.objects.filter(libro=libro, tipo_contenido='audio').first()
        contexto['pista_audio'] = pista
        
    return render(request, 'leer-libro.html', contexto)



@login_required
def pagina_confirmar_carrito(request):
    carrito_obj = Carrito(request)
    if not carrito_obj.carrito:
        return redirect('pagina_carrito')
    contexto = {
        "carrito": carrito_obj
    }
    return render(request, 'confirmar_carrito.html', contexto)

@login_required
@transaction.atomic
def procesar_carrito_compra(request):
    carrito_obj = Carrito(request)
    if not carrito_obj.carrito.items():
        messages.error(request, "Tu carrito está vacío. Agrega libros antes de comprar.")
        return redirect('pagina_carrito')

    usuario = request.user
    total_pagado = carrito_obj.obtener_total_con_iva()

    try:
        nuevo_pedido = Pedido.objects.create(usuario=usuario, total_pagado=total_pagado, estado_pago='completado')

        for key, item in carrito_obj.carrito.items():
            libro = get_object_or_404(Libro, id=item["producto_id"])
            if not BibliotecaUsuario.objects.filter(usuario=usuario, libro=libro).exists():
                BibliotecaUsuario.objects.create(usuario=usuario, libro=libro)
            DetallePedido.objects.create(pedido=nuevo_pedido, libro=libro, precio_compra=item["precio"])
        
        carrito_obj.limpiar()
        messages.success(request, f"¡Tu compra de ${total_pagado} fue exitosa! Los libros han sido añadidos a tu biblioteca.")
        return redirect('mis_libros')

    except Exception as e:
        messages.error(request, f'Hubo un error al procesar tu compra: {e}')
        return redirect('pagina_carrito')

def pagina_carrito(request):
    carrito_obj = Carrito(request) 
    contexto = {
        "carrito": carrito_obj
    }
    return render(request, 'carrito.html', contexto)

def agregar_carrito(request, id_libro):
    carrito = Carrito(request)
    libro = get_object_or_404(Libro, id=id_libro)
    carrito.agregar(libro)
    return redirect("pagina_carrito")

def eliminar_carrito(request, id_libro):
    carrito = Carrito(request)
    libro = get_object_or_404(Libro, id=id_libro)
    carrito.eliminar(libro)
    return redirect("pagina_carrito")

def limpiar_carrito(request):
    carrito = Carrito(request)
    carrito.limpiar()
    return redirect("pagina_carrito")




@login_required
def servir_audio(request, id_contenido):
    contenido = get_object_or_404(ContenidoLibro, id=id_contenido)
    
    if not contenido.archivo:
        raise Http404("El archivo de audio no existe.")

    
    
    ruta_archivo = contenido.archivo.path  
    response = FileResponse(open(ruta_archivo, 'rb')) 
    
    return response



def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html  = template.render(context_dict)
    result = BytesIO()
   
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

@login_required
def descargar_factura(request, id_pedido):
    
    pedido = get_object_or_404(Pedido, id=id_pedido, usuario=request.user)
    
    
    items = pedido.detalles.all()
    
    data = {
        'pedido': pedido,
        'items': items,
        'usuario': request.user,
    }
    
   
    return render_to_pdf('factura.html', data)