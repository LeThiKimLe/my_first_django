from django.urls import path
from core import views

app_name= 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name= 'home_view'),
    path('product/<slug:slug>', views.ItemDetailView.as_view(), name='product_detail'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout_view'),
    path('add-to-cart/<slug:slug>/', views.add_to_cart, name = 'add-to-cart'),
    path('remove-from-cart/<slug:slug>/', views.remove_from_cart , name = 'remove-from-cart'),
    path('order-summary/', views.OrderSummaryView.as_view(), name='order-summary'),
    path('remove_single_item_from_cart/<slug>', views.remove_single_item_from_cart,
          name='remove_single_item_from_cart'),
    path('payment/<payment_option>', views.PaymentView.as_view(),name = 'payment'),
    path('create-payment-intent/', views.create_payment, name= 'create-payment-intent'),
    path('add-coupon/', views.AddCouponView.as_view(), name = 'add-coupon'),
    path('request-refund/', views.RefundView.as_view(), name = 'request-refund')
    
]