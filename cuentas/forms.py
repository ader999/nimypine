# cuentas/forms.py

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Mipyme, TipoEmpresa, SectorEconomico
from produccion.models import UnidadMedida
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
    sector_economico = forms.ModelChoiceField(
        queryset=SectorEconomico.objects.all(),
        required=True,
        label="Sector Económico",
        empty_label="Selecciona un sector"
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
        fields = ['nombre', 'identificador_fiscal', 'tipo', 'sector']
        labels = {
            'nombre': 'Nombre de tu Empresa',
            'identificador_fiscal': 'Identificador Fiscal (Opcional)',
            'tipo': 'Tipo de Empresa',
            'sector': 'Sector Económico'
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


class CambiarContrasenaForm(forms.Form):
    password_actual = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Contraseña Actual",
        required=True
    )
    password_nueva = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nueva Contraseña",
        required=True
    )
    password_confirmacion = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Confirmar Nueva Contraseña",
        required=True
    )

    def clean_password_confirmacion(self):
        password_nueva = self.cleaned_data.get("password_nueva")
        password_confirmacion = self.cleaned_data.get("password_confirmacion")
        if password_nueva and password_confirmacion and password_nueva != password_confirmacion:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password_confirmacion


class ActualizarPerfilForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombre(s)',
            'last_name': 'Apellido(s)',
            'email': 'Correo Electrónico',
        }


class ConfigurarAvatarForm(forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['avatar']
        widgets = {
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'avatar': 'Seleccionar Avatar',
        }


class EditarInformacionEmpresaForm(forms.ModelForm):
    class Meta:
        model = Mipyme
        fields = ['nombre', 'numero_telefono', 'correo', 'identificador_fiscal']
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'correo': forms.EmailInput(attrs={'class': 'form-control'}),
            'identificador_fiscal': forms.TextInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'nombre': 'Nombre de la Empresa',
            'numero_telefono': 'Número de Teléfono',
            'correo': 'Correo Electrónico',
            'identificador_fiscal': 'Identificador Fiscal (RFC, RUT, etc.)',
        }


class ConfigurarLogoForm(forms.ModelForm):
    class Meta:
        model = Mipyme
        fields = ['logo']
        widgets = {
            'logo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'logo': 'Seleccionar Logo',
        }


class CambiarSectorEconomicoForm(forms.ModelForm):
    class Meta:
        model = Mipyme
        fields = ['sector']
        widgets = {
            'sector': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'sector': 'Sector Económico',
        }


class ConfigurarParametrosProduccionForm(forms.ModelForm):
    unidad_medida_predeterminada = forms.ModelMultipleChoiceField(
        queryset=UnidadMedida.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True,
        label="Unidades de medida predeterminadas",
        help_text="Selecciona las unidades de medida que utilizará la empresa"
    )

    class Meta:
        model = Mipyme
        fields = [
            'unidad_medida_predeterminada',
            'porcentaje_ganancia_predeterminado',
            'margen_desperdicio_predeterminado',
            'moneda_predeterminada'
        ]
        widgets = {
            'porcentaje_ganancia_predeterminado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100'
            }),
            'margen_desperdicio_predeterminado': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '50'
            }),
            'moneda_predeterminada': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'porcentaje_ganancia_predeterminado': 'Porcentaje de ganancia por defecto (%)',
            'margen_desperdicio_predeterminado': 'Margen de desperdicio por defecto (%)',
            'moneda_predeterminada': 'Moneda predeterminada',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si hay datos iniciales, marcar las opciones seleccionadas
        if self.instance and self.instance.pk and self.instance.unidad_medida_predeterminada:
            # Convertir IDs almacenados en JSON a objetos UnidadMedida
            ids_unidades = self.instance.unidad_medida_predeterminada
            if ids_unidades:
                unidades_seleccionadas = UnidadMedida.objects.filter(id__in=ids_unidades)
                self.fields['unidad_medida_predeterminada'].initial = unidades_seleccionadas

    def clean_unidad_medida_predeterminada(self):
        unidades = self.cleaned_data.get('unidad_medida_predeterminada')
        if not unidades:
            raise forms.ValidationError("Debes seleccionar al menos una unidad de medida.")
        # Convertir objetos a IDs para almacenar en JSON
        return [unidad.id for unidad in unidades]