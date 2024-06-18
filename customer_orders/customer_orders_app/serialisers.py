'''
Defines serialiser that converts django objects to python objects
and vis vasa
'''
from .models import Customer, Order
from rest_framework import serializers


class BaseSerialiser(serializers.ModelSerializer):
    def create(self, validated_data):
        """
        Calls the create method of the superclass with 
        the provided validated data.

        Args:
            validated_data: The data to create the object with.

        Returns:
            The result of calling the create method of the superclass.
        """
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        """
        Updates the fields of an object instance with the provided
        validated data.

        Args:
            instance: The object instance to update.
            validated_data: A dictionary containing the data to
            update the object instance with.

        Returns:
            The updated object instance.
        """
        for key, value in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.save()
        return instance


class CustomerSerialiser(BaseSerialiser):
    """
    Serializes Customer objects to represent their ID and name fields.

    This serializer is read-only for id and includes the ID and name
    fields of a Customer.
    """
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'name']
    
class OrderSerialiser(BaseSerialiser):
    """
    Serializes Order objects to represent their ID, item,
    amount, and creation timestamp.

    Provides methods to create a new Order object
    and update an existing Order object.
    """
    id = serializers.UUIDField(read_only=True)
    created_at = serializers.DateTimeField(format="%B %d, %Y, %I:%M %p", read_only=True)
    customer = CustomerSerialiser(read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'item', 'amount', 'created_at', 'customer']

