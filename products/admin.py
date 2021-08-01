from django.contrib import admin
from .models import (OtpModel, Products,
Rates,
Category,
Subcategory,
AttributeName,AttributeValue,ProductAttribute,
ProductChangePriceAttributes,
Cart,Checkout,Orders,OrderLines,DealsViaCard,Return_product)


class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ['p_id']
    fields = ['attribute_values', 'p_id']

class ProductAttributeInline(admin.TabularInline):
    model = ProductAttribute

class ProductChangePriceAttributesAdmin(admin.ModelAdmin):
    list_display = ['p_id']
    fields = ['attribute_values', 'p_id']

class ProductChangePriceAttributesInline(admin.TabularInline):
    model = ProductChangePriceAttributes


class DealsViaCardAdmin(admin.ModelAdmin):
    list_display = ['p_id']
    # fields = [,'new_price', 'percent_off_on_deal']

class DealsViaCardInline(admin.TabularInline):
    model = DealsViaCard


# class ProductQuantityAlertInline(admin.TabularInline):
#     model = ProductQuantityAlert


# class ProductQuantityAlertAdmin(admin.ModelAdmin):
 
#     list_display = ('product_id', 'total_qty','left_qty')



class ProductAdmin(admin.ModelAdmin):
    model = Products
    inlines = [
        ProductChangePriceAttributesInline,
        ProductAttributeInline,
        DealsViaCardInline,
        # ProductQuantityAlertInline,
    ]
    list_display = ('p_name', 'price','qty_in_packet')
    class Media:
    #this path may be any you want, 
    #just put it in your static folder
        js = ('js/admin_added_js1.js', )

admin.site.register(Products, ProductAdmin)
admin.site.register(ProductAttribute,ProductAttributeAdmin)
admin.site.register(ProductChangePriceAttributes,ProductChangePriceAttributesAdmin)
admin.site.register(DealsViaCard,DealsViaCardAdmin)
# admin.site.register(ProductQuantityAlert,ProductQuantityAlertAdmin)

# admin.site.register(Comments)
admin.site.register(Rates)
admin.site.register(Category)
admin.site.register(Subcategory)

admin.site.register(AttributeName)
admin.site.register(AttributeValue)

admin.site.register(Cart)

admin.site.register(OtpModel)

admin.site.register(Checkout)



class OrderLinesAdmin(admin.ModelAdmin):
    list_display = ['product_id','order_id','per_order_amount']
    fields = ['product_id', 'qty','price','per_order_amount','order_id']



class OrderLinesInline(admin.TabularInline):
    model = OrderLines


class OrdersAdmin(admin.ModelAdmin):
    model = Orders
    inlines = [
        OrderLinesInline,
    ]
    list_display = ('checkout', 'order_status','user','shipped_at','return_order_date','returned_order','payment_failed')
    fields = ['checkout', 'order_status','user','shipped_at','return_order_date','returned_order','payment_failed']


admin.site.register(Orders, OrdersAdmin)
admin.site.register(OrderLines,OrderLinesAdmin)

admin.site.register(Return_product)


