from rest_framework import permissions

class DynamicRolePermission(permissions.BasePermission):
    def get_required_permission(self, view):
        """Map view actions to permission codenames"""
        # Get model from view's queryset or get_queryset()
        if view.queryset is not None:
            model = view.queryset.model
        else:
            try:
                # Get model from get_queryset() if available
                model = view.get_queryset().model
            except (AttributeError, AssertionError):
                return None

        app_label = model._meta.app_label
        model_name = model._meta.model_name
        
        action_map = {
            'list': 'view',
            'retrieve': 'view',
            'create': 'add',
            'update': 'change',
            'partial_update': 'change',
            'destroy': 'delete',
        }
        
        action = view.action
        if action in action_map:
            return f'{app_label}.{action_map[action]}_{model_name}'
        
        # Handle custom actions
        if hasattr(view, 'permission_codenames') and action in view.permission_codenames:
            return view.permission_codenames[action]
        
        return None

    def has_permission(self, request, view):
        if request.user.is_superuser:
            return True
            
        perm_name = self.get_required_permission(view)
        if not perm_name:
            return True
            
        return request.user.has_perm(perm_name)

    def has_object_permission(self, request, view, obj):
        if hasattr(view, 'check_ownership') and view.check_ownership(request, obj):
            return True
        return self.has_permission(request, view)