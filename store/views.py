from django.shortcuts import render,HttpResponse,redirect
from store.forms.authforms import CustomerCreationForm,CustomerAuthForm
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate ,login as loginUser,logout
from store.models import Tshirt,sizevariant,Cart,Orders,Order_items,Payments,occasion,Brand,Color,IdealFor,NeckType,Sleeve
from store.forms.checkout_form import CheckForm
from django.contrib.auth.decorators import login_required
from instamojo_wrapper import Instamojo
from Tshop.settings import API_KEY ,AUTH_TOKEN
API = Instamojo(api_key=API_KEY, auth_token=AUTH_TOKEN, endpoint='https://test.instamojo.com/api/1.1/')




from django.db.models import Min

# Create your views here.

#Home
def home(request):
    query = request.GET
    
    tshirts=[]
    tshirts = Tshirt.objects.all()
    brand =query.get('brand')
    color = query.get('color')
    sleeve = query.get('sleeve')
    if brand != '' and brand is not None:
        tshirts = tshirts.filter(brand__slug=brand)
    if color != '' and color is not None:
        tshirts = tshirts.filter(color__slug=color)
    if sleeve != '' and sleeve is not None:
        tshirts = tshirts.filter(sleeve__slug=sleeve)

    brands =Brand.objects.all()
    sleeves =Sleeve.objects.all()   
    colors =Color.objects.all() 

    print(tshirts)

    context= {
        "tshirts":tshirts,
        "brands": brands,
        'colors': colors,
        'sleeves': sleeves,
       }
    return render(request ,template_name='store/home.html', context=context)

#cart
def cart(request):
    cart= request.session.get('cart')
    if cart is  None:
        cart=[]
    
    for c in cart:
        tshirt_id=c.get('tshirt')
        tshirt = Tshirt.objects.get(id=tshirt_id)
        c['size'] = sizevariant.objects.get(tshirt=tshirt_id, size = c['size'])
        c['tshirt']=tshirt
    return render(request ,template_name='store/cart.html',context={'cart':cart})

#login
def login(request):
    if (request.method) == 'GET':
        form = CustomerAuthForm()
        next_page = request.GET.get('next')
        if next_page is not None:
            request.session['next_page'] = next_page

        return render(request ,template_name='store/login.html', context={ 'form':form})


    else:
        form=CustomerAuthForm(data =request.POST)
        if form.is_valid():
            username =form.cleaned_data.get('username')
            password =form.cleaned_data.get('password')
            user = authenticate(username = username ,password=password)
            if user:
                loginUser(request,user)

                session_cart =request.session.get('cart')
                if session_cart is None:
                    session_cart=[]
                else:
                    for c in session_cart:
                        size = c.get('size')
                        tshirt_id = c.get('tshirt')
                        quantity = c.get('quantity')
                        cart_obj = Cart()
                        cart_obj.sizevariant = sizevariant.objects.get(size =size , tshirt = tshirt_id)
                        cart_obj.quantity = quantity
                        cart_obj.user = user
                        cart_obj.save()


                cart = Cart.objects.filter(user = user)
                session_cart = []
                for c in cart:
                    obj={
                        'size' : c.sizevariant.size,
                        'tshirt': c.sizevariant.tshirt.id,
                        'quantity': c.quantity
                    }
                    session_cart.append(obj)

                request.session['cart'] = session_cart
                next_page = request.session.get("next_page")
                if next_page is None:
                    next_page = 'homepage'
                return redirect(next_page)

        else:
            return render(request ,template_name='store/login.html', context={ 'form':form})



#order
@login_required(login_url = '/login')
def orders(request):
    user = request.user
    orders =Orders.objects.filter(user = user ).order_by('-date').exclude(order_status='PENDING')
    context = {
            "orders" : orders

    }
    return render(request ,template_name='store/orders.html', context=context)


#signup
def signup(request):

    if (request.method =='GET'):

        form = CustomerCreationForm()
        context ={
            "form":form}
        return render(request ,template_name='store/signup.html' ,context=context)
    else:
        form = CustomerCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.email = user.username
            user.save()
            user.first_name =user.username
            user.save() 

            return redirect('login')
        context ={
            "form":form}
        return render(request ,template_name='store/signup.html' ,context=context)

#logout
def signout(request):
    logout(request)
    return redirect('homepage')

