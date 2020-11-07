
from django.contrib import admin
from django.urls import path
from store.views import home,cart,login,orders,signup,signout,logout,show_product,add_to_cart,checkout
from store.views import validatePayment
from .import views


urlpatterns = [
    path('' ,home ,name='homepage'),
    path('cart' ,cart),
    path('login' ,login, name='login'),
    path('orders' ,orders, name='orders'),
    path('signup' ,signup),
    path('checkout' ,checkout),
    path('logout' ,signout),
    path('product/<str:slug>' ,show_product),
    path('addtocart/<str:slug>/<str:size>' ,add_to_cart),
    path('validate_payment' ,validatePayment),
    
]
