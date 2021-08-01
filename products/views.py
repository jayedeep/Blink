from datetime import datetime
from django.http import HttpResponse
from django.shortcuts import redirect, render
from . models import Checkout, OrderLines, Orders, Products,Rates,AttributeName,Cart,OtpModel
from django.db.models import Avg,Count,Max,Min
from users.models import User
from django.urls import reverse
from .forms import CheckoutForm,ReturnProductForm
from django.http import JsonResponse
from django.db.models import Q
from django.contrib.auth.decorators import login_required

from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.template.loader import render_to_string

from datetime import timedelta

import smtplib
import random

from weasyprint import HTML
from . import Checksum
from django.views.decorators.csrf import csrf_exempt
import uuid
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from django.contrib import messages


MERCHANT_KEY = 'Z9uzcquqrxUuNErK'


def search(request):        
    if request.method == 'GET': # this will be GET now      
        product_search =  request.GET.get('search') # do some research what it does    
    subcategory="All"
    all_products=Products.objects.all().filter(Q(p_subcategory__subcategory_name__icontains=product_search)|Q(p_category__category_name__icontains=product_search) | Q(p_name__icontains=product_search)|Q(brand__icontains=product_search))
    minvalue=all_products.aggregate(Min('price'))
    maxvalue=all_products.aggregate(Max('price'))
    page = request.GET.get('page',1)   
    paginator = Paginator(all_products, 10)
    try:
        all_products = paginator.page(page)
    except PageNotAnInteger:
        all_products = paginator.page(1)
    except EmptyPage:
        all_products = paginator.page(paginator.num_pages)
    messages.info(request, f"Your Search For: {product_search}")

    return render(request, 'products/productlist.html',{'products':all_products,'result_for':subcategory,'minvalue':minvalue,'maxvalue':maxvalue})


def productlist(request,subcategory=None):
    page = request.GET.get('page',1)

    if subcategory == None:
        all_products=Products.objects.all().order_by('price')
        subcategory='All'
    else:
        all_products=Products.objects.all().filter(Q(p_subcategory__subcategory_name=subcategory)|Q(p_category__category_name=subcategory)).order_by('price')
    minvalue=all_products.aggregate(Min('price'))
    maxvalue=all_products.aggregate(Max('price'))

    paginator = Paginator(all_products, 10)
    try:
        all_products = paginator.page(page)
    except PageNotAnInteger:
        all_products = paginator.page(1)
    except EmptyPage:
        all_products = paginator.page(paginator.num_pages)

    # messages.info(request,")
    return render(request, 'products/productlist.html',{'products':all_products,'result_for':subcategory,'minvalue':minvalue,'maxvalue':maxvalue})

def productlist_sortby(request):
    page = request.GET.get('page',1)

    if request.is_ajax and request.method == "GET":
        sort_by=request.GET.get('sort_by',False)
        subcategory=request.GET.get('subcategory',False)
        all_products=Products.objects.all()
        if subcategory == 'All' or None:
            all_products=all_products.order_by('price')
            subcategory='All'
        else:
            all_products=all_products.filter(Q(p_subcategory__subcategory_name=subcategory)|Q(p_category__category_name=subcategory)).order_by('price')

        if sort_by != False:
            if sort_by == 'avg_rating':
                all_products=all_products.annotate(avg_rating=Avg('rates__rate')).order_by('-avg_rating')
            elif sort_by == 'popularity':
                all_products=all_products.annotate(rating_count=Count('rates__rate')).order_by('-rating_count')
            else:
                all_products=all_products.order_by(sort_by)
           

        else:
            minvalue=request.GET.get('minvalue',False)
            maxvalue=request.GET.get('maxvalue',False)
            all_products=all_products.filter(price__range=(minvalue, maxvalue))
        paginator = Paginator(all_products, 10)
        try:
            all_products = paginator.page(page)
        except PageNotAnInteger:
            all_products = paginator.page(1)
        except EmptyPage:
            all_products = paginator.page(paginator.num_pages)
  
                # print('all_products',all_products)
    return render(request, 'products/productlist_temp.html',{'products':all_products})

