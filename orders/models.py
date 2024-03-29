from user_auth.models import User
from email.policy import default
from django.db import models
from home.models import Product, Variation
from datetime import timezone
from django.core.exceptions import ValidationError
from django.utils import timezone as tz
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return self.payment_id
    

class Order(models.Model):

    STATUS = (
        ('New','New'),
        ('Accepted','Accepted'),
        ('Completed','Completed'),
        ('Cancelled','Cancelled'),
    )

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20) 
    first_name = models.CharField(max_length=50) 
    last_name = models.CharField(max_length=50) 
    phone = models.CharField(max_length=15) 
    email = models.EmailField(max_length=50) 
    address_line_1 = models.CharField(max_length=50) 
    address_line_2 = models.CharField(max_length=50) 
    country = models.CharField(max_length=50) 
    state = models.CharField(max_length=50) 
    city = models.CharField(max_length=50) 
    pin_code = models.IntegerField()
    order_note = models.CharField(max_length=100, blank=True)
    order_total = models.DecimalField(max_digits=10, decimal_places=2)
    tax = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    payment_method=models.CharField(max_length=15) 
    ip = models.CharField(max_length=20, blank=True)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)        
    updated_at = models.DateTimeField(auto_now=True)


    def full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def full_address(self):
        return f'{self.address_line_1} {self.address_line_2}'

    def __str__(self):
        return self.first_name
    
@receiver(post_save, sender=Order)
def update_payment_status(sender, instance, **kwargs):
    if instance.status == 'Completed' and instance.payment:
        instance.payment.status = 'Completed'
        instance.payment.save()
    

class OrderProduct(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variation = models.ManyToManyField(Variation,blank=True)
    quantity = models.IntegerField()
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)        
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.product.product_name
     
    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    


class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    card_id = models.CharField(max_length=12, unique=True)
    balance = models.DecimalField(default=0, max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.user.username}'s Wallet"
    

class WalletTransaction(models.Model):
    TRANSACTION_TYPES = (
        ('debit', 'Debit'),
        ('credit', 'Credit'),
    )

    transaction_id = models.CharField(max_length=12, unique=True)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    order_reference = models.ForeignKey('Order', on_delete=models.SET_NULL, blank=True, null=True)
    updated_balance = models.DecimalField(max_digits=10, decimal_places=2) 
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.wallet.user.username}'s {self.get_transaction_type_display()} transaction of {self.amount}"
    

class Offer(models.Model):
    name = models.CharField(max_length=100)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateField()
    products = models.OneToOneField(Product, on_delete=models.SET_NULL, null=True, related_name='product')
    is_active= models.BooleanField(default=True)

    def __str__(self):
        return self.name
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.products:
            self.products.is_sale = True
            discount_amount = self.products.price * (self.discount_percentage / 100)
            self.products.discounted_price = self.products.price - discount_amount
            self.products.save()

    def clean(self):
        if self.valid_to is not None and self.valid_to < tz.now().date():
            raise ValidationError({'valid_to': "Valid to date must be in the future."})
        
        if self.valid_from is not None and self.valid_to is not None and self.valid_from > self.valid_to:
            raise ValidationError({'valid_from': "Valid from date must be before valid to date."})
        

@receiver(post_save, sender=Offer)
def update_product_on_offer_creation(sender, instance, created, **kwargs):
    if created:
        if instance.products:
            instance.products.is_sale = True
            discount_amount = instance.products.price * (instance.discount_percentage / 100)
            instance.products.discounted_price = instance.products.price - discount_amount
            instance.products.save()