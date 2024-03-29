from django.urls import path
from . import views

urlpatterns = [
    path('',views.index, name='home'),
    path('dashboard/main/', views.dashboard, name='dashboard'),
    path('dashboard/my-orders/', views.my_orders, name='my_orders'),
    path('dashboard/my-orders/order-detail/<int:order_id>', views.order_detail, name='order_detail'),
    path('dashboard/cancel-orders/<int:order_id>', views.cancel_orders, name='cancel_orders'),
    path('dashboard/change-password/', views.change_password, name='change_password'),
    path('dashboard/account-details/', views.update_account_details, name='update_account_details'),
    path('dashboard/wallet/', views.wallet, name='wallet'),
    path('dashboard/my-address/', views.my_address, name='my_address'),
    path('dashboard/add-address/', views.add_address, name='add_address'),
    path('dashboard/edit-address/<int:address_id>', views.edit_address, name='edit_address'),
    path('dashboard/select-address/<int:address_id>', views.select_address, name='select_address'),
    path('dashboard/delete-address/<int:address_id>', views.delete_address, name='delete_address'),
    path('about/',views.about, name='about'),
    path('faq/',views.faq, name='faq'),
    path('contact-us/',views.contact_us, name='contact_us'),

]