def productdetail(request,p_id):
    products=Products.objects.get(id=p_id)
    
    #product_attribute
    try:
        product_attr_list=list(products.productattribute.attribute_values.all().values())
    except Exception as e:
        product_attr_list=[]
    values=[i['a_value'] for i in product_attr_list]
    names=[AttributeName.objects.get(id=i['a_name_id']).a_name for i in product_attr_list]
    d={}
    for i in range(len(names)):
        if names[i] not in d.keys():
            d[names[i]]=[values[i]]
        else:
            vals=d.get(names[i])
            vals.append(values[i])
            d[names[i]]=vals
    li=[]
    if d !={}:
        for i in d.items():
            dd={}
            dd[i[0]]=",".join(i[1])
            li.append(dd)
    
    li1=[]
    if d !={}:
        for i in d.items():
            dd={}
            dd[i[0]]=i[1]
            if len(d[i[0]])>1:
                li1.append(dd)
    #avg_rate
    product_avg_rate=products.rates_set.aggregate(Avg('rate'))['rate__avg'] if products.rates_set.values().count() != 0 else 0
    rate_list=['orange' for i in range(int(product_avg_rate))]+['black' for i in range(5-int(product_avg_rate))]

    # every rates and every comments
    product_comments_rate=list(products.rates_set.all().values()) if list(products.rates_set.all().values()) !=[] else []
    for i in product_comments_rate:
        get_user=User.objects.get(id=i['user_id'])
        i['user_id']=get_user
        i['rate']=['orange' for i in range(int(i['rate']))]+['black' for i in range(5-int(i['rate']))]

    return render(request, 'products/productdetail.html',{'products':products,'prdct_attrs':li,'prdct_varient':li1,'avg_rate':rate_list,'product_comments_rate':product_comments_rate})

@login_required
def submit_rates_and_comments(request):
    if request.is_ajax and request.method == "POST":
        products=Products.objects.get(id=request.POST.get('p_id',False))
        if len(Rates.objects.filter(Q(user=request.user) & Q(p_id=products))) == 0:
            rates_table=Rates.objects.create(comment=request.POST.get('comments',False),rate=request.POST.get('userRating',False),user=request.user,p_id=products)
            rates_table.save()
            product_comments_rate=list(products.rates_set.all().filter(id=rates_table.id).values()) if list(products.rates_set.all().filter(id=rates_table.id).values()) !=[] else []

        else:
            # message for error
            product_comments_rate=[]

        for i in product_comments_rate:
            get_user=User.objects.get(id=i['user_id'])
            i['user_id']=get_user
            i['rate']=['orange' for i in range(int(i['rate']))]+['black' for i in range(5-int(i['rate']))]

        return render(request, 'products/get_more_comments.html', {'product_comments_rate': product_comments_rate})
       
    else:
        return JsonResponse({"error": "please enter valid"}, status=400)

@login_required
def productcart(request):
    # category=Category.objects.all()
    if request.method=="POST":
        requestdata=dict(request.POST)
        product=Products.objects.get(id=int(requestdata.get('p_id')[0]))
        x=product.productchangepriceattributes_set
        selected_varient=''
        for i in requestdata.get('slct'):
            a_name=i.split('-')[0]
            a_value=i.split('-')[1]
            selected_varient=selected_varient+a_value+","
            x=x.filter(attribute_values__a_value=a_value,attribute_values__a_name__a_name=a_name)
        if len(x)!=0:
            if len(Cart.objects.filter(Q(product_id=product) & Q(user_id=request.user) & Q(selected_product_varient=selected_varient)))==0:
                cart=Cart.objects.create(product_id=product,user_id=request.user,qty=1,selected_product_varient=selected_varient,price=x[0].price)
                messages.success(request, f"Your Cart is Ready")
            else:
                cart=Cart.objects.filter(Q(product_id=product) & Q(user_id=request.user) & Q(selected_product_varient=selected_varient))
                cart=cart.update(qty=cart[0].qty+1)
                messages.info(request, f"Your Cart is Updated")
        else:
            messages.error(request, f"product is unavailable with this varient")
        cart=Cart.objects.filter(user_id=request.user)
        return render(request,"products/cart.html",{'cart':cart})

    else:
        cart=Cart.objects.filter(user_id=request.user)
        return render(request,"products/cart.html",{'cart':cart})

