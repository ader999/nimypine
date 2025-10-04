import pytest
from django.contrib.auth import get_user_model
from produccion.models import Insumo, Producto, Proceso, Formulacion, UnidadMedida
from cuentas.models import Mipyme, SectorEconomico

User = get_user_model()

@pytest.fixture
def setup_db():
    """
    Fixture para configurar la base de datos con datos de prueba.
    """
    user = User.objects.create_user(username='test_user', email='test@test.com', password='password')
    sector = SectorEconomico.objects.create(nombre='Alimentos')
    mipyme = Mipyme.objects.create(propietario=user, nombre='MiPyME de Alimentos', sector=sector)
    user.mipyme = mipyme
    user.save()
    
    unidad_kg = UnidadMedida.objects.create(nombre='Kilogramo', abreviatura='kg')
    unidad_un = UnidadMedida.objects.create(nombre='Unidad', abreviatura='un')

    insumo = Insumo.objects.create(
        nombre='Harina',
        mipyme=mipyme,
        unidad=unidad_kg,
        costo_unitario=1.5,
        stock_actual=100
    )
    
    proceso = Proceso.objects.create(
        nombre='Mezclado',
        mipyme=mipyme,
        costo_por_hora=10  # Añadir costo por hora para el proceso
    )
    
    return user, mipyme, insumo, proceso, unidad_un

@pytest.mark.django_db
def test_crear_producto(setup_db):
    """
    Prueba la creación de un nuevo Producto.
    """
    user, mipyme, insumo, proceso, unidad_un = setup_db
    
    producto = Producto.objects.create(
        nombre='Pan',
        descripcion='Pan artesanal.',
        mipyme=mipyme
    )
    
    # La formulación ahora relaciona producto con insumo, no con proceso
    Formulacion.objects.create(
        producto=producto,
        insumo=insumo,
        cantidad=0.5
    )
    
    assert producto.nombre == 'Pan'
    assert producto.mipyme == mipyme
    assert producto.formulacion.count() == 1
    assert producto.formulacion.first().insumo.nombre == 'Harina'