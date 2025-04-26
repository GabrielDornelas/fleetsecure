from django.shortcuts import render
from rest_framework import viewsets, permissions, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, PasswordChangeSerializer
from rest_framework.permissions import IsAuthenticated, IsAdminUser

class IsAdminOrSelf(permissions.BasePermission):
    """
    Permission that allows access to administrators or the user themselves.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_admin or obj == request.user

class IsAdminUser(permissions.BasePermission):
    """
    Permission that allows access only to admin users.
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_admin)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        elif self.action in ['update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAdminOrSelf()]
        elif self.action == 'list':
            return [IsAuthenticated(), IsAdminUser()]
        return [IsAuthenticated()]
    
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'change_password':
            return PasswordChangeSerializer
        return UserSerializer
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsAdminOrSelf])
    def change_password(self, request, pk=None):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {"old_password": ["Incorrect current password"]},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({"status": "Password changed successfully"})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdminUser])
    def activate(self, request, pk=None):
        user = self.get_object()
        user.is_active = True
        user.save()
        return Response({"status": "User activated"})
    
    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated, IsAdminUser])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        user.is_active = False
        user.save()
        return Response({"status": "User deactivated"})
