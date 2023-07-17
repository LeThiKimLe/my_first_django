from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render, redirect
from requests import request
from core.models import Item, OrderItem, Order, BillingAddress, Payment, Coupon, Refund
from rest_framework.reverse import reverse
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from core.forms import CheckoutForm, CouponForm, RefundForm
from django.core import serializers
import stripe, logging
import json
import os
from django.views.decorators.csrf import csrf_exempt
import random
import string
stripe.api_key = settings.STRIPE_SECRET_KEY


def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=20))

# Create your views here.
def item_list(request):
    context = {
        'items':  Item.objects.all(),
    }
    return render(request, "product_page.html", context)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user = self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'couponform' : CouponForm(),
                'order': order,
                'DISPLAY_COUPON_FORM': True
            }
            return render(self.request, "checkout_page.html", context)
        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")
            
    def post(self, *args, **kwargs):

        form = CheckoutForm(self.request.POST or None)

        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                street_address = form.cleaned_data.get('street_address')
                apartment_address = form.cleaned_data.get('apartment_address')
                country = form.cleaned_data.get('country')
                zip = form.cleaned_data.get('zip')
                # TODO: ADD FUNCTIONALITIES FOR THESE FIELDS
                # same_billing_address = form.cleaned_data.get('same_billing_address')
                # save_info = form.cleaned_data.get('save_info')
                payment_option = form.cleaned_data.get('payment_option')
                billing_address = BillingAddress(
                    user=self.request.user,
                    street_address = street_address,
                    apartment_address = apartment_address,
                    country = country,
                    zip = zip
                )
                billing_address.save()
                order.billing_address = billing_address
                order.save()
                messages.success(self.request,'Check out success')
                if payment_option == "S":
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == "P":
                    return redirect('core:payment', payment_option='paypal')
                else:
                # TODO: HANDLE DIRECT TO PAYMENT OPTION
                    messages.warning(self.request, "Invalid payment option")
                    return redirect('core:checkout_view')
            messages.warning(self.request, "Invalid payment option")
            return redirect('core:checkout_view')
                
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("core:order-summary")
        
class PaymentView(View):
    def get(self, *args, **kwarg):
        # order
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            context = {
                'order':order,
                'DISPLAY_COUPON_FORM': False
            }
            return render(self.request, 'payment_page.html', context)
        else:
            messages.error(self.request, "You have not add a billing address")
            return redirect("core:checkout_view")
        
    def post(self, *args, **kwargs):
        print("hi")
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total() * 100)
        try:
            charge = stripe.Charge.create(
            amount = amount,
            currency = "usd",
            source="tok_visa",
            description="My First Test Charge (created for API docs at https://www.stripe.com/docs/api)",
            )
            # create payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_total()
            payment.save()

            # assign the payment to the order

            order_items = order.items.all()
            order_items.update(ordered=True)
            for item in order_items:
                item.save()

            order.ordered = True
            order.payment = payment
            order.ref_code = create_ref_code()
            order.save()

            # redirect
            messages.success(self.request, "Your order was successfully!!")
            return redirect("/cart")

        except stripe.error.CardError as e:
            body = e.json_body
            err = body.get('error', {})
            messages.error(self.request, f" {err.get('message')}")
            return redirect("core:payment")

        except stripe.error.InvalidRequestError:
            
            messages.error(self.request, "Invalid Parameter")
            return redirect("core:payment")

        except stripe.error.AuthenticationError as e:
            messages.error(self.request, "Not authenticated")
            return redirect("core:payment")

        except stripe.error.APIConnectionError as e:
            messages.error(self.request, "Network Error")
            return redirect("core:payment")

        except stripe.error.StripeError as e:
            messages.error(self.request, "Something went wrong. You were not charged. Please try again")
            return redirect("core:payment")

        except Exception as e:
            messages.error(self.request, str(e) )
            return redirect("core:payment")

def home_view(request):

    context = {
        'items':  Item.objects.all()
    }
    return render(request, "home_page.html", context)

class HomeView(ListView):
    # Là một cách khác dùng khai báo một view hiển thị list object
    # Nhưng ở đây ko cần khai báo content
    # Chỉ cần khai báo model object
    # Trong file front end (html) dùng biến object_list để lấy list (mặc định)
    model = Item
    paginate_by = 2
    template_name = 'home_page.html'


class OrderSummaryView(LoginRequiredMixin,View):

    def get(self, *args, **kwargs):
        
        try:
            order = Order.objects.get(user=self.request.user, ordered = False)
            context = {
                'object': order
            }
            return render(self.request, 'account/order_summary.html', context)

        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")
        

