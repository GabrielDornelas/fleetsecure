from rest_framework import serializers
from .models import Driver
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id']

class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = ['id', 'user', 'license_number', 'is_active', 'full_name']
        read_only_fields = ['id']
    
    def get_full_name(self, obj):
        return obj.user.get_full_name()

class DriverCreateSerializer(serializers.ModelSerializer):
    username = serializers.CharField(write_only=True)
    first_name = serializers.CharField(write_only=True)
    last_name = serializers.CharField(write_only=True)
    email = serializers.EmailField(write_only=True)
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    
    class Meta:
        model = Driver
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'license_number', 'is_active']
    
    def create(self, validated_data):
        user_data = {
            'username': validated_data.pop('username'),
            'first_name': validated_data.pop('first_name'),
            'last_name': validated_data.pop('last_name'),
            'email': validated_data.pop('email'),
        }
        password = validated_data.pop('password')
        
        user = User.objects.create(**user_data)
        user.set_password(password)
        user.save()
        
        driver = Driver.objects.create(user=user, **validated_data)
        return driver 