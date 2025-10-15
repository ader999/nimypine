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