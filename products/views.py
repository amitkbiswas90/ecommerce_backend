from rest_framework import viewsets, permissions
from products.models import Product, Category, Review, ProductImage
from products import serializers
from django_filters.rest_framework import DjangoFilterBackend
from products.filter import ProductFilter
from  rest_framework.filters import SearchFilter
from products.pagination import PagePagination
from api.permission import DynamicRolePermission
from api.mixins import OwnershipCheckMixin




class ProductViewSet(viewsets.ModelViewSet, OwnershipCheckMixin):
    permission_classes = [DynamicRolePermission]
    queryset = Product.objects.all().select_related('category')
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name','description']
    filterset_class = ProductFilter
    pagination_class = PagePagination

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.IsAuthenticated()]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.ViewProductSerializer
        return serializers.ProductSerializer

class ProductImageViewSet(viewsets.ModelViewSet,OwnershipCheckMixin):
    serializer_class = serializers.ProductImageSerializer
    permission_classes = [DynamicRolePermission]

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()

    def get_queryset(self):
        return ProductImage.objects.filter(product_id=self.kwargs.get('product_pk'))
    
    def perform_create(self, serializer):
        serializer.save(product_id=self.kwargs.get('product_pk'))

class CategoryViewSet(viewsets.ModelViewSet, OwnershipCheckMixin):
    permission_classes = [DynamicRolePermission]
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()
    

class ReviewViewSet(viewsets.ModelViewSet, OwnershipCheckMixin):
    serializer_class = serializers.ReviewSerializers
    permission_classes = [permissions.AllowAny]
    owner_field = 'user'

    def get_queryset(self):
        """Return reviews for the current product"""
        # Use 'product_pk' instead of 'product_id'
        product_id = self.kwargs.get('product_pk')
        
        if not product_id:
            return Review.objects.none()
            
        base_query = Review.objects.filter(product_id=product_id)
        
        # For non-public actions, also filter by current user
        if self.action not in ['list', 'retrieve']:
            base_query = base_query.filter(user=self.request.user)
        return base_query

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [permissions.AllowAny()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            product_id=self.kwargs.get('product_pk')
        )