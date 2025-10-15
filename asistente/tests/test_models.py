import pytest
from django.contrib.auth import get_user_model
from asistente.models import Conversacion, Mensaje, GuiaUsuario
from cuentas.models import Mipyme, SectorEconomico

User = get_user_model()

@pytest.fixture
def setup_asistente():
    """
    Fixture para configurar los datos necesarios para las pruebas del asistente.
    """
    user = User.objects.create_user(username='test_user', email='test@test.com', password='password')
    sector = SectorEconomico.objects.create(nombre='Tecnología')
    mipyme = Mipyme.objects.create(propietario=user, nombre='MiPyME Tech', sector=sector)
    user.mipyme = mipyme
    user.save()
    
    conversacion = Conversacion.objects.create(
        usuario=user,
        titulo='Conversación de prueba'
    )
    return user, conversacion

@pytest.mark.django_db
def test_crear_mensaje(setup_asistente):
    """
    Prueba la creación de un nuevo Mensaje en una Conversacion.
    """
    user, conversacion = setup_asistente
    
    mensaje = Mensaje.objects.create(
        conversacion=conversacion,
        es_usuario=True,
        contenido='Este es un mensaje de prueba.'
    )
    
    assert mensaje.conversacion == conversacion
    assert mensaje.es_usuario is True
    assert mensaje.contenido == 'Este es un mensaje de prueba.'
    assert conversacion.mensajes.count() == 1

@pytest.mark.django_db
def test_crear_guia_usuario():
    """
    Prueba la creación de una nueva GuiaUsuario.
    """
    guia = GuiaUsuario.objects.create(
        titulo='Guía de Inicio Rápido',
        pasos='Paso 1: Hacer esto. Paso 2: Hacer aquello.'
    )
    assert guia.titulo == 'Guía de Inicio Rápido'
    assert guia.pasos == 'Paso 1: Hacer esto. Paso 2: Hacer aquello.'
    assert str(guia) == 'Guía de Inicio Rápido'