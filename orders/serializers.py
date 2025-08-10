from orders.models import Cart, CartItem, Order, OrderItem
from rest_framework import serializers
from products.models import Product



class AddCartItemSeralizers(serializers.ModelSerializer):
    product_id = serializers.IntegerField()
    class Meta:
        model = CartItem
        fields = ['id','product_id','quantity']
    
    def validate_product_id(self, product_id):
        if not Product.objects.filter(pk=product_id).exists():
            raise serializers.ValidationError(
                f"This product {product_id} does not exists"
            )
        return product_id

    def save(self, **kwargs):
        cart_id = self.context.get('cart_id')
        product_id = self.validated_data.get('product_id')
        quantity = self.validated_data.get('quantity')

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, product_id=product_id
            )
            cart_item.quantity += quantity
            self.instance = cart_item.save()
        
        except CartItem.DoesNotExist:
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data
            )
        return self.instance
        

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id','name','price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price'
    )
    class Meta:
        model = CartItem
        fields = ['id','cart','product','quantity','total_price']

    
    def get_total_price(self, cart_item:CartItem):
        return cart_item.quantity * cart_item.product.price
    
class CartItemUpdaeSerializers(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['quantity']


class CartSerializers(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(
        method_name='get_total_price'
    )
    class Meta:
        model = Cart
        fields = ['id','user','items','total_price']
        read_only_fields = ['user']
    
    def get_total_price(self, cart:Cart):
        return sum([item.product.price * item.quantity for item in cart.items.all()]) 

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()
    
    def validate_cart_id(self, cart_id):
        if not Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('No cart found with this id')
        if not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError('Cart is empty')
        return cart_id
    
    def create(self, validated_data):
        cart_id = validated_data['cart_id']
        user_id = self.context.get('user_id')

        cart = Cart.objects.get(pk=cart_id)
        cart_items = cart.items.select_related('product').all()
        total_price = sum([item.product.price * item.quantity for item in cart_items])
        order = Order.objects.create(user_id=user_id, total_price=total_price)

        order_items =[
            OrderItem(
                order=order,
                product=item.product,
                price = item.product.price,
                quantity = item.quantity,
                total_price = item.product.price * item.quantity
            )
            for item in cart_items
        ]
        OrderItem.objects.bulk_create(order_items)
        cart.delete()
        return order
    
    def to_representation(self, instance):
        return OrderSerializers(instance).data


class OrderItemSerializers(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['id','product','quantity','price','total_price']

class OrderSerializers(serializers.ModelSerializer):
    items = OrderItemSerializers(many=True)
    
    class Meta:
        model = Order
        fields = ['id', 'user', 'status', 'total_price', 'items', 'created_at']