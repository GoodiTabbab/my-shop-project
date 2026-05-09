from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from django.shortcuts import render, get_object_or_404
import os
import time
import re

from .models import Cart, Product,Favorite, Store, Order, OrderItem
from .serializers import CartSerializer

from .serializers import UserSerializer, StoreSerializer, StoreWithProductsSerializer, ProductSerializer, OrderSerializer,OrderItemSerializer,FavoriteSerializer


# 1. Register
@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            "Response Message": "Signed Up Successfully",
            "User": serializer.data,
            "Token": str(refresh.access_token),
        }, status=status.HTTP_201_CREATED)
    return Response({"Errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

# 2. Login
@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    phone_number = request.data.get('phone_number')
    password = request.data.get('password')

    # التحقق من وجود المستخدم
    user = authenticate(username=phone_number, password=password)

    if user:
        refresh = RefreshToken.for_user(user)
        serializer = UserSerializer(user)
        return Response({
            "Response Message": f"{user.first_name} Signed In Successfully",
            "User": serializer.data,
            "Token": str(refresh.access_token)
        })
    return Response({"Response Message": "Wrong Password Or Phone Number"}, status=status.HTTP_400_BAD_REQUEST)

# 3. Personal Information (Update Profile)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def personal_information(request):
    user = request.user
    # partial=True تعني أننا سنحدث بعض الحقول فقط وليس كلها (مثل Patch)
    serializer = UserSerializer(user, data=request.data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            "Message": "Updated successfully",
            "User": serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 4. Profile Data (Me)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response({
        "Response Message": "Profile Data Received Successfully",
        "User": serializer.data
    })

# views.py



@api_view(['GET'])
@permission_classes([AllowAny])
def list_stores(request):
    """Display a listing of the stores"""
    stores = Store.objects.all()
    serializer = StoreSerializer(stores, many=True, context={'request': request})

    return Response({
        "message": "Stores retrieved successfully",
        "stores": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def store_products(request):
    """ Get products for a specific store by name."""
    store_name = request.query_params.get('name')

    if not store_name:
        return Response({
            "message": "Store name is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    store = get_object_or_404(Store, name=store_name)
    serializer = StoreWithProductsSerializer(store, context={'request': request})

    return Response({
        "message": f"Store {store_name} products retrieved successfully",
        "products": serializer.data['products']
    },)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_store(request):
    """Store a newly created store in storage."""
    required_fields = ['name', 'description', 'image', 'location']
    for field in required_fields:
        if field not in request.data:
            return Response({
                "Response Message": "Invalid Information",
                "Errors": {field: [f"{field} is required"]}
            }, status=status.HTTP_400_BAD_REQUEST)

    if 'image' not in request.FILES:
        return Response({
            "Response Message": "Invalid Information",
            "Errors": {"image": ["Image file is required"]}
        }, status=status.HTTP_400_BAD_REQUEST)

    image_file = request.FILES['image']
    allowed_extensions = ['jpeg', 'jpg', 'png', 'gif', 'svg']
    file_extension = image_file.name.split('.')[-1].lower()

    if file_extension not in allowed_extensions:
        return Response({
            "Response Message": "Invalid Information",
            "Errors": {"image": ["Image must be jpeg, png, jpg, gif, or svg"]}
        }, status=status.HTTP_400_BAD_REQUEST)

    location = request.data.get('location', '')

    if not re.match(r'^[a-zA-Z0-9\s,.-]{1,100}$', location):
        return Response({
            "Response Message": "Invalid Information",
            "Errors": {"location": ["Location format is invalid"]}
        }, status=status.HTTP_400_BAD_REQUEST)

    store_data = {
        'name': request.data['name'],
        'description': request.data['description'],
        'location': location
    }

    try:
        timestamp = int(time.time())
        original_filename = image_file.name
        filename = f"{timestamp}_{original_filename}"
        file_path = default_storage.save(f'stores/{filename}', ContentFile(image_file.read()))

        store = Store.objects.create(
            name=store_data['name'],
            description=store_data['description'],
            location=store_data['location'],
            image=file_path
        )

        return Response({
            "message": "Store added successfully",
            "Store": StoreSerializer(store, context={'request': request}).data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "Response Message": "Error creating store",
            "Errors": {"error": [str(e)]}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




@api_view(['GET'])
@permission_classes([AllowAny])
def retrieve_store(request, id):
    """Display the specified store."""
    store = get_object_or_404(Store, id=id)
    serializer = StoreSerializer(store, context={'request': request})

    return Response({
        "Response Message": "Store retrieved successfully",
        "Store": serializer.data
    }, status=status.HTTP_200_OK)



@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_store(request, id):
    """Update the specified store in storage."""
    store = get_object_or_404(Store, id=id)
    location = request.data.get('location')
    if location:
        import re
        if not re.match(r'^[a-zA-Z0-9\s,.-]{1,100}$', location):
            return Response({
                "Response Message": "Invalid Information",
                "Errors": {"location": ["Location format is invalid"]}
            }, status=status.HTTP_400_BAD_REQUEST)

    if 'image' in request.FILES:
        image_file = request.FILES['image']
        allowed_extensions = ['jpeg', 'jpg', 'png', 'gif', 'svg']
        file_extension = image_file.name.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            return Response({
                "Response Message": "Invalid Information",
                "Errors": {"image": ["Image must be jpeg, png, jpg, gif, or svg"]}
            }, status=status.HTTP_400_BAD_REQUEST)

        if store.image:
            try:
                if os.path.isfile(store.image.path):
                    os.remove(store.image.path)
            except:
                pass

        timestamp = int(time.time())
        original_filename = image_file.name
        filename = f"{timestamp}_{original_filename}"
        file_path = default_storage.save(f'stores/{filename}', ContentFile(image_file.read()))
        store.image = file_path

    if 'name' in request.data:
        store.name = request.data['name']
    if 'description' in request.data:
        store.description = request.data['description']
    if 'location' in request.data:
        store.location = request.data['location']

    store.save()

    return Response({
        "Response Message": "Store updated successfully",
        "Store": StoreSerializer(store, context={'request': request}).data
    }, status=status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_store(request, id):
    """Remove the specified store from storage."""
    store = get_object_or_404(Store, id=id)
    store.delete()

    return Response({
        "Message : ": "Deleted Successfully"
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def search_store(request):
    """Search for a store by name."""
    store_name = request.query_params.get('name')

    if not store_name:
        return Response({
            "Message : ": "Store name is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    store = Store.objects.filter(name=store_name).first()
    if not store:
        return Response({
            "Message : ": "Store Not Found"
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = StoreSerializer(store, context={'request': request})

    return Response({
        "Message : ": "Store Retrieved Successfully",
        "Store : ": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def list_products(request):
    """Display a listing of the products,index() method."""
    products = Product.objects.all()
    serializer = ProductSerializer(products, many=True, context={'request': request})

    return Response({
        "message": "Products retrieved successfully",
        "products": serializer.data
    }, status=status.HTTP_200_OK)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_product(request):
    """Store a newly created product in storage, store() method."""
    required_fields = ['name', 'description', 'quantity', 'price', 'image', 'brand', 'store_name']
    for field in required_fields:
        if field not in request.data:
            return Response({
                "Response Message": "Invalid Information",
                "Errors": {field: [f"{field} is required"]}
            }, status=status.HTTP_400_BAD_REQUEST)

    if 'image' not in request.FILES:
        return Response({
            "Response Message": "Invalid Information",
            "Errors": {"image": ["Image file is required"]}
        }, status=status.HTTP_400_BAD_REQUEST)

    image_file = request.FILES['image']
    allowed_extensions = ['jpeg', 'jpg', 'png', 'gif', 'svg']
    file_extension = image_file.name.split('.')[-1].lower()

    if file_extension not in allowed_extensions:
        return Response({
            "Response Message": "Invalid Information",
            "Errors": {"image": ["Image must be jpeg, png, jpg, gif, or svg"]}
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        quantity = int(request.data['quantity'])
        if quantity < 1:
            return Response({
                "Response Message": "Invalid Information",
                "Errors": {"quantity": ["Quantity must be at least 1"]}
            }, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({
            "Response Message": "Invalid Information",
            "Errors": {"quantity": ["Quantity must be an integer"]}
        }, status=status.HTTP_400_BAD_REQUEST)

    try:
        price = float(request.data['price'])
        if price < 0:
            return Response({
                "Response Message": "Invalid Information",
                "Errors": {"price": ["Price must be at least 0"]}
            }, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
        return Response({
            "Response Message": "Invalid Information",
            "Errors": {"price": ["Price must be a number"]}
        }, status=status.HTTP_400_BAD_REQUEST)

    store_name = request.data.get('store_name')
    store = get_object_or_404(Store, name=store_name)

    try:
        timestamp = int(time.time())
        original_filename = image_file.name
        filename = f"{timestamp}_{original_filename}"
        file_path = default_storage.save(f'products/{filename}', ContentFile(image_file.read()))

        product = Product.objects.create(
            name=request.data['name'],
            description=request.data['description'],
            brand=request.data['brand'],
            quantity=quantity,
            price=price,
            image=file_path
        )

        store.products.add(product)

        return Response({
            "Response Message": "Product added successfully",
            "Product": ProductSerializer(product, context={'request': request}).data
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({
            "Response Message": "Error creating product",
            "Errors": {"error": [str(e)]}
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([AllowAny])
def retrieve_product(request, id):
    """Display the specified product,show() method."""
    product = get_object_or_404(Product, id=id)
    serializer = ProductSerializer(product, context={'request': request})

    return Response({
        "Response Message": "Product retrieved successfully",
        "Product": serializer.data
    }, status=status.HTTP_200_OK)



@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_product(request, id):
    """Update the specified product in storage,update() method."""
    product = get_object_or_404(Product, id=id)

    if 'quantity' in request.data:
        try:
            quantity = int(request.data['quantity'])
            if quantity < 1:
                return Response({
                    "Response Message": "Invalid Information",
                    "Errors": {"quantity": ["Quantity must be at least 1"]}
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({
                "Response Message": "Invalid Information",
                "Errors": {"quantity": ["Quantity must be an integer"]}
            }, status=status.HTTP_400_BAD_REQUEST)

    if 'price' in request.data:
        try:
            price = float(request.data['price'])
            if price < 0:
                return Response({
                    "Response Message": "Invalid Information",
                    "Errors": {"price": ["Price must be at least 0"]}
                }, status=status.HTTP_400_BAD_REQUEST)
        except (ValueError, TypeError):
            return Response({
                "Response Message": "Invalid Information",
                "Errors": {"price": ["Price must be a number"]}
            }, status=status.HTTP_400_BAD_REQUEST)

    if 'image' in request.FILES:
        image_file = request.FILES['image']
        allowed_extensions = ['jpeg', 'jpg', 'png', 'gif', 'svg']
        file_extension = image_file.name.split('.')[-1].lower()

        if file_extension not in allowed_extensions:
            return Response({
                "Response Message": "Invalid Information",
                "Errors": {"image": ["Image must be jpeg, png, jpg, gif, or svg"]}
            }, status=status.HTTP_400_BAD_REQUEST)

        if product.image:
            try:
                if os.path.isfile(product.image.path):
                    os.remove(product.image.path)
            except:
                pass

        timestamp = int(time.time())
        original_filename = image_file.name
        filename = f"{timestamp}_{original_filename}"
        file_path = default_storage.save(f'products/{filename}', ContentFile(image_file.read()))
        product.image = file_path

    if 'name' in request.data:
        product.name = request.data['name']
    if 'description' in request.data:
        product.description = request.data['description']
    if 'brand' in request.data:
        product.brand = request.data['brand']
    if 'quantity' in request.data:
        product.quantity = int(request.data['quantity'])
    if 'price' in request.data:
        product.price = float(request.data['price'])

    product.save()

    return Response({
        "Response Message": "Product updated successfully",
        "Product": ProductSerializer(product, context={'request': request}).data
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([AllowAny])
def search_product(request):
    """Search for a product by name, search() method."""
    product_name = request.query_params.get('name')

    if not product_name:
        return Response({
            "Message : ": "Product name is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    product = Product.objects.filter(name=product_name).first()

    if not product:
        return Response({
            "Message : ": "Product Not Found"
        }, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, context={'request': request})

    return Response({
        "Message : ": "Product Retrieved Successfully",
        "Product : ": serializer.data
    }, status=status.HTTP_200_OK)




@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product(request, id):
    """Remove the specified product from storage, destroy() method."""
    product = get_object_or_404(Product, id=id)
    product.delete()

    return Response({
        "Message : ": "Deleted Successfully"
    }, status=status.HTTP_200_OK)



# =========================
# Get All Cart Items
# =========================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_index(request):

    carts = Cart.objects.filter(
        user=request.user
    ).select_related('product')

    serializer = CartSerializer(
        carts,
        many=True,
        context={'request': request}
    )

    return Response({
        "Cart": serializer.data,
        "Message": "Retrieved Successfully"
    })


# =========================
# Add Product To Cart
# =========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cart_store(request):

    name = request.data.get('name')
    quantity = int(request.data.get('quantity', 1))

    try:
        product = Product.objects.get(name=name)

    except Product.DoesNotExist:
        return Response({
            'message': 'Product not found'
        }, status=404)

    cart_item = Cart.objects.filter(
        user=request.user,
        product=product
    ).first()

    if cart_item:

        cart_item.quantity += quantity
        cart_item.price += product.price * quantity
        cart_item.save()

    else:

        Cart.objects.create(
            user=request.user,
            product=product,
            quantity=quantity,
            price=product.price * quantity
        )

    return Response({
        'message': 'Product added to cart'
    })


# =========================
# Delete Cart Item
# =========================

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def cart_destroy(request):

    product_id = request.data.get('product_id')

    cart = Cart.objects.filter(
        user=request.user,
        product_id=product_id
    ).first()

    if not cart:
        return Response({
            "message": "Cart item not found"
        }, status=404)

    cart.delete()

    return Response({
        "message": "Cart item deleted successfully"
    })


# =========================
# Increase Quantity
# =========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increase_cart(request):

    product_id = request.data.get('product_id')

    cart = Cart.objects.filter(
        user=request.user,
        product_id=product_id
    ).first()

    if not cart:
        return Response({
            "message": "Cart item not found"
        }, status=404)

    cart.quantity += 1
    cart.price += cart.product.price
    cart.save()

    return Response({
        "message": "Quantity increased",
        "cart": CartSerializer(cart).data
    })


# =========================
# Decrease Quantity
# =========================

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decrease_cart(request):

    product_id = request.data.get('product_id')

    cart = Cart.objects.filter(
        user=request.user,
        product_id=product_id
    ).first()

    if not cart:
        return Response({
            "message": "Cart item not found"
        }, status=404)

    if cart.quantity > 1:
        cart.quantity -= 1
        cart.price -= cart.product.price
        cart.save()

    else:
        cart.delete()

    return Response({
        "message": "Quantity decreased"
    })

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_product_favorite(request):

    product_id = request.data.get('product_id')

    if not product_id:
        return Response({
            "message": "product_id is required"
        }, status=400)

    try:
        product = Product.objects.get(id=product_id)

    except Product.DoesNotExist:
        return Response({
            "message": "Product not found"
        }, status=404)

    favorite_exists = Favorite.objects.filter(
        user=request.user,
        product=product
    ).exists()

    if favorite_exists:
        return Response({
            "message": "Already in favorites"
        }, status=400)

    Favorite.objects.create(
        user=request.user,
        product=product
    )

    return Response({
        "message": "Product added to favorites",
        "status": True
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_product_favorite(request):

    favorites = Favorite.objects.filter(
        user=request.user
    ).select_related('product')

    serializer = FavoriteSerializer(
        favorites,
        many=True,
        context={'request': request}
    )

    return Response({
        'data': serializer.data,
        'message': 'success message',
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_product_favorite(request):

    product_id = request.data.get('product_id')

    favorite = Favorite.objects.filter(
        user=request.user,
        product_id=product_id
    ).first()

    if not favorite:
        return Response({
            "message": "Favorite product not found",
            "status": False
        }, status=404)

    favorite.delete()

    return Response({
        "message": "Favorite product deleted successfully",
        "status": True
    })

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_user_orders(request):
    """Lis the user's orders. index1() method."""
    user = request.user
    orders = Order.objects.filter(user=user)
    serializer = OrderSerializer(orders, many=True, context={'request': request})

    return Response({
        "Message": "Orders Retrieved Successfully",
        "Order": serializer.data
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def order_details(request):
    """ Showing the order details with items and product images, details() method."""
    order_id = request.query_params.get('order_id')
    if not order_id:
        return Response({
            "Message : ": "Order ID is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, id=order_id)
    order_items = order.items.all()
    serializer = OrderItemSerializer(order_items, many=True, context={'request': request})

    return Response({
        "Items": serializer.data,
        "Message : ": "Retrieved Successfully"
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order(request):
    """Creating a new order from the user's cart. create() method."""
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    if not cart_items.exists():
        return Response({
            "message": "Cannot create an order with an empty cart."
        }, status=status.HTTP_400_BAD_REQUEST)
    total_cost = sum(item.price for item in cart_items)
    order_data = {
        'user': user,
        'cost': total_cost,
        'state': 'pending',
        'pay_status': request.data.get('pay_status', False),
        'location': request.data.get('location', '')
    }
    order = Order.objects.create(**order_data)
    for cart_item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            quantity=cart_item.quantity,
            price=cart_item.price
        )

    cart_items.delete()

    return Response({
        "Message": "Order Created Successfully",
        "Order": OrderSerializer(order, context={'request': request}).data
    }, status=status.HTTP_200_OK)


#######??????? what is the difference between this one and index() or list_orders_pending()?
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_pending_orders(request):
    """listing of pending orders (alternative endpoint),show() method"""
    orders = Order.objects.filter(state='pending')
    serializer = OrderSerializer(orders, many=True, context={'request': request})

    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_orders_pending(request):
    """to display a listing of pending orders, index() method."""
    orders = Order.objects.filter(state='pending')
    serializer = OrderSerializer(orders, many=True, context={'request': request})

    return Response({
        "Message": "Orders Retrieved Successfully",
        "Order": serializer.data
    }, status=status.HTTP_200_OK)


####################
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_order_status(request):
    """Update order status,update() method."""
    # This is a placeholder since the original PHP implementation had issues
    # In practice, this would update specific order statuses
    return Response({
        "Message : ": "The order is being delivered"
    }, status=status.HTTP_200_OK)




@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_order(request):
    """Delete an order by ID"""
    order_id = request.query_params.get('order_id')
    if not order_id:
        return Response({
            "Message": "Order ID is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, id=order_id)
    order.delete()

    return Response({
        "Message": "Orders deleted Successfully"
    }, status=status.HTTP_200_OK)



@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_order_shipped(request):
    """Update order state to 'shipped'"""
    order_id = request.data.get('order_id')
    if not order_id:
        return Response({
            "Message": "Order ID is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, id=order_id)
    order.state = 'shipped'
    order.save()

    return Response({
        "Message": "Orders Shipped Successfully",
        "Order": OrderSerializer(order, context={'request': request}).data
    }, status=status.HTTP_200_OK)



@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_order_delivered(request):
    """Update order state to 'delivered'"""
    order_id = request.data.get('order_id')
    if not order_id:
        return Response({
            "Message": "Order ID is required"
        }, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, id=order_id)
    order.state = 'delivered'
    order.save()

    return Response({
        "Message": "Orders Delivered Successfully",
        "Order": OrderSerializer(order, context={'request': request}).data
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_product_from_order(request):
    """Remove a product from an order."""
    order_id = request.data.get('order_id')
    product_name = request.data.get('product_name')

    if not order_id or not product_name:
        return Response({
            "message": "Order ID and Product name are required"
        }, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, id=order_id)
    product = get_object_or_404(Product, name=product_name)
    order_item = OrderItem.objects.filter(order=order, product=product).first()
    if not order_item:
        return Response({
            "message": "Product not found in the order."
        }, status=status.HTTP_404_NOT_FOUND)

    order.cost -= order_item.price * order_item.quantity
    order.save()
    order_item.delete()
    if not order.items.exists():
        order.delete()

    return Response({
        "message": "Product removed from the order successfully.",
        "order": OrderSerializer(order, context={'request': request}).data
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def increase_order_item(request):
    """Increase quantity of a product in an order,increase() method"""
    order_id = request.data.get('order_id')
    product_id = request.data.get('product_id')
    if not order_id or not product_id:
        return Response({
            "message": "Order ID and Product ID are required"
        }, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, id=order_id)
    product = get_object_or_404(Product, id=product_id)

    order_item = OrderItem.objects.filter(order=order, product=product).first()
    if not order_item:
        return Response({
            "message": "Product not found in the order."
        }, status=status.HTTP_404_NOT_FOUND)

    order_item.quantity += 1
    order_item.price += product.price
    order_item.save()
    order.cost += product.price
    order.save()

    return Response({
        "message": "Increased Successfully",
        "Order": OrderSerializer(order, context={'request': request}).data
    }, status=status.HTTP_200_OK)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decrease_order_item(request):
    """Decrease quantity of a product in an order, decrease() method"""
    order_id = request.data.get('order_id')
    product_id = request.data.get('product_id')

    if not order_id or not product_id:
        return Response({
            "message": "Order ID and Product ID are required"
        }, status=status.HTTP_400_BAD_REQUEST)

    order = get_object_or_404(Order, id=order_id)
    product = get_object_or_404(Product, id=product_id)

    order_item = OrderItem.objects.filter(order=order, product=product).first()
    if not order_item:
        return Response({
            "message": "Product not found in the order."
        }, status=status.HTTP_404_NOT_FOUND)

    if order_item.quantity > 1:
        order_item.quantity -= 1
        order_item.price -= product.price
        order_item.save()
        order.cost -= product.price
        order.save()

        return Response({
            "message": "Decreased Successfully",
            "Order": OrderSerializer(order, context={'request': request}).data
        }, status=status.HTTP_200_OK)
    else:
        order.cost -= product.price
        order.save()
        order_item.delete()

        return Response({
            "message": "Item removed from order",
            "Order": OrderSerializer(order, context={'request': request}).data
        }, status=status.HTTP_200_OK)








