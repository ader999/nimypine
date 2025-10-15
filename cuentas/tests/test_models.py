import pytest
from django.contrib.auth import get_user_model
from cuentas.models import Mipyme, SectorEconomico

User = get_user_model()

@pytest.mark.django_db
def test_crear_usuario():
    """
    Prueba la creación de un nuevo usuario.
    """
    usuario = User.objects.create_user(
        username='testuser', 
        email='test@example.com', 
        password='password123'
    )
    assert usuario.username == 'testuser'
    assert usuario.email == 'test@example.com'
    assert usuario.check_password('password123')
    assert not usuario.is_staff
    assert not usuario.is_superuser

@pytest.mark.django_db
def test_crear_mipyme():
    """
    Prueba la creación de una nueva MiPyme.
    """
    usuario = User.objects.create_user(
        username='testuser', 
        email='test@example.com', 
        password='password123'
    )
    sector = SectorEconomico.objects.create(nombre='Tecnología')
    mipyme = Mipyme.objects.create(
        nombre='Mi Mipyme de Prueba',
        propietario=usuario,
        sector=sector
    )
    assert mipyme.nombre == 'Mi Mipyme de Prueba'
    assert mipyme.propietario == usuario
    assert mipyme.sector == sector
