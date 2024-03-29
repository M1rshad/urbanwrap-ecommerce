from email import message
from email.headerregistry import Address
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.password_validation import validate_password
from .models import Product, Category
from user_auth.models import ShippingAddress, User, UserProfile
from shop.models import WishlistItem
from shop.views import _wishlist_id
from admin_panel.forms import EditUserForm
from user_auth.forms import UserProfileForm, ShippingAddressForm
from orders.models import Order,Wallet, WalletTransaction
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.contrib import messages
from django.core.mail import send_mail
import uuid
# Create your views here.
def index(request):
    featured = Product.objects.all().filter(is_active=True).order_by('-priority','id')[:4] 
    sale = Product.objects.all().filter(is_active=True, is_sale=True).order_by('-id')[:4] 
    t_shirt_category = Category.objects.get(category_name='T shirt')
    recent_t_shirts = Product.objects.all().filter(category=t_shirt_category, is_active=True).order_by('-created_date')[:4]
    joggers_category = Category.objects.get(category_name='Joggers')
    recent_joggers = Product.objects.all().filter(category=joggers_category, is_active=True).order_by('-created_date')[:4]
    sweatshirts_category = Category.objects.get(category_name='Sweatshirts')
    recent_sweatshirts = Product.objects.all().filter(category=sweatshirts_category, is_active=True).order_by('-created_date')[:4]
    trousers_category = Category.objects.get(category_name='Trousers')
    recent_trousers = Product.objects.all().filter(category=trousers_category, is_active=True).order_by('-created_date')[:4]
    if request.user.is_authenticated:
        wishlist_items = WishlistItem.objects.filter(user=request.user)
    else:
        wishlist_items = WishlistItem.objects.filter(wishlist__wishlist_id = _wishlist_id(request))
    product_wishlist_map = {item.product_id: True for item in wishlist_items}
    context = {
        'featured':featured,
        'sale':sale,
        'recent_t_shirts':recent_t_shirts,
        'recent_joggers':recent_joggers,
        'recent_sweatshirts':recent_sweatshirts,
        'recent_trousers':recent_trousers,
        'product_wishlist_map':product_wishlist_map,
    }
    return render(request, 'home/index.html', context)


@csrf_exempt
@login_required(login_url='log_in')
def dashboard(request):
    orders = Order.objects.all().filter(user=request.user, is_ordered=True).order_by('-id')
    order_count = orders.count()
    user_profile = UserProfile.objects.get(user=request.user)
 
    context={
        'orders':orders,
        'order_count':order_count,
        'user_profile':user_profile,
    }
    return render(request, 'home/dashboard.html', context)


@login_required(login_url='log_in')
def my_orders(request):
    orders = Order.objects.all().filter(user=request.user, is_ordered=True).order_by('-id')
    context={
        'orders':orders,
    }
    return render(request, 'home/my_orders.html', context)

@login_required(login_url='log_in')
def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    context={
        'order':order,
    }
    return render(request, 'home/order_detail.html', context)

@login_required(login_url='log_in')
def cancel_orders(request, order_id):
    order_obj = Order.objects.get(id=order_id)
    order_obj.status = 'Cancelled'
    order_obj.save()
    if order_obj.payment.status == 'Completed':
        wallet = Wallet.objects.get(user=request.user)
        wallet.balance += order_obj.order_total
        wallet.save()
        wallet_transaction = WalletTransaction.objects.create(
            transaction_id=str(uuid.uuid4().int)[:12],
            wallet=wallet,
            amount=order_obj.order_total,
            transaction_type='credit',
            order_reference=order_obj,
            updated_balance=wallet.balance,
        )
    
    order_items = order_obj.orderproduct_set.all()
    for item in order_items:
        product_variation = item.variation.all()

        #update the stock
        product = Product.objects.get(id=item.product_id)
        product_variations = product.variant.all()
        quantity = item.quantity
        for variation in product_variations:
            for i in product_variation:
                if i==variation:
                    variation.stock += quantity
                    variation.save()


    #order confirmation email
    subject = 'Order cancellation'
    message = f"""
    Hi {request.user.username},
    Your order has been cancelled!
    Order Number = {order_obj.order_number} 
    """
    send_mail(subject, message, "abdullamirshadcl@gmail.com", [request.user.email,], fail_silently=False)
    
    return redirect('my_orders')


