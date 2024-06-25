
'''
This module defines classes that will be mapped into
database tables
'''
from django.db import models
import uuid
from phonenumber_field.modelfields import PhoneNumberField


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

    class Meta:
        ordering = ['created_at']
        abstract = True


class Customer(BaseModel):
    """
    Represents a customer in the system.
    """
    name = models.CharField(max_length=50)
    phone_number = PhoneNumberField(unique=True)

    def save(self, *args, **kwargs):
        if not isinstance(self.name, str):
            raise ValueError("Name must be a string")
        if not self.phone_number.is_valid():
            raise ValueError("Valid phone should be +254703045843")
        super().save(*args, **kwargs)

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
    item = models.CharField(max_length=50, blank=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, blank=False)

    def __str__(self) -> str:
        return f'{self.item} - {self.amount}'
