import os
import django
from django.conf import settings
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'booksbs.settings')
django.setup()

from tienda.models import Libro, ContenidoLibro

def cargar_paginas(id_libro, carpeta_con_imagenes):
    print(f"Buscando libro con ID: {id_libro}...")
    try:
        libro = Libro.objects.get(id=id_libro)
        print(f"Libro encontrado: '{libro.titulo}'")
    except Libro.DoesNotExist:
        print(f"¡ERROR! No se encontró ningún libro con ID {id_libro}.")
        print("Verifica el ID en el panel de Admin.")
        return

    if not os.path.exists(carpeta_con_imagenes):
        print(f"¡ERROR! No se pudo encontrar la carpeta de imágenes en:")
        print(f"{carpeta_con_imagenes}")
        return

    print(f"Leyendo imágenes desde: {carpeta_con_imagenes}...")
    
    try:
        paginas_png = [f for f in os.listdir(carpeta_con_imagenes) if f.endswith('.png')]
        paginas_ordenadas = sorted(paginas_png, key=lambda x: int(x.split('_')[-1].split('.')[0]))
        print(f"Se encontraron {len(paginas_ordenadas)} imágenes .png para procesar.")
    except Exception as e:
        print(f"¡ERROR! Hubo un problema al leer/ordenar los archivos en la carpeta.")
        print("Asegúrate que los archivos se llamen 'pagina_1.png', 'pagina_2.png', etc.")
        print(f"Error técnico: {e}")
        return

    ContenidoLibro.objects.filter(libro=libro).delete()
    print("Se eliminaron las páginas antiguas (si existían).")

    print(f"Iniciando carga de {len(paginas_ordenadas)} páginas. Esto puede tardar...")
    
    for i, nombre_archivo in enumerate(paginas_ordenadas, start=1):
        ruta_completa_archivo = os.path.join(carpeta_con_imagenes, nombre_archivo)
        
        with open(ruta_completa_archivo, 'rb') as f:
            
            # --- ¡ESTA ES LA LÍNEA CORREGIDA! ---
            contenido = ContenidoLibro(libro=libro, orden=i, tipo_contenido='imagen')
            
            contenido.archivo.save(nombre_archivo, File(f), save=False)
            contenido.save()
            
            if i % 20 == 0:
                print(f"  ... {i} páginas cargadas...")

    print(f"✅ ¡Proceso completado! Se subieron {len(paginas_ordenadas)} páginas correctamente.")

if __name__ == "__main__":
    print("Este script no está hecho para ejecutarse directamente.")
    print("Debes ejecutarlo usando 'python manage.py shell'")
    print("Y luego usar: from cargar_paginas import cargar_paginas")