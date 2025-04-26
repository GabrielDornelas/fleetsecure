from rest_framework import serializers
from .models import Truck
from users.serializers import UserSerializer

class TruckSerializer(serializers.ModelSerializer):
    user_details = UserSerializer(source='user', read_only=True)
    
    class Meta:
        model = Truck
        fields = ['id', 'plate_number', 'model', 'year', 'user', 'user_details']
        read_only_fields = ['id']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('user', None)
        return representation
        
    def validate(self, attrs):
        """Validate that the user is active"""
        user = attrs.get('user')
        if user and not user.is_active:
            raise serializers.ValidationError({"user": "Cannot assign truck to inactive user"})
        return attrs
