from django.urls import path
from .views import CustomerView

urlpatterns = [
    # path for CRUD operations for customer
    path('get-customers/', CustomerView.as_view()),
    path('add-customer/', CustomerView.as_view()),
    path('update-customer/<str:customer_id>/', CustomerView.as_view()),
    path('delete-customer/<str:customer_id>/', CustomerView.as_view()),
]