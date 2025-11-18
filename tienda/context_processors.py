from .models import Genero

def menu_generos(request):
    
    return {'menu_generos': Genero.objects.all()}