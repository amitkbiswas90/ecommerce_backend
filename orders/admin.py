from django.contrib import admin
from orders.models import Cart, CartItem, Order, OrderItem

class CustomCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_email', 'created_at']
    list_select_related = ['user']
    
    def user_email(self, obj):
        return obj.user.email if obj.user else "Guest"
    user_email.short_description = 'User Email'
    user_email.admin_order_field = 'user__email'

class CustomCartItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'cart_id', 'product_name', 'quantity']
    
    def cart_id(self, obj):
        return obj.cart.id
    cart_id.short_description = 'Cart ID'
    
    def product_name(self, obj):
        return str(obj.product)
    product_name.short_description = 'Product'

class CustomOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_email', 'get_total', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__email', 'id']
    
    def user_email(self, obj):
        return obj.user.email if obj.user else "Guest"
    user_email.short_description = 'Customer Email'
    
    def get_total(self, obj):
        return f"${obj.total:.2f}" if hasattr(obj, 'total') else "N/A"
    get_total.short_description = 'Total Amount'

class CustomOrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_id', 'product_name', 'quantity', 'get_unit_price', 'get_total_price']
    
    def order_id(self, obj):
        return obj.order.id
    order_id.short_description = 'Order ID'
    
    def product_name(self, obj):
        return str(obj.product)
    product_name.short_description = 'Product'
    
    def get_unit_price(self, obj):
        return f"${obj.price:.2f}" if hasattr(obj, 'price') else "N/A"
    get_unit_price.short_description = 'Unit Price'
    
    def get_total_price(self, obj):
        if hasattr(obj, 'price'):
            return f"${obj.quantity * obj.price:.2f}"
        return "N/A"
    get_total_price.short_description = 'Total Price'

admin.site.register(Cart, CustomCartAdmin)
admin.site.register(CartItem, CustomCartItemAdmin)
admin.site.register(Order, CustomOrderAdmin)
admin.site.register(OrderItem, CustomOrderItemAdmin)