'''
Module defines view funtions for CRUD operation for customer and
order classes
'''
from .models import Customer, Order
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpRequest
from .serialisers import CustomerSerialiser, OrderSerialiser
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView



class CustomerView(APIView):
    """
    Handles HTTP requests related to Customer objects.

    Includes methods for retrieving, creating, updating,
    and deleting Customer objects.
    """

    def get(self, request: HttpRequest) -> Response:
        """
        Retrieves customer information based on the provided
        customer_id if given,
        otherwise returns information for all customers.

        Args:
            request: The HTTP request object.

        Returns:
            A Response object containing customer information
            or an error message.
        """
        try:
            customer_id = request.query_params.get('customer_id')
            if not customer_id:
                all_customers = Customer.objects.all().values('id', 'name')
                return Response(all_customers)

            if customer := Customer.objects.filter(id=customer_id).first():
                customer_data = CustomerSerialiser(customer)
                return Response(customer_data.data)
            return Response(f'No customer with id {customer_id}', 404)
        except Exception as error:
            return Response(f'Error : {error}', 400)

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
        try:
            serialiser = CustomerSerialiser(data=request.data)
            if serialiser.is_valid():
                serialiser.save()
                return Response(serialiser.data, status=201)
            return Response(serialiser.errors, status=400)
        except Exception as error:
            return Response(f'Error : {error}', 400)

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
        try:
            customer = get_object_or_404(Customer, id=customer_id)
            if name := request.data.get('name'):
                customer.name = name
                customer.save()
                return Response(f'New name {name}')
            return Response('No name passed', 400)
        except Exception as error:
            return Response(f'Error : {error}', 400)

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
        try:
            customer = get_object_or_404(Customer, id=customer_id)
            name = customer.name
            customer.delete()
            return Response(f'Successfully  deleted {name.upper}')
        except Exception as error:
            return Response(f'Error : {error}', 400)

class OrderListView(ListAPIView):
    """
    Handles HTTP GET requests for listing Order objects with pagination.
    """
    queryset = Order.objects.all()
    serializer_class = OrderSerialiser


class OrderView(APIView):
    """
    Handles HTTP requests related to Order objects.

    Includes methods for retrieving, creating, updating,
    and deleting Order objects.
    """

    def get(self, request: HttpRequest) -> Response:
        """
        Retrieves order information based on the
        provided customer_id or order_id if given,
        otherwise returns information for all orders.

        Args:
            request: The HTTP request object.

        Returns:
            A Response object containing information of
            orders or an error message.
        """
        customer_id = request.query_params.get('customer_id')
        try:
            if order_id := request.query_params.get('order_id'):
                order = get_object_or_404(Order, id=order_id)
                order_data = OrderSerialiser(order).data
                return Response(order_data)
            
            if not customer_id:
                return Response("Customer_id or order_id must be passed", 400)
            
            customer = Customer.objects.prefetch_related(
                    'orders').filter(id=customer_id).first()

            if not customer:
               return Response(f'Customer with {customer_id} doesnt exist', 400)
 
            customer_orders = customer.orders.all()
            customer_orders_data = OrderSerialiser(customer_orders, many=True).data
            return Response(customer_orders_data)
            
        except Exception as error:
            return Response(f'Error : {error}', 400)

    def post(self, request: HttpRequest) -> Response:
        """
        Creates a new Order object based on the data in the HTTP request.

        Args:
            request: The HTTP request object containing the data
            for the new Order.

        Returns:
            A Response object with the serialized data of
              the new Order or error messages.
        """
        customer_id = request.data.get('customer_id')
        item = request.data.get('item')
        amount = request.data.get('amount')

        try:
            customer = get_object_or_404(Customer, id=customer_id)
            data = {'customer_id': customer_id, 'item': item, 'amount': amount}

            order = Order.objects.create(**data)
            return Response(f'order_id: {order.id} created', 201)
        except Exception as error:
            return Response(f'Error : {error}, 400')

    def put(self, request: HttpRequest, order_id: str) -> Response:
        """
        Updates an existing Order object identified by order_id
        with the data in the HTTP request.

        Args:
            request: The HTTP request object containing the
            updated data for the Order.
            order_id: The ID of the Order to update.

        Returns:
            A Response object with the serialized data
            of the updated Order or error messages.
        """
        try:
            order = get_object_or_404(Order, id=order_id)
            serialiser = OrderSerialiser(
                order, data=request.data, partial=True)
            if serialiser.is_valid():
                serialiser.save()
                return Response(serialiser.data)
            return Response(serialiser.errors, 400)
        except Exception as error:
            return Response(f'Error: {error}', 400)

    def delete(self, request: HttpRequest, order_id: str) -> Response:
        """
        Deletes a specific Order identified by order_id.

        Args:
            request: The HTTP request object.
            order_id: The ID of the Order to delete.

        Returns:
            A Response object with a success message
            indicating the deletion of the Order.
        """
        try:
            order = get_object_or_404(Order, id=order_id)
            order_name = str(order)
            order.delete()
            return Response(f'{order_name} Successfully deleted')
        except Exception as error:
            return Response(f'Error : {error}', 400)
