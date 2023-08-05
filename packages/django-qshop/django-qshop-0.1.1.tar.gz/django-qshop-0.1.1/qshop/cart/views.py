from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, Http404
from django.core.urlresolvers import reverse
from django.utils.datastructures import DotExpandedDict
from django.contrib import messages
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User, UserManager
from django.contrib.auth import logout

from . import Cart, ItemAlreadyExists, ItemDoesNotExist
from ..models import Product
from .forms import OrderForm
from .models import Order


def add_to_cart(request, product_id):
    cart = Cart(request)

    quantity = request.GET.get('quantity', 1)
    variation_id = request.GET.get('variation', None)
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        messages.add_message(request, messages.ERROR, _('Wrong product.'))
    else:

        product.select_variation(variation_id)

        cart.add(product, quantity)

        messages.add_message(request, messages.INFO, _('Product added to <a href="%s">cart</a>.') % reverse('cart'))

    return_url = request.GET.get('return_url', None)
    if return_url:
        return HttpResponseRedirect(return_url)
    return HttpResponseRedirect(reverse('cart'))


def remove_from_cart(request, item_id):
    cart = Cart(request)
    cart.remove(item_id)
    return HttpResponseRedirect(reverse('cart'))


def update_cart(request):
    cart = Cart(request)
    data = DotExpandedDict(request.POST)
    for (item_id, quantity) in data['quantity'].items():
        try:
            quantity = int(quantity)
            if quantity < 1:
                cart.remove(item_id)
            else:
                cart.update(item_id, quantity)
        except:
            pass
    return HttpResponseRedirect(reverse('cart'))


def show_cart(request):
    cart = Cart(request)
    return render_to_response('qshop/cart/cart.html', {
        'cart': cart,
    }, context_instance=RequestContext(request))


def order_cart(request):
    cart = Cart(request)
    if cart.total_products() < 1:
        return HttpResponseRedirect(reverse('cart'))

    order_form = OrderForm()

    if request.method == 'POST':
        order_form = OrderForm(request.POST)

        if order_form.is_valid():
            order = order_form.save(cart)
            request.session['order_pk'] = order.pk
            cart.checkout()
            return HttpResponseRedirect(order.get_redirect())

    return render_to_response('qshop/cart/order.html', {
        'cart': cart,
        'order_form': order_form,
    }, context_instance=RequestContext(request))


def cart_order_success(request):
    order_pk = request.session.get('order_pk', None)
    try:
        del request.session['order_pk']
    except:
        pass
    order = get_object_or_404(Order, pk=order_pk)
    return render_to_response('qshop/cart/order_success.html', {
        'order': order,
    }, context_instance=RequestContext(request))


def cart_order_cancelled(request):
    return render_to_response('qshop/cart/order_cancelled.html', {
    }, context_instance=RequestContext(request))


def cart_order_error(request):
    return render_to_response('qshop/cart/order_error.html', {
    }, context_instance=RequestContext(request))
