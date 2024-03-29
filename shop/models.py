from django.db import models
from home.models import Product, Variation
from user_auth.models import User, Coupon

# Create your models here.
class Cart(models.Model):
    cart_id = models.CharField(max_length=250, blank=True)
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    variations = models.ManyToManyField(Variation, blank=True)
    cart = models.ForeignKey(Cart, on_delete= models.CASCADE, null=True)
    quantity = models.IntegerField()
    is_active = models.BooleanField(default=True)

    def sub_total(self):
        if self.product.is_sale:
            return self.product.discounted_price * self.quantity 
        else:
            return self.product.price * self.quantity 

    def __unicaode__(self):
        return self.product
    
    
class Wishlist(models.Model):
    wishlist_id = models.CharField(max_length=250, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.wishlist_id
    

class WishlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete= models.CASCADE)
    wishlist = models.ForeignKey(Wishlist, on_delete= models.CASCADE, null=True)
    is_active = models.BooleanField(default=True)

    def __unicaode__(self):
        return self.product