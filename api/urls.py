from django.urls import path, include
from rest_framework_nested import routers
from products.views import ProductViewSet, CategoryViewSet, ReviewViewSet, ProductImageViewSet
from orders.views import CartViewSet, CartItemViewSet, OrderViewSet
# from users.views import RoleViewSet, RolePermissionViewSet, PermissionView, UserRoleViewSet, UserViewSet
# from users.views import RoleCreateViewSet, PermissionViewSet
from users.views import RoleViewSet, UserViewSet

router = routers.DefaultRouter()

router.register('products',ProductViewSet, basename='product')
router.register('categories',CategoryViewSet)
router.register('carts', CartViewSet, basename='carts')
router.register('orders', OrderViewSet, basename='orders')
router.register('roles', RoleViewSet, basename='role')
router.register('users', UserViewSet, basename='users')  




product_router = routers.NestedDefaultRouter(
    router, 'products', lookup='product'
)
product_router.register('reviews',ReviewViewSet,basename='product-review')
product_router.register('images', ProductImageViewSet, basename='product-image')

cart_router = routers.NestedDefaultRouter(
    router, 'carts', lookup='cart'
)
cart_router.register('items', CartItemViewSet, basename='cart-item')


urlpatterns = [
    path('',include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(cart_router.urls)),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),
]