def match_otp(request):
    otpmodel=OtpModel.objects.filter(user=request.user)
    if otpmodel.count() == 0:
        otpmodel=OtpModel.objects.create(user=request.user,otp_number=otp)
    else:
        otpmodel=otpmodel[0]
    if request.is_ajax and request.method == "POST":
        usr_otp=request.POST.get('otp_value')
        if usr_otp != False and usr_otp !='' and usr_otp==otpmodel.otp_number:
            otpmodel.varified=True
            otpmodel.times=1
            otpmodel.save()
            messages.success(request, f"Your Order is created! Please Check Your Orders")
            return redirect(order_created)
        else:
            # messages.warning(request, f"Please Try Again,Otp doesn't Matched")
            # print("both are different! try again!!!!!!!")
            return JsonResponse({"warning":"Otp doesn't Matched,Please Try Again,"})
    else:
        return JsonResponse({"response":'okay'})
    # return render(request,"products/otp_validation.html")

def order_failed(request):
    otpmodel=OtpModel.objects.filter(user=request.user)
    if otpmodel.count() == 0:
        otpmodel=OtpModel.objects.create(user=request.user,otp_number=otp)
    else:
        otpmodel=otpmodel[0]
    otpmodel.times=0
    otpmodel.save()
    return render(request,'products/order_failed.html')


def order_created(request):
    return render(request,'products/otp_validated.html')

def send_otp(request):
    otp = random.randint(100000, 999999)
    otp = str(otp)
    otpmodel=OtpModel.objects.filter(user=request.user)
    if otpmodel.count() == 0:
        otpmodel=OtpModel.objects.create(user=request.user,otp_number=otp)
    else:
        otpmodel=otpmodel[0]
        otpmodel.otp_number=otp
        
    otpmodel.varified=False
    otpmodel.save()
    try:
        # SUBJECT=f"Use OTP {otp} Dear {request.user.username}"
        # TEXT=f"""Use OTP {otp} to Confirm The Order. 
        # Don't share it with someone else."""
        # message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

        # s = smtplib.SMTP("smtp.gmail.com" , 587)  # 587 is a port number
        # s.starttls()
        # s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        # s.sendmail("<"+settings.EMAIL_HOST_USER+">" ,request.user.email , message)
        # s.quit()
        otpmodel.times+=1
        otpmodel.save()
        messages.success(request, f"OTP sent succesfully On {request.user.email}")
    except:
        messages.error(request, f"Please enter the valid email address OR check an internet connection")
    return render(request,"products/otp_validation.html",{'times':otpmodel.times})


# def varify_otp(request):
#     otpmodel=OtpModel.objects.filter(user=request.user)
#     if otpmodel.count() == 0:
#         otpmodel=OtpModel.objects.create(user=request.user,otp_number=otp)
#     else:
#         otpmodel=otpmodel[0]

#     usr_otp=request.POST.get('otp',False)

#     if usr_otp != False and usr_otp==otpmodel.otp_number:
#         otpmodel.varified=True
#         otpmodel.times=1
#         otpmodel.save()
#         messages.success(request, f"Your Order is created! Please Check Your Orders")
#         return render(request,"products/otp_validated.html")
#     else:
#         messages.warning(request, f"Please Try Again,Otp doesn't Matched")
        # print("both are different! try again!!!!!!!")
        # return redirect('otp_varify')

# def varify_otp(request):
#     otp = random.randint(100000, 999999)
#     otp = str(otp)
#     otpmodel=OtpModel.objects.filter(user=request.user)
#     if otpmodel.count() == 0:
#         otpmodel=OtpModel.objects.create(user=request.user,otp_number=otp)
#     else:
#         otpmodel=otpmodel[0]

#     if request.method == "GET":

