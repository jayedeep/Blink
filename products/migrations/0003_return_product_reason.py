# Generated by Django 3.1.7 on 2021-07-14 15:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_remove_return_product_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='return_product',
            name='reason',
            field=models.TextField(default=1),
            preserve_default=False,
        ),
    ]