# Generated by Django 4.2.2 on 2023-07-14 15:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_order_being_delivered_order_received_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='ref_code',
            field=models.CharField(default=123, max_length=20),
            preserve_default=False,
        ),
    ]