# Generated by Django 3.1.7 on 2021-07-17 05:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0009_orders_returned_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='orders',
            name='payment_failed',
            field=models.BooleanField(default=True),
        ),
    ]