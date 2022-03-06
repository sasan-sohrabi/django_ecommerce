from django.shortcuts import render


def cart(requests):
    return render(requests, 'store/cart.html')
