'''
Defines serialiser that converts django objects to python objects
and vis vasa
'''
from .models import Customer, Order
from rest_framework import serializers


class CustomerSerialiser(serializers.ModelSerializer):
    """
    Serializes Customer objects to represent their ID and name fields.

    This serializer is read-only for id and includes the ID and name
    fields of a Customer.
    """
    id = serializers.UUIDField(read_only=True)
    class Meta:
        model = Customer
        fields = ['id', 'name']

    def create(self, validated_data: dict) -> Customer:
        """
        Creates a new Customer object using the provided validated data.

        Args:
            validated_data: A dictionary containing the data to create
            the Customer object.

        Returns:
            The newly created Customer object.
        """
        return Customer.objects.create(**validated_data)
    
    def update(self, instance: Customer, validated_data:dict) -> Customer:
        """
        Updates the fields of a Customer instance with the
        provided validated data.

        Args:
            instance: The Customer instance to update.
            validated_data: A dictionary containing the data to
            update the Customer instance with.

        Returns:
            The updated Customer instance.
        """
        for key, value in validated_data.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.save()
        return instance
        
