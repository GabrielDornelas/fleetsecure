from rest_framework import serializers
from django.contrib.auth import password_validation
from django.contrib.auth.password_validation import validate_password
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """Serializer for listing and detailing users"""
    full_name = serializers.SerializerMethodField()
    is_driver = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'cpf', 'phone_number', 'date_of_birth', 'profile_picture',
            'is_active', 'is_admin', 'is_driver'
        ]
        read_only_fields = ['id', 'is_active', 'is_driver']
    
    def get_full_name(self, obj):
        return obj.get_full_name()
    
    def get_is_driver(self, obj):
        return obj.is_driver()

class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating new users"""
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'cpf', 'phone_number', 
            'date_of_birth', 'profile_picture', 'is_admin'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs.pop('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords do not match"})
        return attrs
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            cpf=validated_data.get('cpf'),
            phone_number=validated_data.get('phone_number'),
            date_of_birth=validated_data.get('date_of_birth'),
            profile_picture=validated_data.get('profile_picture'),
            is_admin=validated_data.get('is_admin', False)
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class PasswordChangeSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({"new_password": "Passwords do not match"})
        return attrs 