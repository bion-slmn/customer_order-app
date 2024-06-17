'''
Module defines view funtions for CRUD operation for customer and
order classes
'''
from .models import Customer, Order
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpRequest
from .serialisers import CustomerSerialiser
from django.shortcuts import get_object_or_404


class CustomerView(APIView):
    def get(self, request: HttpRequest) -> Response:
        """
        Retrieves customer information based on the provided
        customer_id if given,
        otherwise returns information for all customers.
        customer_id is passed as a query parameter

        Args:
            request: The HTTP request object.

        Returns:
            A Response object containing customer information
            or an error message.
        """
        customer_id = request.query_params.get('customer_id')
        if not customer_id:
            all_customers = Customer.objects.all()
            data = CustomerSerialiser(all_customers, many=True).data
            return Response(data)

        if customer := Customer.objects.filter(
                id=customer_id).values('name', 'id'):
            return Response(customer)
        return Response(f'No customer with id {customer_id}', 404)

    def post(self, request: HttpRequest,) -> Response:
        """
        Creates a new Customer object based on the data in the HTTP request.

        Args:
            request: The HTTP request object containing
            the data for the new Customer.

        Returns:
            A Response object with the serialized data of
              the new Customer or error messages.
        """
        serialiser = CustomerSerialiser(data=request.data)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data, status=201)
        return Response(serialiser.errors, status=400)

    def put(self, request: HttpRequest, customer_id: str) -> Response:
        """
        Updates the name of a specific Customer identified by customer_id
        with the new name provided in the request data.

        Args:
            request: The HTTP request object containing the new
            name for the Customer.
            customer_id: The ID of the Customer to update.

        Returns:
            A Response object with a success message if the name was updated,
            or an error message if no name was provided.
        """
        customer = get_object_or_404(Customer, id=customer_id)
        if name := request.data.get('name'):
            customer.name = name
            customer.save()
            return Response(f'New name {name}')
        return Response('No name passed', 400)

    def delete(self, request: HttpRequest, customer_id: str) -> Response:
        """
        Deletes a specific Customer identified by customer_id.

        Args:
            request: The HTTP request object.
            customer_id: The ID of the Customer to delete.

        Returns:
            A Response object with a success message indicating
            the deletion of the Customer.
        """
        customer = get_object_or_404(Customer, id=customer_id)
        name = customer.name
        customer.delete()
        return Response(f'Successfully  deleted {name.upper}')
