
'''
This module defines classes that will be mapped into
database tables
'''
from django.db import models
import uuid


class BaseModel(models.Model):
    """
    Base model class for other models to inherit common fields.
    """

    id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        primary_key=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Customer(BaseModel):
    """
    Represents a customer in the system.

    Args:
        name: The name of the customer.

    Returns:
        str: The name of the customer.
    """
    name = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.name


class Order(BaseModel):
    """
    Represents an order made by a customer.

    Args:
        customer: The customer who placed the order.
        item: The name of the item ordered.
        amount: The total amount of the item ordered.
    """
    customer = models.ForeignKey(
        Customer, on_delete=models.CASCADE, related_name='orders')
    item = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self) -> str:
        return f'{self.item} - {self.amount}'
