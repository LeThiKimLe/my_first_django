# Generated by Django 4.2.2 on 2023-07-13 15:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_coupon_amount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='Coupon',
            new_name='coupon',
        ),
    ]
