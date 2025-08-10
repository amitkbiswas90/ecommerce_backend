from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers
from .models import User
from django.contrib.auth.models import Group, Permission

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = ['id','first_name','last_name','address','phone_number','email','password']

class UserSerializer(BaseUserSerializer):
    roles = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Group.objects.all(),
        source='groups',
        required=False
    )

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = ['id','first_name','last_name','address','phone_number','email','roles']
        extra_kwargs = {'password': {'write_only': True}}

    def update(self, instance, validated_data):
        # Handle groups separately
        groups = validated_data.pop('groups', None)
        
        # Update other fields
        instance = super().update(instance, validated_data)
        
        # Update groups if provided
        if groups is not None:
            instance.groups.set(groups)
        
        return instance

# Keep your existing Permission and Role serializers
class PermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

class RoleSerializer(serializers.ModelSerializer):
    permissions = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Permission.objects.all()
    )
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']

class RoleDetailSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions']