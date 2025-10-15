from rest_framework import serializers
from .models import Usuario


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Accepts username or email and password.
    """
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)


class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    Includes password confirmation and validation.
    """
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = Usuario
        fields = [
            'username',
            'email',
            'first_name',
            'last_name',
            'password',
            'password2',
            'rol',
            'avatar'
        ]

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = Usuario.objects.create_user(**validated_data)
        return user


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for user details and profile information.
    """
    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'mipyme',
            'es_admin_mipyme',
            'es_creador_contenido',
            'rol',
            'avatar',
            'email_confirmado',
            'is_active',
            'date_joined'
        ]
        read_only_fields = ['id', 'email_confirmado', 'is_active', 'date_joined']