from django.db import models
from users.models import User
from django.core.validators import MaxValueValidator, MinValueValidator 
from datetime import datetime
from datetime import timedelta
from PIL import Image

# Create your models here.
import uuid

class Category(models.Model):
    category_name=models.CharField(max_length=50)
    # category_code=models.IntegerField()

    def __str__(self):
        return self.category_name

class Subcategory(models.Model):
    subcategory_name=models.CharField(max_length=50)
    Category=models.ForeignKey(Category, on_delete=models.CASCADE)
    def __str__(self):
        return self.subcategory_name


class AttributeName(models.Model):
    a_name=models.CharField(max_length=50)
    def __str__(self):
        return self.a_name

class AttributeValue(models.Model):
    a_value=models.CharField(max_length=50)
    a_name=models.ForeignKey(AttributeName,on_delete=models.CASCADE)
    
    def __str__(self):
        return self.a_value 


class Products(models.Model):
    p_name=models.CharField(max_length=50,blank=False,null=False)
    brand=models.CharField(max_length=50,blank=False,null=False)
    warrenty=models.CharField(max_length=50,blank=False,null=False)
    p_category=models.ForeignKey(Category, on_delete=models.CASCADE)
    p_subcategory=models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    p_created=models.DateField(auto_now_add=datetime.now)
    # p_rate=models.ManyToManyField(Rates)
    price=models.IntegerField(validators=[MinValueValidator(1)])
    description=models.TextField()
    qty_in_packet=models.IntegerField()

    # deals_via_card=models.TextField()
    real_price=models.IntegerField(validators=[MinValueValidator(1)])
    percent_off=models.IntegerField(validators=[MaxValueValidator(100)])

    photo_1=models.ImageField(upload_to='products')
    photo_2=models.ImageField(upload_to='products')
    photo_3=models.ImageField(upload_to='products')
    photo_4=models.ImageField(upload_to='products',blank=True,null=True)
    photo_5=models.ImageField(upload_to='products',blank=True,null=True)
    photo_6=models.ImageField(upload_to='products',blank=True,null=True)

    total_qty=models.IntegerField(validators=[MinValueValidator(1)])
    left_qty=models.IntegerField(validators=[MinValueValidator(1)])
    on_alert_qty=models.IntegerField(validators=[MinValueValidator(1)])

    # free_delivery=models.BooleanField()
    delivery_fees=models.IntegerField(validators=[MinValueValidator(0)])
    
    def __str__(self):
        return self.p_name
    
    def save(self, *args, **kwargs):
        super(Products, self).save(*args, **kwargs)
        imag1 = Image.open(self.photo_1.path)
        if imag1.width > 400 or imag1.height> 300:
            output_size = (400, 300)
            imag1.thumbnail(output_size)
            imag1.save(self.photo_1.path)
        imag2 = Image.open(self.photo_2.path)
        if imag2.width > 400 or imag2.height> 300:
            output_size = (400, 300)
            imag2.thumbnail(output_size)
            imag2.save(self.photo_2.path)
        imag3 = Image.open(self.photo_3.path)
        if imag3.width > 400 or imag3.height> 300:
            output_size = (400, 300)
            imag3.thumbnail(output_size)
            imag3.save(self.photo_3.path)
        
        # imag4 = Image.open(self.photo_4.path)
        # if imag4.width > 400 or imag4.height> 300:
        #     output_size = (400, 300)
        #     imag4.thumbnail(output_size)
        #     imag4.save(self.photo_4.path)
        # imag5 = Image.open(self.photo_5.path)
        # if imag5.width > 400 or imag5.height> 300:
        #     output_size = (400, 300)
        #     imag5.thumbnail(output_size)
        #     imag5.save(self.photo_5.path)
        # imag6 = Image.open(self.photo_6.path)
        # if imag6.width > 400 or imag6.height> 300:
        #     output_size = (400, 300)
        #     imag6.thumbnail(output_size)
        #     imag6.save(self.photo_6.path)

class DealsViaCard(models.Model):
    deal_of=[
        ('paytm','Paytm'),
        ('paypal','paypal'),
        ('debit_credit','Debit Credit'),
    ]
    deals_name=models.CharField(max_length=200,blank=False)
    percent_off_on_deal=models.IntegerField(validators=[MaxValueValidator(100)])
    # new_price=models.IntegerField(validators=[MinValueValidator(1)])el
    deal_of=models.CharField(max_length=100,choices=deal_of)
    p_id=models.ForeignKey(Products,on_delete=models.CASCADE,blank=False,null=True)