#         otpmodel.otp_number=otp
#         otpmodel.varified=False
#         otpmodel.save()
#         if otpmodel.times < 3:
#             try:
        
#                 # SUBJECT=f"Use OTP {otp} Dear {request.user.username}"
#                 # TEXT=f"""Use OTP {otp} to Confirm The Order. 
#                 # Don't share it with someone else."""
#                 # message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

#                 # s = smtplib.SMTP("smtp.gmail.com" , 587)  # 587 is a port number
#                 # s.starttls()
#                 # s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
#                 # s.sendmail("<"+settings.EMAIL_HOST_USER+">" ,request.user.email , message)
#                 # s.quit()
#                 # print("third",otpmodel.otp_number)
#                 otpmodel.times+=1
#                 otpmodel.save()
#                 messages.success(request, f"OTP sent succesfully On {request.user.email}")

#             except:
#                 messages.error(request, f"Please enter the valid email address OR check an internet connection")
#             return render(request,"products/otp_validation.html",{'times':otpmodel.times})
#         else:
#             otpmodel.times=0
#             otpmodel.save()
#             return redirect('home')
            
#     else:
#         usr_otp=request.POST.get('otp',False)

#         if usr_otp != False and usr_otp==otpmodel.otp_number:
#             otpmodel.varified=True
#             otpmodel.save()
#             messages.success(request, f"Your Order is created! Please Check Your Orders")
#             return render(request,"products/otp_validated.html")
#         else:
#             messages.warning(request, f"Please Try Again,Otp doesn't Matched")
#             # print("both are different! try again!!!!!!!")
#             return redirect('otp_varify')

def return_policy(request):
    return render(request,"products/return_policy.html")
def terms_and_conditions(request):
    return render(request,"products/terms_and_conditions.html")

def about(request):
    return render(request,"products/about_us.html")

def contact(request):
    if request.method=="POST":
        name=request.POST.get('name')
        email=request.POST.get('email')
        user_msg=request.POST.get('message')
        
        try:
            SUBJECT=f"User {name}'s Query"
            TEXT=user_msg
            message = 'Subject: {}\n\n{}'.format(SUBJECT, TEXT)

            s = smtplib.SMTP("smtp.gmail.com" , 587)  # 587 is a port number
            s.starttls()
            s.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
            s.sendmail("<"+email+">" , settings.EMAIL_HOST_USER, message)
            # print("Message SuccessFully sent to admin")
            messages.success(request, "Message SuccessFully sent to admin,Thank You!")
            s.quit()
        except:
            messages.error(request, "Something Went Wrong! Please Try again, Thank You")
        return render(request,"products/contact.html")

    if request.method=="GET":
        return render(request,"products/contact.html")

    
    # return render(request,"products/contact.html")


@login_required
def productcartupdateremove(request):
    if request.is_ajax and request.method == "GET":
        # get the nick name from the client side.
        cart_id = request.GET.get("cart_id", None)
        sign=request.GET.get("sign", None)
        cart=Cart.objects.get(id=cart_id)

        if sign == 'plus':
            cart.qty=cart.qty+1
        else:
            cart.qty=cart.qty-1
        cart.save()

        if cart.qty<=0:
            cart.delete()
        cart=Cart.objects.filter(user_id=request.user)
        return render(request, 'products/cart_temp.html', {'cart': cart})

