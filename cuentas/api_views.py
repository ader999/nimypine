from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from .serializers import LoginSerializer, RegisterSerializer, UserSerializer
from .utils import enviar_email_confirmacion


class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    """
    API view for user registration.
    Creates a new user, sends email confirmation, and returns success message.
    """
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            enviar_email_confirmacion(user)
            return Response(
                {'message': 'User created successfully. Check your email for confirmation code.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginAPIView(APIView):
    """
    API view for user login.
    Authenticates user, checks email confirmation, and returns token if valid.
    """
    permission_classes = [AllowAny]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                if user.email_confirmado:
                    token, created = Token.objects.get_or_create(user=user)
                    return Response({
                        'token': token.key,
                        'user': UserSerializer(user).data
                    }, status=status.HTTP_200_OK)
                else:
                    enviar_email_confirmacion(user)
                    return Response(
                        {'error': 'Email not confirmed. Check your email for the confirmation code.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    """
    API view for user logout.
    Requires authentication and deletes the user's token.
    """
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response(
                {'message': 'Logged out successfully'},
                status=status.HTTP_200_OK
            )
        except Exception as e:
            return Response(
                {'error': 'Logout failed'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )