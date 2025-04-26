from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Driver
from .serializers import DriverSerializer, DriverCreateSerializer
from rest_framework.decorators import action

# Create your views here.

class DriverViewSet(viewsets.ModelViewSet):
    queryset = Driver.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return DriverCreateSerializer
        return DriverSerializer
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        try:
            driver = Driver.objects.get(user=request.user)
            serializer = self.get_serializer(driver)
            return Response(serializer.data)
        except Driver.DoesNotExist:
            return Response(
                {"detail": "The current user is not a driver."},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=True, methods=['patch'])
    def activate(self, request, pk=None):
        driver = self.get_object()
        driver.is_active = True
        driver.save()
        return Response({"status": "Driver activated"})
    
    @action(detail=True, methods=['patch'])
    def deactivate(self, request, pk=None):
        driver = self.get_object()
        driver.is_active = False
        driver.save()
        return Response({"status": "Driver deactivated"})
