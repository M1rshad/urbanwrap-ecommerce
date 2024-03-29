from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from home.models import Product, Category, Variation
from orders.models import Wallet
from user_auth.models import ShippingAddress, Coupon
from .models import Cart, CartItem, Wishlist, WishlistItem
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q 
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import ProductFilterForm
from user_auth.forms import ShippingAddressForm
# Create your views here.
def shop(request, category_slug=None):
    categories = None
    products = None
    form = None
    product_wishlist_map=None
    
    if category_slug != None:
        categories = get_object_or_404(Category, slug=category_slug, is_active=True)
        products = Product.objects.filter(category=categories, is_available=True, is_active=True)
        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True, is_active=True).order_by('id')
        form = ProductFilterForm(request.GET)
        if form.is_valid():
            category = form.cleaned_data.get('category')
            size = form.cleaned_data.get('size')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            if category:
                products = products.filter(category__category_name=category,is_available=True, is_active=True).order_by('id')
            if size:
                products = products.filter(variant__variation_value=size,is_available=True, is_active=True).order_by('id')
            if min_price:
                products = products.filter(price__gte=min_price,is_available=True, is_active=True).order_by('id')
            if max_price:
                products = products.filter(price__lte=max_price,is_available=True, is_active=True).order_by('id')
        
        if request.user.is_authenticated:
            wishlist_items = WishlistItem.objects.filter(user=request.user)
        else:
            wishlist_items = WishlistItem.objects.filter(wishlist__wishlist_id = _wishlist_id(request))
        product_wishlist_map = {item.product_id: True for item in wishlist_items}

        paginator = Paginator(products, 12)
        page = request.GET.get('page')
        paged_product = paginator.get_page(page)
        product_count = products.count()

 
                
    context = {
        'products' : paged_product,
        'product_count' : product_count,
        'form': form,
        'product_wishlist_map': product_wishlist_map,
        }
    return render(request, 'shop/shop.html', context)


@csrf_exempt
def product_detail(request, category_slug, product_slug):
    try:
        single_product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        variation = single_product.variant.all().order_by('id')
        in_cart =  CartItem.objects.filter(cart__cart_id=_cart_id(request), product = single_product).exists()
        if request.user.is_authenticated:
            in_wishlist=WishlistItem.objects.filter(user=request.user, product=single_product).exists()
        else:
            in_wishlist = WishlistItem.objects.filter(wishlist__wishlist_id=_wishlist_id(request), product=single_product).exists()
    except Exception as e:
        raise e
    context = {
        'single_product' : single_product,
        'in_cart' : in_cart,
        'variation':variation,
        'in_wishlist':in_wishlist,
        }
    return render(request, 'shop/product_detail.html', context)

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart

