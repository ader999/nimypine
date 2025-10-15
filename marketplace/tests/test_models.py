import pytest
from django.contrib.auth import get_user_model
from marketplace.models import PlantillaExcel
from cuentas.models import Mipyme, SectorEconomico

User = get_user_model()

@pytest.fixture
def usuario_mipyme():
    """
    Fixture para crear un usuario, un sector y una mipyme para las pruebas.
    """
    user = User.objects.create_user(username='test_user', email='test@test.com', password='password')
    sector = SectorEconomico.objects.create(nombre='Consultoría')
    mipyme = Mipyme.objects.create(propietario=user, nombre='MiPyME Test', sector=sector)
    # Asignar la MiPyME creada al perfil del usuario
    user.mipyme = mipyme
    user.save()
    return user

@pytest.mark.django_db
def test_crear_plantilla_excel(usuario_mipyme):
    """
    Prueba la creación de una nueva PlantillaExcel.
    """
    plantilla = PlantillaExcel.objects.create(
        nombre='Mi Plantilla de Prueba',
        descripcion='Una descripción de prueba para la plantilla.',
        creador=usuario_mipyme,
        precio=10.00,
        archivo_plantilla='archivos_plantillas/test.xlsx'
    )
    assert plantilla.nombre == 'Mi Plantilla de Prueba'
    assert plantilla.creador == usuario_mipyme
    assert str(plantilla) == 'Mi Plantilla de Prueba'
    assert plantilla.downloads == 0