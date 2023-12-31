from django.conf import settings
from django.db import models
from django.shortcuts import reverse
from django_countries.fields import CountryField

CATEGORY_CHOICES = (
    ('S', 'Shirt'),
    ('SW', 'Sport wear'),
    ('OW', 'Outwear')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null= True)
    category = models.CharField(choices = CATEGORY_CHOICES, max_length=2, default='S')
    label = models.CharField(choices = LABEL_CHOICES, max_length=1, default= 'P')
    slug = models.SlugField()
    description = models.TextField(default="This is sample product. Don't try to buy")
    image = models.ImageField(blank=True, null=True)

    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        # Lấy URL tuyệt đối của url có name='...', đằng sau là tham số truyền vào 
        # (vào views để biết tham số là gì, ngoài giá trị request mặc định)
        return reverse('core:product_detail', kwargs = {
            'slug': self.slug
        })
    
    def get_add_to_cart(self):
        return reverse("core:add-to-cart", kwargs={
            'slug':self.slug
        })
    
    def get_remove_from_cart(self):
        return reverse("core:remove-from-cart", kwargs={
            'slug':self.slug
        })

# Create your models here.
class OrderItem(models.Model):
    # Cột lấy giá trị từ id của class khác
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE, blank=True, null=True)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default = 1)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    
    def get_total_item_price(self):
        return self.quantity*self.item.price
    
    def get_total_discount_price(self):
        return self.quantity*self.item.discount_price
    
    def get_amount_saved(self):
        return (self.item.price-self.item.discount_price)*self.quantity

    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_item_price()
    
class Order(models.Model):

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length = 20)
    ordered = models.BooleanField(default=False)
    # Nếu muốn truy xuất ngược về bảng có lấy giá trị từ id của mình, dùng ManyToMany để dễ lấy,
    # Kiểu như mình là chủ, quản lý nhiều lính
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(null = True)
    billing_address = models.ForeignKey('BillingAddress', on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)

    '''
    1. Item was added to cart
    2. Adding a billing Address
    (Failed checkout)
    3. Payment
    (Preprocessing, processing, packaging)
    4. Being delivered
    5. Received
    6. Refunds
    '''

    # Hàm str này được overwrite lại hàm gốc, 
    # Quy định cách hiển thị đối tượng khi được gọi đến (Trên giao diện admin)
    def __str__(self):
        return self.user.username
    
    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_final_price()
        if self.coupon:
            total -= self.coupon.amount
        return total
    
class BillingAddress(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    apartment_address = models.CharField(max_length=100)
    country = CountryField(multiple=False, default='Vietnam')
    zip = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                             blank=True, null = True)
    amount = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username


class Coupon(models.Model):
    code = models.CharField(max_length=15)
    amount = models.IntegerField(default = 200)

    def __str__(self):
        return self.code
    
class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete = models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()

    def __str__(self):
        return f"{self.pk}"
