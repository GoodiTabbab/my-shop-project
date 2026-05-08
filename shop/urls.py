from django.urls import path
from . import views
from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('me/', views.me, name='me'),
    path('personal-info/', views.personal_information, name='personal_info'),
    path('cart/', views.cart_index),
    path('cart/store/', views.cart_store),
    path('cart/delete/', views.cart_destroy),
    path('cart/increase/', views.increase_cart),
    path('cart/decrease/', views.decrease_cart),
    path('favorite/', views.get_product_favorite, name='favorite.list'),
    path('favorite/add/', views.add_product_favorite, name='favorite.add'),
    path('favorite/delete/', views.delete_product_favorite, name='favorite.delete'),
]