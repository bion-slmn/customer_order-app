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
from .decorator import handle_exceptions
from rest_framework.generics import ListAPIView
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from .sms_sender import send_sms
import django_rq


class CustomerListView(ListAPIView):
    """
    A view that returns a list of all customers. Pagination is added

    This view retrieves all customer objects from the database and serializes
    them using CustomerSerialiser.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Customer.objects.all()
    serializer_class = CustomerSerialiser


class OrderListView(ListAPIView):
    """
    A view that returns a list of all orders. With pagination

    This view retrieves all order objects
    from the database and serializes them using OrderSerialiser.
    """
    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Order.objects.all()
    serializer_class = OrderSerialiser


class CustomerView(APIView):
    """
    Handles HTTP requests related to Customer objects.

    Includes methods for retrieving, creating, updating,
    and deleting Customer objects.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAuthenticated]

    @handle_exceptions
    def get(self, request: HttpRequest, customer_id: str) -> Response:
        """
        Retrieves and returns data for a specific customer.

        Args:
            request: The HTTP request object.
            customer_id: The ID of the customer to retrieve.

        Returns:
            A Response object containing the serialized data
            of the specified customer include.
        """
        customer = get_object_or_404(
            Customer.objects.prefetch_related('orders'),
            id=customer_id)
        customer_info = {
            'Customer_details': CustomerSerialiser(customer).data,
            'orders': customer.orders.all().values(
                'created_at',
                'item',
                'amount')}
        return Response(customer_info)

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

    @handle_exceptions
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
        serialiser = CustomerSerialiser(
            customer, data=request.data, partial=True)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, 400)

    @handle_exceptions
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


class OrderView(APIView):
    """
    Handles HTTP requests related to Order objects.

    Includes methods for retrieving, creating, updating,
    and deleting Order objects.
    """
    # authentication_classes = [SessionAuthentication]
    # permission_classes = [IsAuthenticated]

    @handle_exceptions
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
        many = False

        if order_id := request.query_params.get('order_id'):
            orders = get_object_or_404(Order, id=order_id)

        elif customer_id := request.query_params.get('customer_id'):
            customer = get_object_or_404(
                Customer.objects.prefetch_related('orders'), id=customer_id)
            orders = customer.orders.all()
            many = True
        else:
            return Response('Please pass customer_id or order_id', 400)

        return Response(self.serialize_orders(orders, many))

    def serialize_orders(self, orders, many=False):
        return OrderSerialiser(orders, many=many).data

    @handle_exceptions
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

        customer = get_object_or_404(Customer, id=customer_id)
        data = {'customer_id': customer_id, 'item': item, 'amount': amount}

        order = Order.objects.create(**data)

        django_rq.enqueue(
            send_sms, customer.phone_number, {
                'item': item, 'amount': amount})
        return Response(OrderSerialiser(order).data, 201)

    @handle_exceptions
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

        order = get_object_or_404(Order, id=order_id)
        serialiser = OrderSerialiser(
            order, data=request.data, partial=True)
        if serialiser.is_valid():
            serialiser.save()
            return Response(serialiser.data)
        return Response(serialiser.errors, 400)

    @handle_exceptions
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

        order = get_object_or_404(Order, id=order_id)
        order_name = str(order)
        order.delete()
        return Response(f'{order_name} Successfully deleted')
