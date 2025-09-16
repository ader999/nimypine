# cuentas/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Mipyme, TipoEmpresa
from .funciones import generar_username_unico


class RegistroCreadorForm(forms.Form):
    first_name = forms.CharField(max_length=150, required=True, label="Nombres")
    last_name = forms.CharField(max_length=150, required=True, label="Apellidos")
    email = forms.EmailField(required=True, label="Email")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")
    password_confirmacion = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirmar Contraseña")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email

    def clean_password_confirmacion(self):
        password = self.cleaned_data.get("password")
        password_confirmacion = self.cleaned_data.get("password_confirmacion")
        if password and password_confirmacion and password != password_confirmacion:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password_confirmacion



class RegistroMipymeForm(forms.Form):
    # --- Datos de la Empresa ---
    nombre_empresa = forms.CharField(max_length=255, required=True, label="Nombre de la Empresa")
    identificador_fiscal = forms.CharField(max_length=50, required=False, label="Identificador Fiscal RFC, RUT, etc. (Opcional)")
    tipo_empresa = forms.ModelChoiceField(
        queryset=TipoEmpresa.objects.all(),
        required=True,
        label="Tipo de Empresa",
        empty_label="Selecciona una categoría"
    )

    # --- Datos del Administrador (NUEVOS CAMPOS) ---
    # Eliminamos el campo 'username'
    first_name = forms.CharField(max_length=150, required=True, label="Nombres del Administrador")
    last_name = forms.CharField(max_length=150, required=True, label="Apellidos del Administrador")
    email = forms.EmailField(required=True, label="Email del Administrador")
    password = forms.CharField(widget=forms.PasswordInput, required=True, label="Contraseña")
    password_confirmacion = forms.CharField(widget=forms.PasswordInput, required=True, label="Confirmar Contraseña")

    # El resto de los métodos de validación se quedan igual
    def clean_password_confirmacion(self):
        password = self.cleaned_data.get("password")
        password_confirmacion = self.cleaned_data.get("password_confirmacion")
        if password and password_confirmacion and password != password_confirmacion:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password_confirmacion

class SoloMipymeForm(forms.ModelForm):
    class Meta:
        model = Mipyme
        fields = ['nombre', 'identificador_fiscal', 'tipo']
        labels = {
            'nombre': 'Nombre de tu Empresa',
            'identificador_fiscal': 'Identificador Fiscal (Opcional)',
            'tipo': 'Tipo de Empresa'
        }


class CreacionUsuarioMipymeForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = Usuario
        # ¡IMPORTANTE! Eliminamos 'username' de los campos que ve el usuario.
        fields = ('first_name', 'last_name', 'email', 'rol')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacemos que nombre y apellido sean obligatorios
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True

        # Añadimos clases de Bootstrap y etiquetas más claras
        self.fields['first_name'].label = "Nombre(s)"
        self.fields['last_name'].label = "Apellido(s)"
        self.fields['email'].label = "Correo Electrónico"
        self.fields['rol'].widget = forms.Select(attrs={'class': 'form-select'})

        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    def save(self, commit=True):
        # --- 3. SOBRESCRIBIMOS EL MÉTODO SAVE ---
        # Primero, llamamos al método save original pero sin guardar en la BD (commit=False)
        usuario = super().save(commit=False)

        # Obtenemos el nombre y apellido del formulario validado
        nombre = self.cleaned_data['first_name']
        apellido = self.cleaned_data['last_name']

        # Llamamos a nuestra función para generar y asignar el username
        usuario.username = generar_username_unico(nombre, apellido)

        # Si el argumento 'commit' es True, guardamos el usuario en la base de datos
        if commit:
            usuario.save()

        return usuario

class EditarRolUsuarioForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['rol']
        widgets = {
            'rol': forms.Select(attrs={'class': 'form-select'}),
        }