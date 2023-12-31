from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = {
    ('S', 'Strike'),
    ('P', 'PayPal')
}

class CheckoutForm(forms.Form):

    street_address = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder' : '123 Man Thiện'
    }))
    apartment_address = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'placeholder' : 'Apartment or Suite'
    }))
    country = CountryField(blank_label='(select country)').formfield( widget=CountrySelectWidget( attrs={
        'class':'custom-select d-block w-100',
    }
    ))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'placeholder' : '70000'
    }))
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    save_info = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)


class CouponForm(forms.Form):
    code = forms.CharField(widget=forms.TextInput ({
        'class': 'form-control',
        'placeholder': 'Promo Code',
        'aria-label' : 'Promo code',
        'aria-describedby' : 'button-addon2'
    }))

class RefundForm(forms.Form):
    ref_code = forms.CharField()
    message = forms.CharField(widget=forms.Textarea(attrs = {
        'rows': 4
    }))
    email = forms.EmailField()