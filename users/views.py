from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from . import serializers
from .models import User
from django.contrib.auth.models import Group
from api.permission import DynamicRolePermission

class RoleViewSet(viewsets.ModelViewSet):
    permission_classes = [DynamicRolePermission]
    # Add custom permission mapping for special actions
    permission_codenames = {
        'add_roles': 'users.assign_roles',
        'remove_roles': 'users.assign_roles',
    }
    queryset = Group.objects.all()
    
    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ['retrieve', 'list']:
            queryset = queryset.prefetch_related('permissions')
        return queryset

    def get_serializer_class(self):
        if self.action in ['retrieve','list']:
            return serializers.RoleDetailSerializer
        return serializers.RoleSerializer

class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [DynamicRolePermission]
    permission_codenames = {
        'roles': 'users.view_user_roles',
        'add_roles': 'users.assign_roles',
        'remove_roles': 'users.assign_roles',
    }
    queryset = User.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return serializers.UserCreateSerializer
        return serializers.UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.prefetch_related('groups')

    @action(detail=True, methods=['post'])
    def add_roles(self, request, pk=None):
        user = self.get_object()
        role_ids = request.data.get('roles', [])
        user.groups.add(*role_ids)
        return Response({'status': 'roles added'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def remove_roles(self, request, pk=None):
        user = self.get_object()
        role_ids = request.data.get('roles', [])
        user.groups.remove(*role_ids)
        return Response({'status': 'roles removed'}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'])
    def roles(self, request, pk=None):
        user = self.get_object()
        roles = user.groups.all()
        serializer = serializers.RoleDetailSerializer(roles, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)