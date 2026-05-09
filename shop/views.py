from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import UserSerializer
from .models import Favorite,Product
from .serializers import FavoriteSerializer
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

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Cart, Product
from .serializers import CartSerializer


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
    quantity_to_add = int(request.data.get('quantity', 1))

    try:
        product = Product.objects.get(name=name)
    except Product.DoesNotExist:
        return Response({'message': 'Product not found'}, status=404)

    cart_item = Cart.objects.filter(user=request.user, product=product).first()
    
    current_in_cart = cart_item.quantity if cart_item else 0
    total_requested_quantity = current_in_cart + quantity_to_add

    if total_requested_quantity > product.quantity:
        return Response({
            'message': f'Sorry, only {product.quantity} items available in stock. You already have {current_in_cart} in cart.',
            'available_stock': product.quantity
        }, status=status.HTTP_400_BAD_REQUEST)

    if cart_item:
        cart_item.quantity = total_requested_quantity
        cart_item.price += product.price * quantity_to_add
        cart_item.save()
    else:
        Cart.objects.create(
            user=request.user,
            product=product,
            quantity=quantity_to_add,
            price=product.price * quantity_to_add
        )

    return Response({'message': 'Product added to cart successfully'})


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

    # التحقق من الكمية المتوفرة
    if cart.quantity >= cart.product.quantity:
        return Response({
            "message": f"Sorry, only {cart.product.quantity} items available",
            "available_quantity": cart.product.quantity
        }, status=status.HTTP_400_BAD_REQUEST)

    # زيادة الكمية
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