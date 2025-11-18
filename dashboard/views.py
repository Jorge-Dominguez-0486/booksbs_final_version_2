from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.db.models import Q
from decimal import Decimal, InvalidOperation
import re 


from tienda.models import Pedido, Libro, Genero, Autor, ContenidoLibro


from .forms import (
    LibroForm, UserForm, GeneroForm, AutorForm, 
    NuevoUsuarioForm, PedidoStatusForm, ContenidoLibroForm,
    ContenidoBulkForm, AdminPasswordChangeForm
)


def es_admin(user):
    return user.is_staff or user.is_superuser






from django.db.models import Count
import json

@login_required
@user_passes_test(es_admin)
def vista_dashboard_home(request):
    
    num_pedidos = Pedido.objects.count()
    num_libros = Libro.objects.count()
    num_usuarios = User.objects.count()

   
    datos_generos = Genero.objects.annotate(total=Count('libros')).values('nombre_genero', 'total')
    
    
    labels_generos = [item['nombre_genero'] for item in datos_generos]
    data_generos = [item['total'] for item in datos_generos]

   
    datos_pedidos = Pedido.objects.values('estado_pago').annotate(total=Count('id'))
    
    labels_pedidos = [item['estado_pago'] for item in datos_pedidos]
    data_pedidos = [item['total'] for item in datos_pedidos]

    contexto = {
        'num_pedidos': num_pedidos,
        'num_libros': num_libros,
        'num_usuarios': num_usuarios,
        
        
        'labels_generos_json': json.dumps(labels_generos),
        'data_generos_json': json.dumps(data_generos),
        'labels_pedidos_json': json.dumps(labels_pedidos),
        'data_pedidos_json': json.dumps(data_pedidos),
    }
    return render(request, 'dashboard/home.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_ver_pedidos(request):
    
    query = request.GET.get('q')
    pedidos = Pedido.objects.all()
    
    if query:
        search_filter = Q()
        is_numeric_search = False
        
        try:
            query_int = int(query)
            search_filter |= Q(id=query_int)
            is_numeric_search = True
        except ValueError:
            pass
            
        try:
            query_dec = Decimal(query)
            search_filter |= Q(total_pagado=query_dec)
            is_numeric_search = True
        except InvalidOperation:
            pass
        
        
        if not is_numeric_search:
            search_filter = (
                Q(usuario__email__icontains=query) |
                Q(usuario__first_name__icontains=query) |
                Q(estado_pago__icontains=query) |
                Q(fecha_pedido__icontains=query) 
            )
            
        pedidos = pedidos.filter(search_filter).order_by('-fecha_pedido').distinct()
    else:
        pedidos = pedidos.order_by('-fecha_pedido')
        
    contexto = {
        'pedidos': pedidos,
        'search_query': query
    }
    return render(request, 'dashboard/ver_pedidos.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_editar_pedido(request, id_pedido):
    
    pedido = get_object_or_404(Pedido, id=id_pedido)

    if request.method == 'POST':
        form = PedidoStatusForm(request.POST, instance=pedido)
        if form.is_valid():
            form.save()
            messages.success(request, f'El estado del Pedido #{pedido.id} ha sido actualizado.')
            return redirect('dash_ver_pedidos')
    else:
        form = PedidoStatusForm(instance=pedido)

    contexto = {
        'form': form,
        'titulo_pagina': f'Editar Estado (Pedido #{pedido.id} - {pedido.usuario.email})'
    }
    
    return render(request, 'dashboard/form_generico.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_ver_libros(request):
    
    query = request.GET.get('q')
    libros = Libro.objects.all()
    
    if query:
        search_filter = Q()
        is_numeric_search = False

        try:
            query_int = int(query)
            search_filter |= Q(id=query_int)
            is_numeric_search = True
        except ValueError:
            pass 

        try:
            query_dec = Decimal(query)
            search_filter |= Q(precio=query_dec)
            is_numeric_search = True
        except InvalidOperation:
            pass 
        
        
        if not is_numeric_search:
            search_filter = (
                Q(titulo__icontains=query) |
                Q(descripcion__icontains=query) |
                Q(estado_publicacion__icontains=query) |
                Q(formato__icontains=query) |
                Q(autores__nombre_autor__icontains=query) |
                Q(generos__nombre_genero__icontains=query)
            )
            
        libros = libros.filter(search_filter).order_by('id').distinct()
    else:
        libros = libros.order_by('id')
        
    contexto = {
        'libros': libros,
        'search_query': query
    }
    return render(request, 'dashboard/ver_libros.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_agregar_libro(request):
    
    if request.method == 'POST':
        form = LibroForm(request.POST, request.FILES)
        if form.is_valid():
            nuevo_libro = form.save() 
            messages.success(request, f'¡Libro "{nuevo_libro.titulo}" creado! Ahora puedes subir su contenido.')
            return redirect('dash_editar_libro', id_libro=nuevo_libro.id)
        else:
            messages.error(request, 'Hubo un error. Revisa el formulario.')
    else:
        form = LibroForm()
    
    contexto = {
        'form': form,
        'titulo_pagina': 'Agregar Nuevo Libro'
    }
    return render(request, 'dashboard/form_generico.html', contexto)


@login_required
@user_passes_test(es_admin)
def vista_editar_libro(request, id_libro):
    libro = get_object_or_404(Libro, id=id_libro)
    contenido_actual = ContenidoLibro.objects.filter(libro=libro).order_by('orden')

    form_libro = LibroForm(instance=libro)
    form_contenido_individual = ContenidoLibroForm()
    form_contenido_bulk = ContenidoBulkForm()

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'form_libro':
            form_libro = LibroForm(request.POST, request.FILES, instance=libro)
            if form_libro.is_valid():
                form_libro.save()
                messages.success(request, '¡Información del libro actualizada!')
            else:
                messages.error(request, 'Error al actualizar el libro.')
            return redirect('dash_editar_libro', id_libro=id_libro)

        elif form_type == 'form_contenido_individual':
            form_contenido_individual = ContenidoLibroForm(request.POST, request.FILES)
            if form_contenido_individual.is_valid():
                nuevo_contenido = form_contenido_individual.save(commit=False)
                nuevo_contenido.libro = libro 
                nuevo_contenido.save()
                messages.success(request, '¡Contenido individual agregado!')
            else:
                messages.error(request, 'Error al subir el archivo individual.')
            return redirect('dash_editar_libro', id_libro=id_libro)
        
        elif form_type == 'form_contenido_bulk':
            form_bulk = ContenidoBulkForm(request.POST, request.FILES)
            if form_bulk.is_valid():
                archivos_subidos = request.FILES.getlist('archivos')
                
                
                
                def get_numero_de_archivo(archivo):
                    
                    numeros = re.findall(r'\d+', archivo.name)
                    if numeros:
                        
                        return int(numeros[-1])
                    return 0 

                
                archivos_subidos.sort(key=get_numero_de_archivo) 
                
                
                ultimo_orden_obj = contenido_actual.last()
                orden_actual = (ultimo_orden_obj.orden + 1) if ultimo_orden_obj else 1
                
                for f in archivos_subidos:
                    ContenidoLibro.objects.create(
                        libro=libro, 
                        tipo_contenido='imagen',
                        archivo=f, 
                        orden=orden_actual
                    )
                    orden_actual += 1
                    
                messages.success(request, f'¡Se subieron {len(archivos_subidos)} páginas de golpe!')
            else:
                messages.error(request, 'Error al subir los archivos.')
            return redirect('dash_editar_libro', id_libro=id_libro)
    
    contexto = {
        'form_libro': form_libro,
        'form_contenido_individual': form_contenido_individual,
        'form_contenido_bulk': form_contenido_bulk,
        'contenido_actual': contenido_actual,
        'titulo_pagina': f'Editando Libro: {libro.titulo}',
        'libro': libro 
    }
    return render(request, 'dashboard/form_editar_libro.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_borrar_libro(request, id_libro):
    
    libro = get_object_or_404(Libro, id=id_libro)
    if request.method == 'POST':
        libro.delete()
        messages.success(request, f"El libro '{libro.titulo}' ha sido eliminado.")
        return redirect('dash_ver_libros')
    
    contexto = {
        'objeto': libro,
        'titulo_pagina': 'Borrar Libro',
        'url_cancelar': 'dash_ver_libros'
    }
    return render(request, 'dashboard/borrar_generico.html', contexto)


@login_required
@user_passes_test(es_admin)
def vista_borrar_contenido(request, id_libro, id_contenido):
    contenido = get_object_or_404(ContenidoLibro, id=id_contenido)
    if contenido.libro.id != id_libro:
        messages.error(request, 'Error: El contenido no pertenece a este libro.')
        return redirect('dash_editar_libro', id_libro=id_libro)
    
    contenido.delete()
    messages.success(request, f"El archivo de contenido '{contenido.archivo.name}' ha sido eliminado.")
    return redirect('dash_editar_libro', id_libro=id_libro)
    

@login_required
@user_passes_test(es_admin)
def vista_ver_contenido(request):
    query = request.GET.get('q')
    contenido_lista = ContenidoLibro.objects.select_related('libro').order_by('-id')

    if query:
        search_filter = (
            Q(id__icontains=query) |
            Q(libro__titulo__icontains=query) |
            Q(tipo_contenido__icontains=query)
        )
        contenido_lista = contenido_lista.filter(search_filter).distinct()
        
    contexto = {
        'contenido_lista': contenido_lista,
        'search_query': query
    }
    return render(request, 'dashboard/ver_contenido.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_ver_rel_generos(request):
    relaciones = Libro.generos.through.objects.select_related('libro', 'genero').all().order_by('-id')
    contexto = {
        'relaciones': relaciones,
    }
    return render(request, 'dashboard/ver_relacion_generos.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_borrar_rel_genero(request, id_relacion):
    relacion = get_object_or_404(Libro.generos.through, id=id_relacion)
    relacion.delete()
    messages.success(request, 'Relación Género-Libro eliminada exitosamente.')
    return redirect('dash_ver_rel_generos')

@login_required
@user_passes_test(es_admin)
def vista_ver_rel_autores(request):
    relaciones = Libro.autores.through.objects.select_related('libro', 'autor').all().order_by('-id')
    contexto = {
        'relaciones': relaciones,
    }
    return render(request, 'dashboard/ver_relacion_autores.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_borrar_rel_autor(request, id_relacion):
    relacion = get_object_or_404(Libro.autores.through, id=id_relacion)
    relacion.delete()
    messages.success(request, 'Relación Autor-Libro eliminada exitosamente.')
    return redirect('dash_ver_rel_autores')


@login_required
@user_passes_test(es_admin)
def vista_ver_usuarios(request):
    
    query = request.GET.get('q')
    usuarios = User.objects.all()
    
    if query:
        search_filter = Q()
        is_numeric_search = False

        try:
            query_int = int(query)
            search_filter |= Q(id=query_int)
            is_numeric_search = True
        except ValueError:
            pass
        
       
        if not is_numeric_search:
            search_filter = (
                Q(email__icontains=query) | 
                Q(first_name__icontains=query) | 
                Q(username__icontains=query)
            )
            
        usuarios = usuarios.filter(search_filter).order_by('id').distinct()
    else:
        usuarios = usuarios.order_by('id')
        
    contexto = {
        'usuarios': usuarios,
        'search_query': query
    }
    return render(request, 'dashboard/ver_usuarios.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_editar_usuario(request, id_usuario):
    
    usuario = get_object_or_404(User, id=id_usuario)

    form_info = UserForm(instance=usuario)
    form_pass = AdminPasswordChangeForm(user=usuario)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'form_info':
            form_info = UserForm(request.POST, instance=usuario)
            if form_info.is_valid():
                form_info.save()
                messages.success(request, '¡Información del usuario actualizada!')
                return redirect('dash_editar_usuario', id_usuario=id_usuario)

        elif form_type == 'form_pass':
            form_pass = AdminPasswordChangeForm(user=usuario, data=request.POST)
            if form_pass.is_valid():
                form_pass.save()
                messages.success(f'¡Contraseña del usuario {usuario.email} actualizada!')
                return redirect('dash_editar_usuario', id_usuario=id_usuario)
    
    contexto = {
        'form_info': form_info,
        'form_pass': form_pass,
        'titulo_pagina': f'Editar Usuario: {usuario.username}'
    }
    return render(request, 'dashboard/form_editar_usuario.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_borrar_usuario(request, id_usuario):
    
    usuario = get_object_or_404(User, id=id_usuario)
    if usuario.is_superuser:
        messages.error(request, 'No puedes eliminar a un Superusuario.')
        return redirect('dash_ver_usuarios')
        
    if request.method == 'POST':
        usuario.delete()
        messages.success(request, f"El usuario '{usuario.username}' ha sido eliminado.")
        return redirect('dash_ver_usuarios')
    
    contexto = {
        'objeto': usuario,
        'titulo_pagina': 'Borrar Usuario',
        'url_cancelar': 'dash_ver_usuarios'
    }
    return render(request, 'dashboard/borrar_generico.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_agregar_usuario(request):
    
    if request.method == 'POST':
        form = NuevoUsuarioForm(request.POST)
        if form.is_valid():
            
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            nombre = form.cleaned_data['first_name']
            rol = form.cleaned_data['rol']
            
           
            if User.objects.filter(username=email).exists():
                messages.error(request, 'Ese correo ya está registrado.')
            else:
                
                usuario = User.objects.create_user(username=email, email=email, password=password)
                usuario.first_name = nombre
                
                
                if rol == 'admin':
                    usuario.is_staff = True
                    usuario.is_superuser = True
                elif rol == 'staff':
                    usuario.is_staff = True
                    usuario.is_superuser = False
                else: 
                    usuario.is_staff = False
                    usuario.is_superuser = False
                
                usuario.save()
                messages.success(request, f'Usuario {email} creado exitosamente como {rol}.')
                return redirect('dash_ver_usuarios')
    else:
        form = NuevoUsuarioForm()
    
    contexto = {
        'form': form,
        'titulo_pagina': 'Agregar Nuevo Usuario'
    }
    
    return render(request, 'dashboard/form_generico.html', contexto)


@login_required
@user_passes_test(es_admin)
def vista_ver_generos(request):
    
    query = request.GET.get('q')
    generos = Genero.objects.all()
    
    if query:
        search_filter = Q()
        is_numeric_search = False

        try:
            query_int = int(query)
            search_filter |= Q(id=query_int)
            is_numeric_search = True
        except ValueError:
            pass
            
        
        if not is_numeric_search:
            search_filter = (
                Q(nombre_genero__icontains=query) |
                Q(descripcion_genero__icontains=query)
            )
        
        generos = generos.filter(search_filter).order_by('nombre_genero').distinct()
    else:
        generos = generos.order_by('nombre_genero')
        
    contexto = {
        'generos': generos,
        'search_query': query
    }
    return render(request, 'dashboard/ver_generos.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_agregar_genero(request):
    
    if request.method == 'POST':
        form = GeneroForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Género agregado exitosamente!')
            return redirect('dash_ver_generos')
    else:
        form = GeneroForm()
    
    contexto = {
        'form': form,
        'titulo_pagina': 'Agregar Nuevo Género'
    }
    return render(request, 'dashboard/form_generico.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_editar_genero(request, id_genero):
    
    genero = get_object_or_404(Genero, id=id_genero)
    if request.method == 'POST':
        form = GeneroForm(request.POST, instance=genero)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Género actualizado exitosamente!')
            return redirect('dash_ver_generos')
    else:
        form = GeneroForm(instance=genero)
    
    contexto = {
        'form': form,
        'titulo_pagina': f'Editar Género: {genero.nombre_genero}'
    }
    return render(request, 'dashboard/form_generico.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_borrar_genero(request, id_genero):
    
    genero = get_object_or_404(Genero, id=id_genero)
    if request.method == 'POST':
        genero.delete()
        messages.success(request, f"El género '{genero.nombre_genero}' ha sido eliminado.")
        return redirect('dash_ver_generos')
    
    contexto = {
        'objeto': genero,
        'titulo_pagina': 'Borrar Género',
        'url_cancelar': 'dash_ver_generos'
    }
    return render(request, 'dashboard/borrar_generico.html', contexto)


@login_required
@user_passes_test(es_admin)
def vista_ver_autores(request):
    
    query = request.GET.get('q')
    autores = Autor.objects.all()
    
    if query:
        search_filter = Q()
        is_numeric_search = False

        try:
            query_int = int(query)
            search_filter |= Q(id=query_int)
            is_numeric_search = True
        except ValueError:
            pass
        
        
        if not is_numeric_search:
            search_filter = (
                Q(nombre_autor__icontains=query) |
                Q(biografia__icontains=query)
            )
        
        autores = autores.filter(search_filter).order_by('nombre_autor').distinct()
    else:
        autores = autores.order_by('nombre_autor')

    contexto = {
        'autores': autores,
        'search_query': query
    }
    return render(request, 'dashboard/ver_autores.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_agregar_autor(request):
    
    if request.method == 'POST':
        form = AutorForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Autor agregado exitosamente!')
            return redirect('dash_ver_autores')
    else:
        form = AutorForm()
    
    contexto = {
        'form': form,
        'titulo_pagina': 'Agregar Nuevo Autor'
    }
    return render(request, 'dashboard/form_generico.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_editar_autor(request, id_autor):
    # ... (El resto de la función sigue igual) ...
    autor = get_object_or_404(Autor, id=id_autor)
    if request.method == 'POST':
        form = AutorForm(request.POST, request.FILES, instance=autor)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Autor actualizado exitosamente!')
            return redirect('dash_ver_autores')
    else:
        form = AutorForm(instance=autor)
    
    contexto = {
        'form': form,
        'titulo_pagina': f'Editar Autor: {autor.nombre_autor}'
    }
    return render(request, 'dashboard/form_generico.html', contexto)

@login_required
@user_passes_test(es_admin)
def vista_borrar_autor(request, id_autor):
    # ... (El resto de la función sigue igual) ...
    autor = get_object_or_404(Autor, id=id_autor)
    if request.method == 'POST':
        autor.delete()
        messages.success(request, f"El autor '{autor.nombre_autor}' ha sido eliminado.")
        return redirect('dash_ver_autores')
    
    contexto = {
        'objeto': autor,
        'titulo_pagina': 'Borrar Autor',
        'url_cancelar': 'dash_ver_autores'
    }
    return render(request, 'dashboard/borrar_generico.html', contexto)