# Generated by Django 4.2.2 on 2023-06-28 16:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_item_discount_price'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='description',
            field=models.TextField(default="This is sample product. Don't try to buy"),
        ),
    ]
