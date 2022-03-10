from .models import Cart, CartItem
from .views import _cart_id


def counter(requests):
    cart_items_count = 0
    if 'admin' in requests.path:
        return {}
    else:
        try:
            cart = Cart.objects.get(cart_id=_cart_id(requests))
            cart_items = CartItem.objects.filter(cart=cart)
            for cart_item in cart_items:
                cart_items_count += cart_item.quantity
        except Cart.DoesNotExist:
            cart_items_count = 0
    return dict(cart_items_count=cart_items_count)
