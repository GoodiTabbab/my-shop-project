from rest_framework import serializers
from .models import User
import re
from .models import Favorite, Product, Store, Order, OrderItem
from .models import Cart

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'password', 'first_name', 'last_name', 'location', 'image', 'role']
        extra_kwargs = {
            'password': {'write_only': True},  # لكي لا يظهر الباسورد في الاستجابة
        }

    def validate_phone_number(self, value):
        if not re.match(r'^09[0-9]{8}$', value):
            raise serializers.ValidationError("Invalid phone number format.")
        return value


    def create(self, validated_data):
        # استدعاء الـ Manager الذي أنشأناه أعلاه
        return User.objects.create_user(**validated_data)
# serializers.py



class ProductSerializer(serializers.ModelSerializer):

    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = '__all__'

    def get_image(self, obj):
        request = self.context.get('request')

        if obj.image:

            if request:
                return request.build_absolute_uri(obj.image.url)

            return obj.image.url

        return None

class CartSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)

    class Meta:
        model = Cart
        fields = '__all__'

class FavoriteSerializer(serializers.ModelSerializer):

    product = ProductSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = '__all__'