class ItemDetailView(DetailView):
    # Trong file html, dùng biến object để lấy thông tin (mặc định)
    model = Item
    template_name = 'product_page.html'

@login_required
def add_to_cart(request, slug):
    # Get sẽ trả về object, nếu chỉ gọi get (Model.objects.get())
    # Nếu ko tìm thấy, nó sẽ ném ra lỗi, -> cần try catch -> mệt
    # Nên dùng get_object_or_404 để nếu mà nó ko tìm ra, thì báo lỗi 404 ra cho url luôn
    # Ko có hiện lỗi dừng chương trình lung tung

    ''' Kiểm tra xem item có hợp lệ không''' 
    item = get_object_or_404(Item, slug=slug)

    '''Kiểm tra xem món đồ này có trong giỏ hàng chưa'''
    '''Logic ở đây là coi xem user có từng order món này chưa'''
    '''Mặc định 1 người chỉ đang có 1 hoặc 0 có đơn hàng chưa order'''
    '''Chỉ tạo 1 lần cho một đơn hàng chưa order'''
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user = request.user,
        ordered=False
    )

    # Filter sẽ trả về một queryset, nên có thể dùng hàm exists() để
    # kiểm tra coi có dữ liệu hay ko
    # Dùng queryset như dùng với mảng 
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if item existed in cart
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item was updated to your cart")
            return redirect("core:order-summary") 
        else:
            order.items.add(order_item)
            messages.info(request, "This item was added to your cart")
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date=ordered_date)
        order.items.add(order_item)
        messages.info(request, "This item was added to your cart")

    return redirect("core:product_detail",
        slug=slug
    )

@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if item existed in cart
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user = request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart")
            return redirect('core:order-summary')

        else:
            # Khi người dùng ko có món này trong giỏ đồ
            messages.info(request, "This item was not in your cart")
            return redirect('core:product_detail', slug=slug)

    else:
        messages.info(request, "You do not have an active order")
        return redirect('core:product_detail', slug=slug)
  
    return redirect('core:product_detail', slug=slug)

@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if item existed in cart
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user = request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
            else:
                order.items.remove(order_item)
                order_item.delete()
            messages.info(request, "This item quantity was updated")
            return redirect('core:order-summary')
    else:
        messages.info(request, "You do not have an active order")
        return redirect('core:product_detail', slug=slug)
  
    return redirect('core:product_detail', slug=slug)

def calculate_order_amount(items):
    # Replace this constant with a calculation of the order's amount
    # Calculate the order total on the server to prevent
    # people from directly manipulating the amount on the client
    return 1400

@csrf_exempt
def create_payment(request):
    if request.user.is_authenticated:
        cart  = Order.objects.get(user=request.user)
        total = cart.get_total()
        stripe.api_key = 'sk_test_4eC39HqLyjWDarjtT1zdp7dc'

        if request.method=="POST":
            data = json.loads(request.body)
            # Create a PaymentIntent with the order amount and currency
            intent = stripe.PaymentIntent.create(
                amount=total,
                currency='usd',
                metadata={'integration_check': 'accept_a_payment'},
                )
            try:
                return JsonResponse({'clientSecret': 'hi'})
            except Exception as e:
                return JsonResponse({'error':str(e)},status= 403)


def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code = code)
        return coupon
    except ObjectDoesNotExist:
        messages.error(request,'This coupon does not existed')
        return redirect("core:checkout_view")


class AddCouponView(View):
    def post(self, *args, **kwargs):
        form = CouponForm(self.request.POST or None)
        if form.is_valid():
            try:
                code = form.cleaned_data.get('code')
                order = Order.objects.get(user = self.request.user, ordered=False)
                order.coupon = get_coupon(self.request, code)
                order.save()
                messages.success(self.request, "Successfully added coupon")
                return redirect("core:checkout_view")

            except ObjectDoesNotExist:
                messages.info(self.request, "You do not have an active order")
                return redirect("core:checkout_view")
       
class RefundView(View):

    def get(self, *args, **kwargs):
        form = RefundForm()
        context = {
            'form': form
        }
        return render(self.request, "request_refund.html", context)

    def post(self, *args, **kwargs):
        form = RefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # edit the order
            try:
                order = Order.objects.get(ref_code = ref_code)
                order.refund_requested = True
                order.save()
                # store the refund
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()

                messages.info(self.request, "This request was received")
                return redirect("core:request-refund")

            except ObjectDoesNotExist:
                messages.info(self.request, "This order does not existed")
                return redirect("core:request-refund")




