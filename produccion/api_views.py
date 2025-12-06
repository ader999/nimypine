from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication, SessionAuthentication
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

class StoreProductListAPIView(generics.ListAPIView):
    """
    API endpoint that lists all products from Mipymes that have enabled
    their store visibility (tienda_visible=True).
    """
    serializer_class = ProductoSerializer
    permission_classes = [] # Public API for the store (or use specific key later)
    authentication_classes = []

    def get_queryset(self):
        # Filter products where the related Mipyme has tienda_visible=True AND the product is marked as available
        # AND the product has an image
        return Producto.objects.filter(mipyme__tienda_visible=True, disponible_en_api=True).exclude(imagen='').exclude(imagen__isnull=True).order_by('nombre')

class ToggleTiendaVisibleView(APIView):
    """
    API endpoint to toggle the 'tienda_visible' status of the authenticated user's Mipyme.
    """
    permission_classes = [IsAuthenticated]
    authentication_classes = [SessionAuthentication, TokenAuthentication]

    def post(self, request, *args, **kwargs):
        try:
            mipyme = request.user.mipyme
            if not mipyme:
                 return Response({"error": "User does not have a Mipyme"}, status=status.HTTP_400_BAD_REQUEST)
            
            # Toggle the status
            mipyme.tienda_visible = not mipyme.tienda_visible
            mipyme.save()
            
            return Response({
                "status": "success",
                "tienda_visible": mipyme.tienda_visible,
                "message": f"Tienda {'activada' if mipyme.tienda_visible else 'desactivada'} correctamente."
            }, status=status.HTTP_200_OK)
            
        except AttributeError:
            return Response({"error": "User does not have a Mipyme associated"}, status=status.HTTP_400_BAD_REQUEST)
