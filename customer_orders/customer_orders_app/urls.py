'''
Module defines routes for Customer and Order Views
'''
from django.urls import path
from .views import CustomerView, OrderView, CustomerListView, OrderListView

urlpatterns = [
    # path for CRUD operations for customer
    path('get-customers/', CustomerListView.as_view(), name='all_customers'),
    path('view-customer/<str:customer_id>', CustomerView.as_view(), name='view_customer_info'),
    path('add-customer/', CustomerView.as_view(), name='add-customer'),
    path('update-customer/<str:customer_id>/', CustomerView.as_view(), name="update-customer"),
    path('delete-customer/<str:customer_id>/', CustomerView.as_view(), name='delete-customer'),

    # paths to CRUD operations for order
    path('get-orders/', OrderListView.as_view(), name='all_orders'),
    path('view-order/', OrderView.as_view(), name='view_order'),
    path('add-order/', OrderView.as_view(), name='add-order'),
    path('update-order/<str:order_id>', OrderView.as_view(), name='update-order'),
]