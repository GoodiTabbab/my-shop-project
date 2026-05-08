from django.urls import path
from . import views

urlpatterns = [
    # Store endpoints
    path('stores/', views.list_stores, name='list_stores'),
    path('stores/products/', views.store_products, name='store_products'),
    path('stores/', views.create_store, name='create_store'),
    path('stores/<int:id>/', views.retrieve_store, name='retrieve_store'),
    path('stores/<int:id>/update/', views.update_store, name='update_store'),
    path('stores/<int:id>/delete/', views.delete_store, name='delete_store'),
    path('stores/search/', views.search_store, name='search_store'),
    
    # Product endpoints
    path('products/', views.list_products, name='list_products'),
    path('products/', views.create_product, name='create_product'),
    path('products/<int:id>/', views.retrieve_product, name='retrieve_product'),
    path('products/<int:id>/update/', views.update_product, name='update_product'),
    path('products/<int:id>/delete/', views.delete_product, name='delete_product'),
    path('products/search/', views.search_product, name='search_product'),
    
    # Order endpoints
    path('orders/pending/', views.list_orders_pending, name='list_orders_pending'),
    path('orders/user/', views.list_user_orders, name='list_user_orders'),
    path('orders/details/', views.order_details, name='order_details'),
    path('orders/', views.create_order, name='create_order'),
    path('orders/pending/list/', views.list_pending_orders, name='list_pending_orders'),
    path('orders/update/', views.update_order_status, name='update_order_status'),
    path('orders/delete/', views.delete_order, name='delete_order'),
    path('orders/shipped/', views.update_order_shipped, name='update_order_shipped'),
    path('orders/delivered/', views.update_order_delivered, name='update_order_delivered'),
    path('orders/remove-product/', views.remove_product_from_order, name='remove_product_from_order'),
    path('orders/increase/', views.increase_order_item, name='increase_order_item'),
    path('orders/decrease/', views.decrease_order_item, name='decrease_order_item'),
]