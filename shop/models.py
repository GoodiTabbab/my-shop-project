from django.db import models
from django.contrib.auth.models import AbstractUser

# 1. User Model
class User(AbstractUser):
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    phone_number = models.CharField(max_length=20, unique=True)
    image = models.ImageField(upload_to='users/', blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True, blank=True, null=True)
    role = models.CharField(max_length=50, default='user')
    x_and_y = models.CharField(max_length=255, blank=True, null=True)

    USERNAME_FIELD = 'phone_number' 
    REQUIRED_FIELDS = ['username', 'email']

# 2. Store Model
class Store(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='stores/')
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 3. Product Model
class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    brand = models.CharField(max_length=100)
    quantity = models.IntegerField()
    price = models.FloatField() # يقابل double
    image = models.ImageField(upload_to='products/')
    # علاقة Many-to-Many مع المتجر
    stores = models.ManyToManyField(Store, related_name='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 4. Favorite Model (One-to-Many مع المستخدم والمنتج)
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    created_at = models.DateTimeField(auto_now_add=True)

# 5. Cart Model
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='carts')
    quantity = models.IntegerField()
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 6. Order Model
class Order(models.Model):
    STATE_CHOICES = [
        ('pending', 'Pending'),
        ('processed', 'Processed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    cost = models.FloatField()
    state = models.CharField(max_length=20, choices=STATE_CHOICES, default='pending')
    location = models.CharField(max_length=255, blank=True, null=True)
    pay_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

# 7. Order Item Model
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='order_items')
    quantity = models.IntegerField()
    price = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)