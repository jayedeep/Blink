from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from .models import OtpModel,Orders,OrderLines,Cart,Products
from datetime import datetime
from datetime import timedelta

@receiver(post_save, sender=OtpModel) 
def create_otp(sender, instance, created, **kwargs):
    print(instance.times,"instance of otp>>>>>>>>>>>>>")
    if instance.varified == True:
    
        cart=Cart.objects.filter(user_id=instance.user)
        checkout=instance.user.checkout_set.get()

        if len(cart)!=0:
            orders=Orders.objects.create(checkout=checkout,order_status='order_confirm',user=instance.user,shipped_at=datetime.now()+timedelta(days=10),return_order_date=datetime.now()+timedelta(days=15),amount=0)
            amount=0
            for c in cart:
                if checkout.payment_type == 'case_on_delivery':
                    OrderLines.objects.create(product_id=c.product_id,qty=c.qty,price=c.price,per_order_amount=c.qty*c.price,order_id=orders)
                    amount+=c.qty*c.price
            orders.amount=amount
            orders.payment_failed=False
            orders.save()
            product=Products.objects.get(id=c.product_id.id)
            product.left_qty=product.left_qty-c.qty
            product.save()
            c.delete()
            instance.times=0
            # Profile.objects.create(user=instance)
