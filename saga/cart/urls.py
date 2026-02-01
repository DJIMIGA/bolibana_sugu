from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'cart'  # Définir le namespace de l'application

urlpatterns = [
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('delete_cart/', views.delete_cart, name='delete_cart'),
    path('increase-quantity/<int:cartitem_id>/', views.increase_quantity, name='increase_quantity'),
    path('decrease-quantity/<int:cartitem_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('payment/online/', views.payment_online, name='payment_online'),
    path('payment/delivery/', views.payment_delivery, name='payment_delivery'),
    path('product-options/<int:product_id>/', views.get_product_options, name='get_product_options'),
    path('remove-item/<int:cartitem_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update-shipping/', views.update_shipping, name='update_shipping'),
    path('order-confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('order-detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('stripe/webhook/', views.stripe_webhook, name='stripe_webhook'),
    path('payment-success/', views.payment_success, name='payment_success'),
    path('order-success/<int:order_id>/', views.order_success, name='order_success'),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('payment-cancel/', views.payment_cancel, name='payment_cancel'),
    path('test-email/', views.test_email_configuration, name='test_email'),
    
    # URLs Orange Money
    path('orange-money/payment/', views.orange_money_payment, name='orange_money_payment'),
    path('orange-money/return/', views.orange_money_return, name='orange_money_return'),
    path('orange-money/cancel/', views.orange_money_cancel, name='orange_money_cancel'),
    path('orange-money/webhook/', views.orange_money_webhook, name='orange_money_webhook'),
]