@csrf_exempt
def add_cart(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) 
    quantity=1

    #if user is authenticated
    if current_user.is_authenticated:
        product_variation = []
        if request.POST:
            for key, value in request.POST.items():
                if key != 'quantity':
                    try:
                        variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                        product_variation.append(variation)
                    except:
                        pass
                else:
                    quantity = int(request.POST.get('quantity', 1))
        
        # # Check if the total stock of selected variations is sufficient
        # total_stock = sum(variation.stock for variation in product_variation)
        # if total_stock < quantity:
        #     messages.error(request, 'Insufficient stock.')
        #     return redirect('product_detail')


        is_cart_item_exists = CartItem.objects.filter(product=product, user=current_user).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, user=current_user)

            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

                
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity += quantity
               
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=quantity, user=current_user)
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
            wishlist_item = WishlistItem.objects.filter(user=request.user, product_id=product_id).first()
            if wishlist_item:
                wishlist_item.delete()

        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = quantity,
                user = current_user
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            wishlist_item = WishlistItem.objects.filter(user=request.user, product_id=product_id).first()
            if wishlist_item:
                wishlist_item.delete()
        return redirect('cart')

    else:
        product_variation = []
        if request.POST:
            for key, value in request.POST.items():
                if key != 'quantity':
                    try:
                        variation = Variation.objects.get(product=product, variation_category__iexact=key, variation_value__iexact=value)
                        product_variation.append(variation)
                    except:
                        pass
                else:
                    quantity = int(request.POST.get('quantity', 1))

        try:
            cart = Cart.objects.get(cart_id=_cart_id(request))
        except Cart.DoesNotExist:
            cart = Cart.objects.create(
                cart_id = _cart_id(request)
            )
            cart.save()

        is_cart_item_exists = CartItem.objects.filter(product=product, cart=cart).exists()
        if is_cart_item_exists:
            cart_item = CartItem.objects.filter(product=product, cart=cart)

            ex_var_list=[]
            id=[]
            for item in cart_item:
                existing_variation = item.variations.all()
                ex_var_list.append(list(existing_variation))
                id.append(item.id)

                
            if product_variation in ex_var_list:
                index = ex_var_list.index(product_variation)
                item_id = id[index]
                item = CartItem.objects.get(product=product, id=item_id)
                item.quantity +=quantity
                item.save()
            else:
                item = CartItem.objects.create(product=product, quantity=quantity, cart=cart)  
                if len(product_variation)>0:
                    item.variations.clear()
                    item.variations.add(*product_variation)
                item.save()
            wishlist_item = WishlistItem.objects.filter(wishlist__wishlist_id=_wishlist_id(request), product_id=product_id).first()
            if wishlist_item:
                wishlist_item.delete()
        else:
            cart_item = CartItem.objects.create(
                product = product,
                quantity = quantity,
                cart = cart
            )
            if len(product_variation)>0:
                cart_item.variations.clear()
                cart_item.variations.add(*product_variation)
            cart_item.save()
            wishlist_item = WishlistItem.objects.filter(wishlist__wishlist_id=_wishlist_id(request), product_id=product_id).first()
            if wishlist_item:
                wishlist_item.delete()
        return redirect('cart')


@csrf_exempt
def decrement_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product,user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request)) 
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1 :
            cart_item.quantity -= 1
            cart_item.save()
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart')

def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        cart_item = CartItem.objects.get(user=request.user, product=product, id=cart_item_id)
    else:
        cart = Cart.objects.get(cart_id=_cart_id(request))
        cart_item = CartItem.objects.get(cart=cart, product=product, id=cart_item_id)
    cart_item.delete()
    return redirect('cart')


@csrf_exempt
def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax = 0 
        grand_total = 0
        cart = None
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')
        for cart_item in cart_items:
            if cart_item.product.is_sale:
                total += (cart_item.product.discounted_price * cart_item.quantity)
            else:
                total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax =  0.02 * total
        grand_total = total + tax

        #Coupon functionality
        if request.POST:
            if request.user.is_authenticated:
                coupon = request.POST['coupon']
                coupon_obj = Coupon.objects.filter(coupon_code = coupon)
                current_user = request.user
                if not coupon_obj.exists():
                    messages.error(request, 'Invalid Coupon.')
                    return redirect('cart')
                if request.user.coupon:
                    messages.info(request, 'Coupon already exists.')
                if grand_total <= coupon_obj[0].minimum_amount:
                    messages.error(request, f'Total amount should be above ${coupon_obj[0].minimum_amount}')
                    return redirect('cart')
                if coupon_obj[0].is_expired:
                    messages.error(request, 'Coupon expired.')
                    return redirect('cart')
                current_user.coupon=coupon_obj[0]
                current_user.save()
                messages.success(request, 'Coupon applied.')
                grand_total -= coupon_obj[0].discounted_price
            else:
                coupon = request.POST['coupon']
                coupon_obj = Coupon.objects.filter(coupon_code = coupon)
                if not coupon_obj.exists():
                    messages.error(request, 'Invalid Coupon.')

                    return redirect('cart')
                if cart.coupon:
                    messages.info(request, 'Coupon already exists.')
                
                if grand_total <= coupon_obj[0].minimum_amount:
                    messages.error(request, f'Total amount should be above ${coupon_obj[0].minimum_amount}')
                    return redirect('cart')
                
                if coupon_obj[0].is_expired:
                    messages.error(request, 'Coupon expired.')
                    return redirect('cart')

                cart.coupon = coupon_obj[0]
                cart.save()
                messages.success(request, 'Coupon applied.')
                grand_total -= coupon_obj[0].discounted_price


    except Cart.DoesNotExist:
        pass
    

    context = {
        'total':total,
        'quantity':quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total':grand_total,
        'cart':cart,
        
    }
    return render(request, 'shop/cart.html', context)

    