@login_required(login_url='log_in')
@csrf_exempt
def update_account_details(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if request.POST:
        user_form = EditUserForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'The profile has been updated')
            redirect('dashboard')
    else:
        user_form = EditUserForm(instance=request.user)
        profile_form = UserProfileForm(instance=user_profile)
    context={
        'user_form':user_form,
        'profile_form':profile_form,
        'user_profile': user_profile,
    }
    return render(request, 'home/account_details.html', context)


@login_required(login_url='log_in')
@csrf_exempt
def my_address(request):
    addresses = ShippingAddress.objects.filter(user=request.user).order_by('-id')
    context={
        'addresses':addresses,
    }
    return render(request, 'home/my_address.html',context)

@login_required(login_url='log_in')
@csrf_exempt
def add_address(request):
    
    max_address_allowed=3
    existing_address_count = ShippingAddress.objects.filter(user=request.user).count()

    if existing_address_count >= max_address_allowed:
        messages.error(request, 'Address limit exceeded')
        return redirect('my_address')
    
    form = ShippingAddressForm()
    if request.POST:
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            address= form.save(commit=False)
            address.user=request.user
            address.save()
            return redirect('my_address')
    else:
        form = ShippingAddressForm()
    context ={'form':form}
    return render(request, 'home/add_address.html', context)


@login_required(login_url='log_in')
@csrf_exempt
def edit_address(request, address_id):
    address = ShippingAddress.objects.get(id=address_id)
    if request.POST:
        form = ShippingAddressForm(request.POST, instance=address)
        if form.is_valid():
            address= form.save(commit=False)
            address.user=request.user
            address.save()
            return redirect('my_address')
    else:
        form = ShippingAddressForm(instance=address)
    context ={'form':form}
    return render(request, 'home/edit_address.html', context)


@login_required(login_url='log_in')
@csrf_exempt
def delete_address(request, address_id):
    address = ShippingAddress.objects.get(id=address_id)
    address.delete()
    return redirect('my_address')


@login_required(login_url='log_in')
@csrf_exempt
def select_address(request, address_id):
    shipping_address = ShippingAddress.objects.get(id=address_id)
    shipping_address.status=True
    shipping_address.save()
    return redirect('my_address')


@login_required(login_url='log_in')
@csrf_exempt
def change_password(request):
    if request.POST:
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_password = request.POST['confirm_password']

        # Check if new password matches confirm password
        if new_password != confirm_password:
            messages.error(request, 'New password and confirm password do not match.')
            return redirect('change_password')

        try:
            # Validate new password using Django's built-in validators
            validate_password(new_password, user=request.user)
        except ValidationError as error:
            messages.error(request, error)
            return redirect('change_password')

        # Authenticate user with current password
        user = authenticate(username=request.user.username, password=current_password)
        if user is None:
            messages.error(request, 'Current password is incorrect.')
            return redirect('change_password')

        # Update user's password
        user.set_password(new_password)
        user.save()
        messages.success(request, 'Password has been updated successfully.')
        return redirect('change_password')

    return render(request, 'home/change_password.html')


@csrf_exempt
@login_required(login_url='log_in')
def wallet(request):
    wallet = Wallet.objects.get(user=request.user)
    transaction_history = WalletTransaction.objects.filter(wallet=wallet).order_by('-id')
    context = {
        'wallet': wallet,
        'transaction_history':transaction_history,
    }
    return render(request, 'home/wallet.html', context)



def about(request):
    return render(request, 'home/about.html')


def contact_us(request):
    return render(request, 'home/contact_us.html')


def faq(request):
    return render(request, 'home/faq.html')