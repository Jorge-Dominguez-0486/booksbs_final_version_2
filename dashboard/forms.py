from django import forms
from django.contrib.auth.models import User
from tienda.models import Libro, Genero, Autor, Pedido, ContenidoLibro
from django.contrib.auth.forms import SetPasswordForm


class LibroForm(forms.ModelForm):
    
    generos = forms.ModelMultipleChoiceField(
        queryset=Genero.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    
    autores = forms.ModelMultipleChoiceField(
        queryset=Autor.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Libro
        fields = [
            'titulo', 
            'descripcion', 
            'precio', 
            'portada', 
            'estado_publicacion', 
            'formato',
            'fecha_lanzamiento',
            'duracion_minutos',
            'generos',
            'autores'
        ]
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'portada': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'estado_publicacion': forms.Select(attrs={'class': 'form-control'}),
            'formato': forms.Select(attrs={'class': 'form-control'}),
            'fecha_lanzamiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duracion_minutos': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class UserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'email', 'is_staff', 'is_superuser']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class GeneroForm(forms.ModelForm):
    class Meta:
        model = Genero
        fields = ['nombre_genero', 'descripcion_genero']
        widgets = {
            'nombre_genero': forms.TextInput(attrs={'class': 'form-control'}),
            'descripcion_genero': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class AutorForm(forms.ModelForm):
    class Meta:
        model = Autor
        fields = ['nombre_autor', 'biografia', 'foto']
        widgets = {
            'nombre_autor': forms.TextInput(attrs={'class': 'form-control'}),
            'biografia': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'foto': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

class NuevoUsuarioForm(forms.ModelForm):
    
    ROL_CHOICES = [
        ('cliente', 'Cliente (Usuario normal)'),
        ('staff', 'Bibliotecario / Staff (Acceso al panel)'),
        ('admin', 'Administrador Total (Superusuario)'),
    ]
    
    rol = forms.ChoiceField(
        choices=ROL_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Rol del Usuario"
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña"
    )

    class Meta:
        model = User
        fields = ['email', 'first_name', 'password']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'email': 'Correo Electrónico (Será su usuario)',
            'first_name': 'Nombre Completo',
        }

class PedidoStatusForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ['estado_pago']
        widgets = {
            'estado_pago': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'estado_pago': 'Cambiar Estado del Pedido a:'
        }

class ContenidoLibroForm(forms.ModelForm):
    class Meta:
        model = ContenidoLibro
        fields = ['tipo_contenido', 'archivo', 'orden']
        widgets = {
            'tipo_contenido': forms.Select(attrs={'class': 'form-control'}),
            'archivo': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'orden': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 1 (para Página 1)'}),
        }
        labels = {
            'tipo_contenido': '¿Qué estás subiendo?',
            'archivo': 'Selecciona el archivo (JPG o MP3)',
            'orden': 'Número de Página / Orden'
        }


class ContenidoBulkForm(forms.Form):
    archivos = forms.FileField(
        
        widget=forms.FileInput, 
        label="Seleccionar Páginas (JPG/PNG)",
        required=False
    )

   
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['archivos'].widget.attrs.update({'multiple': True})


class AdminPasswordChangeForm(SetPasswordForm):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})