@csrf_exempt
def remove_coupon(request, cart_id):
    cart = Cart.objects.get(cart_id=cart_id)
    cart.coupon = None
    cart.save()
    messages.info(request, 'Coupon removed.')
    return redirect('cart')


@csrf_exempt
def remove_coupons(request):
    user = request.user
    user.coupon = None
    user.save()
    messages.info(request, 'Coupon removed.')
    return redirect('cart')


def search(request):
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        if keyword:
            products = Product.objects.order_by('-created_date').filter(Q(description__icontains=keyword) | Q(product_name__icontains=keyword))
            product_count = products.count()
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user)
    else:
        wishlist_items = WishlistItem.objects.filter(wishlist__wishlist_id = _wishlist_id(request))
    product_wishlist_map = {item.product_id: True for item in wishlist_items}
    context = {
        'products':products,
        'product_count':product_count,
        'product_wishlist_map':product_wishlist_map,
    }
    return render(request, 'shop/shop.html', context)


@csrf_exempt
@login_required(login_url='log_in')
def checkout(request, total=0, quantity=0, cart_items=None):

    try:
        tax = 0 
        grand_total = 0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True).order_by('id')
        for cart_item in cart_items:
            if cart_item.product.is_sale:
                total += (cart_item.product.discounted_price * cart_item.quantity)
            else:
                total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax =  0.02 * total
        grand_total = total + tax
        print(grand_total)
        if request.user.coupon and grand_total >= request.user.coupon.minimum_amount:
            print(request.user.coupon.minimum_amount)
            grand_total -= request.user.coupon.discounted_price
            print(grand_total)
    except Cart.DoesNotExist:
        pass

    active_shipping_address = ShippingAddress.objects.filter(status=True, user=request.user)
    inactive_shipping_address = ShippingAddress.objects.filter(status=False, user=request.user)
    existing_address_count = ShippingAddress.objects.filter(user=request.user).count()

    wallet=Wallet.objects.get(user=request.user)
    context = {
        'total':total,
        'quantity':quantity,
        'cart_items' : cart_items,
        'tax' : tax,
        'grand_total':grand_total,
        'wallet':wallet,
        'active_shipping_address': active_shipping_address,
        'inactive_shipping_address':inactive_shipping_address, 
        'existing_address_count':existing_address_count, 
    }
    return render(request, 'shop/checkout.html', context)


@csrf_exempt
@login_required(login_url='log_in')
def select_address_checkout(request, address_id):
    shipping_address = ShippingAddress.objects.get(id=address_id)
    shipping_address.status=True
    shipping_address.save()
    return redirect('checkout')

@login_required(login_url='log_in')
def delete_address_checkout(request, address_id):
    address = ShippingAddress.objects.get(id=address_id)
    address.delete()
    return redirect('checkout')

@login_required(login_url='log_in')
def edit_address_checkout(request, address_id):
    address = ShippingAddress.objects.get(id=address_id)
    if request.POST:
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            address= form.save(commit=False)
            address.user=request.user
            address.save()
            return redirect('checkout')
    else:
        form = ShippingAddressForm(instance=address)
    context ={'form':form}
    return render(request, 'home/edit_address.html', context)


@csrf_exempt
@login_required(login_url='log_in')
def add_address_checkout(request):
    if request.POST:
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address= form.save(commit=False)
            address.user=request.user
            address.save()
            return redirect('checkout')
    else:
        form = ShippingAddressForm()
    context ={'form':form}
    return render(request, 'home/add_address.html', context)


def _wishlist_id(request):
    wishlist = request.session.session_key
    if not wishlist:
        wishlist = request.session.create()
    return wishlist

