import pytest
from django.contrib.auth import get_user_model
from produccion.models import Insumo, Producto, Proceso, Formulacion, UnidadMedida, Impuesto
from cuentas.models import Mipyme, SectorEconomico
import decimal

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

@pytest.mark.django_db
def test_crear_impuesto(setup_db):
    """
    Prueba la creación de un impuesto.
    """
    user, mipyme, insumo, proceso, unidad_un = setup_db

    impuesto = Impuesto.objects.create(
        mipyme=mipyme,
        nombre='IVA',
        porcentaje=15.0,
        activo=True
    )

    assert impuesto.nombre == 'IVA'
    assert impuesto.porcentaje == decimal.Decimal('15.00')
    assert impuesto.activo == True
    assert impuesto.mipyme == mipyme

@pytest.mark.django_db
def test_producto_con_impuestos(setup_db):
    """
    Prueba el cálculo de precio con impuestos en un producto.
    """
    user, mipyme, insumo, proceso, unidad_un = setup_db

    # Crear producto con formulación
    producto = Producto.objects.create(
        nombre='Pan con Impuestos',
        descripcion='Pan artesanal con IVA.',
        mipyme=mipyme
    )

    Formulacion.objects.create(
        producto=producto,
        insumo=insumo,
        cantidad=0.5
    )

    # Crear impuestos
    iva = Impuesto.objects.create(
        mipyme=mipyme,
        nombre='IVA',
        porcentaje=15.0,
        activo=True
    )

    dgi = Impuesto.objects.create(
        mipyme=mipyme,
        nombre='DGI',
        porcentaje=5.0,
        activo=True
    )

    # Asignar impuestos al producto
    producto.impuestos.add(iva, dgi)

    # Verificar cálculos
    costo_produccion = producto.costo_de_produccion  # 0.5 * 1.5 = 0.75
    precio_con_impuestos = producto.precio_con_impuestos  # 0.75 + (0.75 * 0.15) + (0.75 * 0.05) = 0.75 + 0.1125 + 0.0375 = 0.9

    assert costo_produccion == decimal.Decimal('0.75')
    assert precio_con_impuestos == decimal.Decimal('0.90')

@pytest.mark.django_db
def test_impuesto_inactivo_no_afecta_calculo(setup_db):
    """
    Prueba que los impuestos inactivos no afecten el cálculo de precio con impuestos.
    """
    user, mipyme, insumo, proceso, unidad_un = setup_db

    # Crear producto con formulación
    producto = Producto.objects.create(
        nombre='Pan sin Impuestos Activos',
        descripcion='Pan artesanal sin impuestos activos.',
        mipyme=mipyme
    )

    Formulacion.objects.create(
        producto=producto,
        insumo=insumo,
        cantidad=0.5
    )

    # Crear impuestos (uno activo, uno inactivo)
    iva_activo = Impuesto.objects.create(
        mipyme=mipyme,
        nombre='IVA Activo',
        porcentaje=15.0,
        activo=True
    )

    iva_inactivo = Impuesto.objects.create(
        mipyme=mipyme,
        nombre='IVA Inactivo',
        porcentaje=10.0,
        activo=False
    )

    # Asignar ambos impuestos al producto
    producto.impuestos.add(iva_activo, iva_inactivo)

    # Verificar que solo el impuesto activo afecta el cálculo
    costo_produccion = producto.costo_de_produccion  # 0.75
    precio_con_impuestos = producto.precio_con_impuestos  # 0.75 + (0.75 * 0.15) = 0.8625

    assert costo_produccion == decimal.Decimal('0.75')
    assert precio_con_impuestos == decimal.Decimal('0.8625')  # Solo IVA activo (15%)