def createorder(request):
    cart=Cart.objects.filter(user_id=request.user)
    checkout=request.user.checkout_set.get()
    if len(cart)!=0:
        orders=Orders.objects.create(checkout=checkout,order_status='order_not_confirm',user=request.user,shipped_at=datetime.now()+timedelta(days=10),return_order_date=datetime.now()+timedelta(days=15),amount=0)
        if checkout.payment_type == 'paytm':
            amount=0
            for c in cart:
                # paytm=c.product_id.dealsviacard_set.filter(deal_of=checkout.payment_type)
                # if len(paytm)!=0:
                    # c.price=(c.price*paytm[0].percent_off_on_deal)//100
                OrderLines.objects.create(product_id=c.product_id,qty=c.qty,price=c.price,per_order_amount=c.qty*c.price,order_id=orders)
                amount+=c.qty*c.price
                product=Products.objects.get(id=c.product_id.id)
                product.left_qty=product.left_qty-c.qty
                product.save()
                c.delete()
            orders.amount=amount

            orders.save()
            param_dict = {

                'MID': 'iNqaaK84118094196288',
                'ORDER_ID': str(orders.orderid),
                'TXN_AMOUNT': str(orders.amount), #change after test
                'CUST_ID': request.user.email, # check users mail
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest',

                }
            param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)    
            return render(request, 'products/paytm.html', {'param_dict': param_dict})
        else:
            messages.error(request, "Something Went Wrong! Please Try again, Thank You")
            return redirect('checkout')
            
def update_order(request,orderid):
    order=Orders.objects.get(orderid=orderid)
    order.orderid=uuid.uuid4()
    order.save()
    param_dict = {
                'MID': 'iNqaaK84118094196288',
                'ORDER_ID': str(order.orderid),
                'TXN_AMOUNT': str(order.amount), #change after test
                'CUST_ID': request.user.email, # check users mail
                'INDUSTRY_TYPE_ID': 'Retail',
                'WEBSITE': 'WEBSTAGING',
                'CHANNEL_ID': 'WEB',
                'CALLBACK_URL':'http://127.0.0.1:8000/handlerequest',
                }

    param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(param_dict, MERCHANT_KEY)    
    return render(request, 'products/paytm.html', {'param_dict': param_dict})

@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    form = request.POST
    response_dict = {}
    checksum=''
    for i in form.keys():
        response_dict[i] = form[i]
        if i == 'CHECKSUMHASH':
            checksum = form[i]
    if checksum!='':
        verify = Checksum.verify_checksum(response_dict, MERCHANT_KEY, checksum)
        if verify:
            if response_dict['RESPCODE'] == '01':
                orders=Orders.objects.filter(orderid=response_dict['ORDERID'])
                orders.update(payment_failed=False,order_status='order_confirm')
                messages.success(request, "Your Order is Created And Paid by You, Thanks for Purchasing!")

                return redirect('orderviews',orderid=orders[0].orderid)
              
            else:
                messages.error(request, f"Order is Created ,Payment Faild Due to {response_dict['RESPMSG']}")

                return render(request, 'products/paymentstatus.html', {'response': response_dict['RESPMSG']})
        else:
            messages.error(request, "Varification is Faild Due to some reasons ,Please Try Again")
            return render(request, 'products/paymentstatus.html', {'response': "something went Wrong with varification of your account! Please Try Again"})


@login_required
def checkout_details(request):
    checkout=Checkout.objects.filter(user=request.user)
    
    checkoutform=CheckoutForm()

    if request.method=='POST':
        if len(checkout)==0:
            form = CheckoutForm(request.POST or None, request.FILES or None)
            user=request.user
            
            if form.is_valid():
                if form.cleaned_data['payment_type']=='case_on_delivery':
                    form = form.save(commit=False) # Return an object without saving to the DB
                    form.user = User.objects.get(pk=request.user.id) # Add an author field which will contain current user's id
                    form.save() # Save the final "real form" to the 
                    messages.success(request, "To Confirm Order ,Varify OTP")
                    return redirect('send_otp')
            # save the form data to model
                else:
                    return redirect("createorder")
                    # print("payment other types")
            else:
                messages.error(request, "Invalid Creadentials,Try Again")
                # print("invalid form")
            return render(request,'products/checkout.html',{'checkoutform':checkoutform})    

        else:
            checkout[0].first_name=request.POST.get('first_name')
            checkout[0].last_name=request.POST.get('last_name')
            checkout[0].address1=request.POST.get('address1')
            checkout[0].address2=request.POST.get('address2')
            checkout[0].country=request.POST.get('country')
            checkout[0].state=request.POST.get('state')
            checkout[0].city=request.POST.get('city')
            checkout[0].zip=request.POST.get('zip')
            checkout[0].payment_type=request.POST.get('payment_type')
            checkout[0].save()
            if request.POST.get('payment_type') == 'case_on_delivery':
                checkout[0].save()
                checkoutform=CheckoutForm(instance=checkout[0])
                messages.success(request, "To Confirm Order ,Varify OTP")
                return redirect('send_otp')    
            else:
                messages.warning(request, "Please Try Again, Something Went Wrong!")
                # messages.info(request, "Updated Form With Your New Changes")
                return redirect("createorder")
    else:
        try:
            checkoutform=CheckoutForm(instance=checkout[0])
        except Exception as e:
            checkoutform=CheckoutForm()
        messages.info(request, "Please Add Your Correct Shipping Address to Delivery Product")
        return render(request,'products/checkout.html',{'checkoutform':checkoutform})


