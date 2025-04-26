from rest_framework import serializers
from .models import Truck
from drivers.serializers import DriverSerializer

class TruckSerializer(serializers.ModelSerializer):
    driver_details = DriverSerializer(source='driver', read_only=True)
    
    class Meta:
        model = Truck
        fields = ['id', 'plate_number', 'model', 'year', 'driver', 'driver_details']
        read_only_fields = ['id']
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation.pop('driver', None)
        return representation
