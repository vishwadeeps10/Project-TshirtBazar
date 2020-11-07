from django.contrib import admin
from store.models import Tshirt , Brand,Cart, Color ,IdealFor ,NeckType ,occasion ,Sleeve,sizevariant,Payments,Order_items,Orders
# Register your models here.

class sizevariantConfigration(admin.TabularInline):
    model = sizevariant

class TshirtConfigration(admin.ModelAdmin):
    inlines = [sizevariantConfigration]
    list_display=['name','discount']
    list_editable=['discount']

    
class CartConfigration(admin.ModelAdmin):
    model= Cart
    list_display=['quantity','sizevariant','tshirt','user']
    readonly_fields =('user','sizevariant','tshirt','quantity')
    def size(self ,obj):
        return obj.sizevariant.size
    def tshirt(self ,obj):
        return obj.sizevariant.tshirt.name


class OrderConfigration(admin.ModelAdmin):
    list_display=['user','shipping_address','phone','date','order_status','payment_method','total']

    readonly_fields =('user','shipping_address','phone','total','payment_method')
      
class PaymentConfigration(admin.ModelAdmin):

    list_display=['order','date','payment_id','payment_request_id','payment_status']



admin.site.register(Tshirt ,TshirtConfigration)
admin.site.register(Brand)
admin.site.register(Color)
admin.site.register(IdealFor)
admin.site.register(NeckType)
admin.site.register(occasion)
admin.site.register(Sleeve)
admin.site.register(Cart ,CartConfigration)

admin.site.register(Orders ,OrderConfigration)
admin.site.register(Payments, PaymentConfigration)
admin.site.register(Order_items)