def show_product(request , slug):
    tshirt = Tshirt.objects.get(slug=slug)
    size = request.GET.get('size')

    if size is None:
        size = tshirt.sizevariant_set.all().order_by('price').first()
    else:
        size = tshirt.sizevariant_set.get(size=size)
 
    size_price = size.price
    sell_price = size_price -(size_price*(tshirt.discount//100))

    context = {'tshirt' : tshirt , 'price':size_price , 'sell_price':sell_price ,'active_size':size}
    return render(request , template_name='store/product_details.html',context=context)

#product import in cart

def add_to_cart(request, slug , size):
    user=None
    if request.user.is_authenticated:
        user=request.user

    cart = request.session.get('cart')
    if cart is None:
        cart=[]

    tshirt = Tshirt.objects.get(slug=slug)
    add_cart_to_anom_user(cart, size ,tshirt)
    
    
        
    if user is not None:
        add_cart_to_database(user ,size ,tshirt)
       


    
        
    request.session['cart'] =cart
    return_url=request.GET.get('return_url')
    return redirect(return_url)

def add_cart_to_database(user ,size, tshirt):
    size =sizevariant.objects.get(size=size ,tshirt = tshirt)
    existing = Cart.objects.filter(user = user ,sizevariant =size)
    if len(existing) > 0:
        obj = existing[0]
        obj.quantity = obj.quantity+1
        obj.save()
    
    else:
        c =Cart()
        c.user=user
        c.sizevariant = size
        c.quantity = 1
        c.save()

def add_cart_to_anom_user(cart ,size ,tshirt):
    flag=True
    for cart_obj in cart:
        t_id=cart_obj.get('tshirt')
        size_short=cart_obj.get('size')
        if t_id == tshirt.id and size==size_short:
            flag=False
            cart_obj['quantity']+=1

    if flag:
        cart_obj={
            'tshirt': tshirt.id,
            'size':size,
            'quantity': 1

        }
        cart.append(cart_obj)
#utility function
def cal_total_payable_amount(cart):
    total = 0
    for c in cart:
        discount =c.get('tshirt').discount
        price = c.get('size').price
        sale_price =(price - ( price * ( discount // 100) ))
        total_of_single_product = sale_price * c.get('quantity')
        total = total + total_of_single_product
        
    return total

@login_required(login_url = '/login')
def checkout(request):
    #get request
    if request.method == 'GET':
        form =CheckForm()
        return render(request , template_name='store/checkout.html' ,context={'form' : form})
    else:
        #post request
        form = CheckForm(request.POST)
        user= None
        if request.user.is_authenticated:
            user = request.user
        if form.is_valid():
            #payment
            cart =request.session.get('cart')
            if cart is None:
                cart=[]
            for c in cart:
                size_str = c.get('size')
                tshirt_id = c.get('tshirt')
                size_obj = sizevariant.objects.get(size=size_str, tshirt=tshirt_id)
                c['size'] = size_obj
                c['tshirt'] = size_obj.tshirt

            shipping_address = form.cleaned_data.get('shipping_address')
            phone = form.cleaned_data.get('phone')
            payment_method = form.cleaned_data.get('payment_method')
            total = cal_total_payable_amount(cart)
            print(shipping_address, phone, payment_method, total)

            order = Orders()
            order.shipping_address = shipping_address
            order.phone = phone
            order.payment_method = payment_method
            order.total = total
            order.order_status = "PENDING"
            order.user = user
            order.save()

            for c in cart:
                OrderItem = Order_items()
                OrderItem.order = order
                size = c.get('size')
                tshirt = c.get('tshirt')
                OrderItem.price =(size.price -(size.price *(tshirt.discount / 100)))
                OrderItem.quantity = c.get('quantity')
                OrderItem.size = size
                OrderItem.tshirt = tshirt
                OrderItem.save()
            #payment
            response = API.payment_request_create(
                amount=order.total,
                purpose="Payment For Tshirts",
                send_email=False,
                buyer_name=f'{user.first_name} {user.last_name}',
                email=user.email,
                redirect_url="http://localhost:8000/validate_payment")

            payment_request_id = response['payment_request']['id']
            url = response['payment_request']['longurl']

            payment = Payments()
            payment.order = order
            payment.payment_request_id = payment_request_id
            payment.save()
            return redirect(url)
            
        else:
            return redirect('/checkout')

def validatePayment(request):
    user = None
    if request.user.is_authenticated:
        user =request.user
    payment_request_id = request.GET.get('payment_request_id')
    payment_id = request.GET.get('payment_id')
    print(payment_request_id,payment_id)
    response = API.payment_request_payment_status(payment_request_id, payment_id)
    status =response.get('payment_request').get('payment').get('status')
    
    if status != 'Failed':
        print('Payment Sucesss')
        try:
            payment = Payments.objects.get(payment_request_id = payment_request_id)
            payment.payment_id = payment_id
            payment.payment_status =status
            payment.save()

            order=payment.order
            order.order_status = 'PLACED'
            order.save()
            cart =[]
            request.session['cart'] = cart
            Cart.objects.filter(user= user).delete()
            return redirect(orders)
        except:
            return render(request , template_name='store/payment_failed.html')
        
    else:
        # show error 
        return render(request , template_name='store/payment_failed.html')

    
