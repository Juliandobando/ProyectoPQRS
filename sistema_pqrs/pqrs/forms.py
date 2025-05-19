#pqrs/form.py
from django import forms
from .models import PQRS, Cliente
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
import re

class LoginForm(forms.Form):
    numero_id = forms.CharField(label="Numero de identificación", max_length=20)
    contraseña =forms.CharField(widget=forms.PasswordInput, label="Contraseña")
# forms.py
class RadicarPQRSForm(forms.Form):
    tipo_id = forms.ChoiceField(choices=Cliente.TIPO_ID)
    numero_id = forms.CharField(max_length=20)
    def clean_numero_id(self):
        numero_id = self.cleaned_data['numero_id']
        if len(numero_id) < 10:
            raise forms.ValidationError("El número de identificación debe tener al menos 10 dígitos.")
        return numero_id
    nombre = forms.CharField(max_length=100)
    correo = forms.EmailField()
    def clean_correo(self):
        correo = self.cleaned_data['correo']
        if not correo.endswith('@gmail.com') and not correo.endswith('@hotmail.com'):
            raise forms.ValidationError("Solo se permiten correos @gmail.com o @hotmail.com")
        
        if ' ' in correo:
            raise forms.ValidationError("El correo no puede contener espacios.")
        return correo

    telefono = forms.CharField(max_length=15)
    def clean_telefono(self):
        telefono = self.cleaned_data['telefono']
        # Permitir números, espacios, guiones y paréntesis, opcional + al inicio
        pattern = r'^\+?[\d\s\-\(\)]{7,15}$'
        if not re.match(pattern, telefono):
            raise ValidationError("Número de teléfono inválido. Debe contener solo números y puede incluir +, espacios, guiones o paréntesis.")
        # Quitar caracteres no numéricos para validar longitud real de dígitos
        digitos = re.sub(r'\D', '', telefono)
        if len(digitos) < 7 or len(digitos) > 15:
            raise ValidationError("El número de teléfono debe tener entre 7 y 15 dígitos.")
        return telefono
    
    tipo = forms.ChoiceField(choices=PQRS.TIPO_PQRS)
    comentarios = forms.CharField(widget=forms.Textarea)
    archivo = forms.FileField(
        required=False,
        validators=[FileExtensionValidator(['pdf'])],
        help_text="Solo se permiten archivos PDF (máximo 5MB)"
    )
    def clean_archivo(self):
        archivo = self.cleaned_data.get('archivo')

        if archivo:
            if archivo.size > 5 * 1024 * 1024:  # 5 MB
                raise ValidationError("El archivo supera los 5MB.")
            if not archivo.name.endswith('.pdf'):
                raise ValidationError("Solo se permiten archivos en formato PDF.")
        return archivo

class GestorLoginForm(forms.Form):
    username = forms.CharField(
        label='Usuario',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Ingrese su usuario'})
    )
    password = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'placeholder': 'Ingrese su contraseña'})
    )

class GestionarPQRSForm(forms.ModelForm):
    class Meta:
        model = PQRS
        fields = ['estado', 'justificacion']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'justificacion': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
        }

    def clean_justificacion(self):
        justificacion = self.cleaned_data.get('justificacion')
        if not justificacion.strip():
            raise forms.ValidationError("Debe justificar el cambio")
        return justificacion
    
class PerfilClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['tipo_id', 'nombre', 'correo', 'telefono']

class CrearUsuarioForm(forms.Form):
    username = forms.CharField(label='Usuario', max_length=150)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)
    confirmar = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('confirmar')

        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data

class AdminLoginForm(forms.Form):
    username = forms.CharField(label='Usuario', max_length=150)
    password = forms.CharField(label='Contraseña', widget=forms.PasswordInput)