@login_required
def userorders(request,order_by=None):
    page = request.GET.get('page',1)
    # category=Category.objects.all()
    order_not_confirms=Orders.objects.filter(user=request.user,order_status='order_not_confirm').count()
    order_confirms=Orders.objects.filter(user=request.user,order_status='order_confirm').count()
    order_cancels=Orders.objects.filter(user=request.user,order_status='order_cancel').count()
    order_deliverings=Orders.objects.filter(user=request.user,order_status='order_delivering').count()
    order_shippeds=Orders.objects.filter(user=request.user,order_status='order_shipped').count()
    
    if order_by == None:
        allorders=Orders.objects.filter(user=request.user)
    else:
        allorders=Orders.objects.filter(user=request.user).filter(order_status=order_by)
    paginator = Paginator(allorders, 5)
    try:
        allorders = paginator.page(page)
    except PageNotAnInteger:
        allorders = paginator.page(1)
    except EmptyPage:
        allorders = paginator.page(paginator.num_pages)
    return render(request,'products/allorders.html',{'allorder':allorders,'order_not_confirms':order_not_confirms,'order_confirms':order_confirms,'order_cancels':order_cancels,'order_deliverings':order_deliverings,'order_shippeds':order_shippeds})

@login_required
def orderviews(request,orderid):
    # category=Category.objects.all()
    order=Orders.objects.get(orderid=orderid)
    orderlines=OrderLines.objects.filter(order_id=order.id)
    today=datetime.now()
    return render(request,'products/order_views.html',{'today':today,'order':order,'orderlines':orderlines})

@login_required
def cancelorder(request,orderid):
    order=Orders.objects.filter(orderid=orderid)
    order.update(order_status='order_cancel')
    messages.error(request, "Your Order is Canceled Successfully!")
    return redirect('userorders')

@login_required
def html_to_pdf_view(request,orderid):
    order=Orders.objects.get(orderid=orderid)
    orderlines=OrderLines.objects.filter(order_id=order.id)
    html_string = render_to_string('products/pdf_template.html', {'order':order,'orderlines':orderlines })

    html = HTML(string=html_string)
    html.write_pdf(target='/tmp/receipt.pdf')

    fs = FileSystemStorage('/tmp')
    with fs.open('receipt.pdf') as pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="receipt.pdf"'
        return response

    return redirect('orderviews',orderid=orderid)

@login_required
def return_product(request,orderid):
    order=Orders.objects.get(orderid=orderid)
    
    if request.method=="POST":
        
        form=ReturnProductForm(request.POST or None, request.FILES or None)
        if form.is_valid():
           
            # orderid=form.cleaned_data.get("orderid")
            
            form = form.save(commit=False)
            form.order=order
            form.user=request.user
            form.save()
            order.returned_order=True
            order.save()
            messages.success(request, "Thanks For Your Support,Shortly We will reach out at you")

            return redirect('orderviews',orderid=orderid)
        else:
            messages.warning(request, "Something Wrong went With Credentials,Please Try Again")
            form=ReturnProductForm()
           
            return render(request,'products/return_product_form.html',{'form':form,'orderid':orderid})

    else:
        form=ReturnProductForm()
        return render(request,'products/return_product_form.html',{'form':form,'orderid':orderid})
