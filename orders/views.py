from orders import serializers
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin
from rest_framework import viewsets,permissions
from orders.models import Cart, CartItem, Order, OrderItem
from api.permission import DynamicRolePermission  
from api.mixins import OwnershipCheckMixin
from orders.telegram import send_telegram_message

class CartViewSet(viewsets.GenericViewSet, CreateModelMixin, RetrieveModelMixin, OwnershipCheckMixin):
    permission_classes = [DynamicRolePermission]
    serializer_class = serializers.CartSerializers
    owner_field = 'user'  # Enable ownership checks

    def get_permissions(self):
        return [permissions.IsAuthenticated()]


    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    def get_queryset(self):
        return Cart.objects.prefetch_related('items__product').filter(user=self.request.user)

class CartItemViewSet(viewsets.ModelViewSet, OwnershipCheckMixin):
    permission_classes = [DynamicRolePermission]
    http_method_names = ['get','post','patch','delete']
    owner_field = 'cart.user'  # Nested ownership path


    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.AddCartItemSeralizers
        elif self.request.method == 'PATCH':
            return serializers.CartItemUpdaeSerializers
        return serializers.CartItemSerializer

    def get_queryset(self):
        # Secure by user ownership
        return CartItem.objects.filter(
            cart_id=self.kwargs.get('cart_pk'),
            cart__user=self.request.user
        )

    def get_serializer_context(self):
        return {'cart_id': self.kwargs.get('cart_pk')}

class OrderViewSet(viewsets.ModelViewSet, OwnershipCheckMixin):
    permission_classes = [DynamicRolePermission]
    owner_field = 'user'  # Enable ownership checks

    def get_permissions(self):
        return [permissions.IsAuthenticated()]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return serializers.CreateOrderSerializer
        return serializers.OrderSerializers
    
    def get_serializer_context(self):
        return {'user_id': self.request.user.id}

    def get_queryset(self):
        # Add security: staff see all, users see only their own
        queryset = Order.objects.prefetch_related('items__product')
        
        if not self.request.user.is_staff:
            queryset = queryset.filter(user=self.request.user)
            
        return queryset

    # Add ownership check for extra security
    def check_ownership(self, request, obj):
        return obj.user == request.user
    
    def perform_create(self, serializer):
        # Save the order normally
        super().perform_create(serializer)
        
        # Send Telegram notification
        order = serializer.instance
        message = (
            f"<b>New Order Received!</b>\n"
            f"🆔 Order ID: <code>{order.id}</code>\n"
            f"👤 User: {order.user.email}\n"
            f"📅 Date: {order.created_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"💰 Total: ${order.total_price}"
        )
        
        # Send async to avoid blocking response
        import threading
        thread = threading.Thread(
            target=send_telegram_message, 
            args=(message,)
        )
        thread.start()