class Rates(models.Model):
    comment=models.CharField(max_length=50)
    rate = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)])
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    p_id= models.ForeignKey(Products,on_delete=models.CASCADE,blank=False,null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'p_id'], 
                name='unique product rate'
            )
        ]

    def __str__(self):
        return str(self.rate)+" by "+str(self.user)

class ProductAttribute(models.Model):
    attribute_values=models.ManyToManyField(AttributeValue)
    p_id= models.OneToOneField(Products,on_delete=models.CASCADE)
    def __str__(self):
        return str(self.p_id)

class ProductChangePriceAttributes(models.Model):
    attribute_values=models.ManyToManyField(AttributeValue)
    p_id= models.ForeignKey(Products,on_delete=models.CASCADE)
    price=models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return str(self.p_id)+" "+str(self.id)

# class ProductChangePrices(models.Model):
#     product_id=models.ForeignKey(Products,on_delete=models.CASCADE)
#     price=models.IntegerField(validators=[MinValueValidator(1)])
#     product_attribute=models.ForeignKey(ProductAttribute,on_delete=models.CASCADE)

class Cart(models.Model):
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE)
    user_id=models.ForeignKey(User,on_delete=models.CASCADE)
    qty=models.IntegerField(validators=[MinValueValidator(0)])
    price=models.IntegerField(validators=[MinValueValidator(1)])
    # productvarient=models.ForeignKey(ProductChangePriceAttributes,on_delete=models.CASCADE)
    selected_product_varient=models.CharField(max_length=100)

    def __str__(self):
        return str(self.user_id)+"'s carts "+ 'for'+ str(self.product_id.p_name)

class Checkout(models.Model):
    
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    first_name=models.CharField(max_length=100)
    last_name=models.CharField(max_length=100)
    address1=models.TextField()
    address2=models.TextField(blank=True,null=True)
    country=models.CharField(max_length=100)
    state=models.CharField(max_length=100)
    city=models.CharField(max_length=100)
    zip=models.CharField(max_length=6)
    payment_type=models.CharField(max_length=50)

    def __str__(self):
        return str(self.user)+"'s Checkout "


class Orders(models.Model):
    
    orderstatus=[
        ('                                                                                  q','Order Not Paid'),
        ('order_confirm','Order Confirm'),
        ('order_cancel','Order Cancel'),
        ('order_delivering','Order Delivering'),
        ('order_shipped','Order Shipped'),
    ]
    orderid=models.CharField(max_length=50,default=uuid.uuid4)
    checkout=models.ForeignKey(Checkout,on_delete=models.CASCADE)
    order_status=models.CharField(max_length=100,choices=orderstatus,default='order_not_confirm')
    created_at=models.DateTimeField(auto_now_add=datetime.now)
    shipped_at=models.DateTimeField(blank=True,null=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    return_order_date=models.DateTimeField(blank=True,null=True)
    returned_order=models.BooleanField(default=False)
    payment_failed=models.BooleanField(default=True)
    amount=models.IntegerField(validators=[MinValueValidator(0)])

class OrderLines(models.Model):
    product_id=models.ForeignKey(Products,on_delete=models.CASCADE)
    qty=models.IntegerField(validators=[MinValueValidator(0)])
    price=models.IntegerField(validators=[MinValueValidator(1)])
    per_order_amount=models.IntegerField(validators=[MinValueValidator(1)])
    order_id=models.ForeignKey(Orders,on_delete=models.CASCADE)

# class ProductQuantityAlert(models.Model):
#     product_id=models.ForeignKey(Products,on_delete=models.CASCADE)
#     total_qty=models.IntegerField(validators=[MinValueValidator(1)])
#     left_qty=models.IntegerField(validators=[MinValueValidator(1)])
    
# class DeliveryChargesOnProduct(models.Model):
#     product_id=models.ForeignKey(Products,on_delete=models.CASCADE)
#     delivery_charge=models.IntegerField(validators=[MinValueValidator(0)])

class OtpModel(models.Model):
    otp_number=models.CharField(max_length=6)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    varified=models.BooleanField(default=False)
    times=models.IntegerField(default=1)
    
class Return_product(models.Model):
    order=models.ForeignKey(Orders,on_delete=models.CASCADE)
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    image_1=models.ImageField(upload_to='return_product',blank=True,null=True)
    image_2=models.ImageField(upload_to='return_product',blank=True,null=True)
    image_3=models.ImageField(upload_to='return_product',blank=True,null=True)
    reason=models.TextField()
    