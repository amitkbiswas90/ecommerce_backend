class OwnershipCheckMixin:
    """
    Mixin for object-level ownership checks
    Define owner_field in your view to specify relationship
    """
    owner_field = 'user'  # Default field name pointing to owner
    
    def check_ownership(self, request, obj):
        # Resolve owner from object
        owner = getattr(obj, self.owner_field, None)
        
        # Check if owner matches request user
        return owner == request.user