from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Product, Category, Cart, CartItem, Order, OrderItem


def product_list(request):
    category_slug = request.GET.get('category')
    search_query = request.GET.get('search')

    products = Product.objects.filter(available=True)

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)

    if search_query:
        products = products.filter(name__icontains=search_query)

    categories = Category.objects.all()

    return render(request, 'store/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': category_slug,
        'search_query': search_query
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, available=True)
    return render(request, 'store/product_detail.html', {'product': product})


@login_required
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if not created:
        cart_item.quantity += 1
        cart_item.save()

    messages.success(request, f'{product.name} added to cart.')
    return redirect('cart')


@login_required
def cart_remove(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('cart')


@login_required
def cart_view(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = CartItem.objects.filter(cart=cart) if cart else []
    total = sum(item.total for item in items)
    return render(request, 'store/cart.html', {'items': items, 'total': total})


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart:
        messages.error(request, 'Your cart is empty.')
        return redirect('cart')

    if request.method == 'POST':
        items = CartItem.objects.filter(cart=cart)
        total = sum(item.total for item in items)

        order = Order.objects.create(
            user=request.user,
            address=request.user.profile.address,
            phone=request.user.profile.phone,
            total=total
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                price=item.product.price,
                quantity=item.quantity
            )

        cart.delete()
        messages.success(request, 'Order placed successfully!')
        return redirect('order_detail', order_id=order.id)

    return render(request, 'store/checkout.html')


@login_required
def order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-created')
    return render(request, 'store/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    items = OrderItem.objects.filter(order=order)
    return render(request, 'store/order_detail.html', {'order': order, 'items': items})