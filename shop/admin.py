from django.contrib import admin
from .models import User, Store, Product, Order, OrderItem, Favorite, Cart

# تسجيل الموديلات لتظهر في لوحة التحكم
admin.site.register(User)
admin.site.register(Store)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Favorite)
admin.site.register(Cart)