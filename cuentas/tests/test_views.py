import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from cuentas.models import Mipyme, SectorEconomico, TipoEmpresa

User = get_user_model()

@pytest.fixture
def sector_economico(db):
    return SectorEconomico.objects.create(nombre='Tecnología')

@pytest.fixture
def tipo_empresa(db):
    return TipoEmpresa.objects.create(nombre='Servicios')

@pytest.mark.django_db
def test_registro_mipyme_view_asigna_propietario(client, sector_economico):
    """
    Prueba que la vista de registro de Mipyme asigne correctamente
    el propietario a la nueva Mipyme.
    """
    url = reverse('cuentas:registro_mipyme')
    data = {
        'nombre_empresa': 'Empresa de Prueba',
        'identificador_fiscal': '123456789',
        'sector_economico': sector_economico.id,
        'first_name': 'Admin',
        'last_name': 'Test',
        'email': 'admin@empresa.com',
        'password': 'password123',
        'password_confirmacion': 'password123',
    }
    
    response = client.post(url, data)
    
    # Redirige a la confirmación de email, lo cual es correcto
    assert response.status_code == 302
    assert response.url == reverse('cuentas:confirmar_email')
    
    # Verificamos que se hayan creado los objetos en la BD
    assert Mipyme.objects.count() == 1
    assert User.objects.count() == 1
    
    mipyme = Mipyme.objects.first()
    usuario = User.objects.first()
    
    # La prueba clave: el propietario de la mipyme es el usuario creado
    assert mipyme.propietario == usuario
    assert mipyme.nombre == 'Empresa de Prueba'
    assert usuario.mipyme == mipyme # El usuario pertenece a la mipyme
    assert usuario.es_admin_mipyme is True

@pytest.mark.django_db
def test_crear_mipyme_para_creador_asigna_propietario(client, sector_economico, tipo_empresa):
    """
    Prueba que la vista para crear una Mipyme para un usuario "creador"
    asigne correctamente al usuario logueado como propietario.
    """
    # 1. Creamos y logueamos un usuario creador sin mipyme
    creador = User.objects.create_user(
        username='creador',
        email='creador@test.com',
        password='password123',
        es_creador_contenido=True
    )
    client.login(username='creador', password='password123')
    
    # 2. Preparamos los datos para el formulario
    url = reverse('cuentas:crear_mipyme_para_creador')
    data = {
        'nombre': 'Mipyme del Creador',
        'sector': sector_economico.id,
        'tipo': tipo_empresa.id  # Añadimos el campo que faltaba
    }
    
    # 3. Hacemos el POST
    response = client.post(url, data)
    
    # 4. Verificamos la redirección y los datos en la BD
    assert response.status_code == 302
    assert response.url == reverse('produccion:panel')
    
    assert Mipyme.objects.count() == 1
    mipyme = Mipyme.objects.first()
    
    # Refrescamos el usuario desde la BD para obtener los datos actualizados
    creador.refresh_from_db()

    # La prueba clave: el propietario es el usuario que estaba logueado
    assert mipyme.propietario == creador
    assert creador.mipyme == mipyme