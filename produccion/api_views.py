from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from .models import Producto
from .serializers import ProductoSerializer


class ProductListAPIView(generics.ListAPIView):
    """
    API view to list products for the authenticated user's mipyme.
    Supports filtering by mipyme if needed (though products are inherently filtered by user's mipyme).
    """
    serializer_class = ProductoSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['mipyme']

    def get_queryset(self):
        """
        Return products belonging to the authenticated user's mipyme.
        """
        user = self.request.user
        if hasattr(user, 'mipyme') and user.mipyme:
            return Producto.objects.filter(mipyme=user.mipyme).select_related('mipyme')
        return Producto.objects.none()
from .serializers import VentaSerializer


class CrearVentaAPIView(generics.CreateAPIView):
    """
    API view to create a new Venta.
    """
    serializer_class = VentaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        # La lógica de creación, incluyendo la asignación de mipyme
        # y el cálculo del total, ya está en el método `create` del serializer.
        # El serializer necesita acceso al 'request' para obtener el usuario.
        serializer.save()