def add_wishlist(request, product_id):
    current_user = request.user
    product = Product.objects.get(id=product_id) 

    #if user is authenticated
    if current_user.is_authenticated:

        is_wishlist_item_exists = WishlistItem.objects.filter(product=product, user=current_user).exists()
        if is_wishlist_item_exists:
            wishlist_item = WishlistItem.objects.filter(product=product, user=current_user)

        else:
            wishlist_item = WishlistItem.objects.create(
                product = product,
                user = current_user
            )
        return redirect('wishlist')

    else:

        try:
            wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        except Wishlist.DoesNotExist:
            wishlist = Wishlist.objects.create(
                wishlist_id = _wishlist_id(request)
            )
            wishlist.save()

        is_wishlist_item_exists = WishlistItem.objects.filter(product=product, wishlist=wishlist).exists()
        if is_wishlist_item_exists:
            wishlist_item = WishlistItem.objects.filter(product=product, wishlist=wishlist)


        else:
            wishlist_item = WishlistItem.objects.create(
                product = product,
                wishlist = wishlist
            )
        return redirect('wishlist')
    
    

@csrf_exempt
def wishlist(request, wishlist_items=None):
    try:
        if request.user.is_authenticated:
            wishlist_items = WishlistItem.objects.filter(user=request.user, is_active=True).order_by('id')
        else:
            wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
            wishlist_items = WishlistItem.objects.filter(wishlist=wishlist, is_active=True).order_by('id')

    except Wishlist.DoesNotExist:
        pass
    
    context = {
        'wishlist_items' : wishlist_items,
    }
    return render(request, 'shop/wishlist.html', context)

def remove_wishlist_item(request, product_id, wishlist_item_id):
    product = get_object_or_404(Product, id=product_id)
    if request.user.is_authenticated:
        wishlist_item = WishlistItem.objects.get(user=request.user, product=product, id=wishlist_item_id)
    else:
        wishlist = Wishlist.objects.get(wishlist_id=_wishlist_id(request))
        wishlist_item = WishlistItem.objects.get(wishlist=wishlist, product=product, id=wishlist_item_id)
    wishlist_item.delete()
    return redirect('wishlist')


@csrf_exempt
def get_stock_status(request):
    if request.method == 'GET' :
        variation_value = request.GET.get('variation_value')
        item_id = request.GET.get('item_id')

        try:
            item = WishlistItem.objects.get(id=item_id)
            product = item.product

            # Find the variation with the specified variation value for the product
            variation = Variation.objects.filter(product=product, variation_value=variation_value).first()

            if variation:
                # Check the stock status of the variation
                if variation.stock > 0:
                    stock_status = 'in_stock'
                else:
                    stock_status = 'out_of_stock'
                
                return JsonResponse({'stock_status': stock_status})

            # If variation is not found, return an error message
            return JsonResponse({'error': 'Variation not found'}, status=400)

        except WishlistItem.DoesNotExist:
            return JsonResponse({'error': 'Item not found'}, status=404)
    
    # If the request is not AJAX or not GET, return a 400 Bad Request
    return JsonResponse({'error': 'Invalid request'}, status=400)

@csrf_exempt
def check_stock(request):
    if request.method == 'GET':
        product_id = request.GET.get('product_id')
        variation_value = request.GET.get('variation_value')
        quantity = int(request.GET.get('quantity', 1))  

        try:
            variation = Variation.objects.get(product_id=product_id, variation_value=variation_value)

            if variation.stock >= quantity:
                stock_status = 'in_stock'
            else:
                stock_status = 'out_of_stock'
            return JsonResponse({'status': stock_status})
        except Variation.DoesNotExist:
            pass
    
    return JsonResponse({'status': 'error'})


# def check_stock_cart(request):
#     if request.method == 'POST':
#         product_id = request.POST.get('product_id')
#         variation_id = request.POST.get('variation_id')
#         quantity = int(request.POST.get('quantity'))

#         try:
#             variation = Variation.objects.get(id=variation_id, product_id=product_id)
#             if variation.stock >= quantity:
#                 return JsonResponse({'status': 'success', 'message': 'In stock'})
#             else:
#                 return JsonResponse({'status': 'error', 'message': 'Out of stock'})
#         except Variation.DoesNotExist:
#             return JsonResponse({'status': 'error', 'message': 'Variation not found'})
    
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'})