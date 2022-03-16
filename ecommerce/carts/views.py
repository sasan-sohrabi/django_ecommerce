from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from carts.models import Cart, CartItem
from store.models import Product, Variation


def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def add_cart(request, product_id):
    product = Product.objects.get(id=product_id)
    product_variations = []
    if request.method == 'POST':
        for item in request.POST:
            key = item
            value = request.POST[key]
            try:
                variation = Variation.objects.get(product=product, variation_category__iexact=key,
                                                  variation_value__iexact=value)
                product_variations.append(variation)

            except ObjectDoesNotExist:
                pass
    print(product_variations, 'asaaaaaaaaaaaaaaaaaaaa')
    try:
        cart = Cart.objects.get(cart_id=_cart_id(request))
    except ObjectDoesNotExist:
        cart = Cart.objects.create(
            cart_id=_cart_id(request)
        )
        cart.save()

    is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart)
    if is_cart_item_exists.exists():
        # print('1111111111111111111')
        cart_item = CartItem.objects.filter(product=product, cart=cart)
        # existing_variations - > database
        # current variations -> product_variations
        # item_id -> database
        ex_var_list = []
        id = []
        for item in cart_item:
            existing_variations = item.variations.all()
            ex_var_list.append(list(existing_variations))
            # print(ex_var_list, '111111111111111-----1111111111111111')
            id.append(item.id)
        # print(product_variations, '222222222222222--------------222222222222')
        # print(product_variations in ex_var_list)
        if product_variations in ex_var_list:
            index = ex_var_list.index(product_variations)
            item_id = id[index]
            item = CartItem.objects.get(product=product, id=item_id)
            item.quantity += 1
            item.save()
        else:
            item = CartItem.objects.create(product=product, quantity=1, cart=cart)
            if len(product_variations) > 0:
                item.variations.clear()
                item.variations.add(*product_variations)
                item.save()

    else:
        # print('000000000000000')
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart
        )
        if len(product_variations) > 0:
            cart_item.variations.clear()
            cart_item.variations.add(*product_variations)
        cart_item.save()
    return redirect('cart')


def decrement_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    try:
        cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')


def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(cart_id=_cart_id(request))
    cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


def cart(requests, total=0, quantity=0, is_active=None):
    try:
        cart = Cart.objects.get(cart_id=_cart_id(requests))
        cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            print(cart_item.variations.all())
            total += (cart_item.product.price * cart_item.quantity)
            quantity = cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax

    except ObjectDoesNotExist:
        total = 0
        quantity = 0
        cart_items = []
        tax = 0
        grand_total = 0

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }


    return render(requests, 'store/cart.html', context)
