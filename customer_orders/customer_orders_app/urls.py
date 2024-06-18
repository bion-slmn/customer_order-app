'''
Module defines routes for Customer and Order Views
'''
from django.urls import path
from .views import CustomerView, OrderView

urlpatterns = [
    # path for CRUD operations for customer
    path('get-customers/', CustomerView.as_view()),
    path('add-customer/', CustomerView.as_view()),
    path('update-customer/<str:customer_id>/', CustomerView.as_view()),
    path('delete-customer/<str:customer_id>/', CustomerView.as_view()),

    # paths to CRUD operations for order
    path('get-orders/', OrderView.as_view()),
    path('add-order/', OrderView.as_view()),
    path('update-order/<str:order_id>', OrderView.as_view()),
    path('delete-order/<str:order_id>', OrderView.as_view()),
]