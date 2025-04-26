from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Truck
from .serializers import TruckSerializer
from rest_framework.decorators import action
from rest_framework.response import Response


class TruckViewSet(viewsets.ModelViewSet):
    queryset = Truck.objects.all()
    serializer_class = TruckSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['user', 'year', 'model']
    search_fields = ['plate_number', 'model']
    ordering_fields = ['year', 'user__first_name']
    
    @action(detail=False)
    def by_user(self, request):
        user_id = request.query_params.get('user_id')
        if user_id:
            trucks = Truck.objects.filter(user_id=user_id)
            serializer = self.get_serializer(trucks, many=True)
            return Response(serializer.data)
        return Response({"error": "user_id parameter is required"}, status=400)
    
    @action(detail=False)
    def by_year(self, request):
        year = request.query_params.get('year')
        if year:
            trucks = Truck.objects.filter(year=year)
            serializer = self.get_serializer(trucks, many=True)
            return Response(serializer.data)
        return Response({"error": "year parameter is required"}, status=400)
