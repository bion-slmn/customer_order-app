from django.test import TestCase
from rest_framework.serializers import ValidationError
from customer_orders_app.models import Customer, Order
from customer_orders_app.serialisers import CustomerSerialiser, OrderSerialiser
import uuid
from django.db.utils import IntegrityError


class CustomerSerialiserTests(TestCase):

    def setUp(self):
        self.customer_data = {
            'name': 'John Doe',
            'phone_number': '+254703045843'
        }
        self.customer = Customer.objects.create(**self.customer_data)

    def test_serialization(self):
        """
        Test that CustomerSerialiser serializes a Customer instance correctly.
        """
        serializer = CustomerSerialiser(self.customer)
        expected_data = {
            'id': str(self.customer.id),
            'name': 'John Doe',
            'phone_number': '+254703045843'
        }
        self.assertEqual(serializer.data, expected_data)

    def test_deserialization_valid_data(self):
        """
        Test that CustomerSerialiser deserializes valid data correctly.
        """
        valid_data = {
            'name': 'Jane Doe',
            'phone_number': '+254703045833'
        }
        serializer = CustomerSerialiser(data=valid_data)
        self.assertTrue(serializer.is_valid())
        customer = serializer.save()
        self.assertEqual(customer.name, 'Jane Doe')
        self.assertEqual(customer.phone_number, '+254703045833')

    def test_deserialization_invalid_data(self):
        """
        Test that CustomerSerialiser raises a ValidationError for invalid data.
        """
        invalid_data = {
            'name': '',
            'phone_number': 'invalid_phone'
        }
        serializer = CustomerSerialiser(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_read_only_id_field(self):
        """
        Test that the 'id' field is read-only.
        """
        data = {
            'id': '12345',
            'name': 'New Name',
            'phone_number': '+254703045543'
        }
        serializer = CustomerSerialiser(instance=self.customer, data=data)
        self.assertTrue(serializer.is_valid())

        customer = serializer.save()
        customer = serializer.save()
        self.assertNotEqual(customer.id, '12345')
        self.assertEqual(customer.id, self.customer.id)
        self.assertEqual(customer.name, 'New Name')


class OrderSerialiserTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name='John Doe', phone_number='+254703045843')
        self.order_data = {
            'customer': self.customer,
            'item': 'Laptop',
            'amount': '999.99'
        }
        self.order = Order.objects.create(**self.order_data)

    def test_serialization(self):
        """
        Test that OrderSerialiser serializes an Order instance correctly.
        """
        serializer = OrderSerialiser(self.order)
        expected_data = {
            'id': str(
                self.order.id),
            'item': 'Laptop',
            'amount': '999.99',
            'created_at': self.order.created_at.strftime(
                "%B %d, %Y, %I:%M %p"),
            'customer': {
                'id': str(
                    self.customer.id),
                'name': 'John Doe',
                'phone_number': '+254703045843'}}
        self.assertEqual(serializer.data, expected_data)

    def test_deserialization_valid_data(self):
        """
        Test that OrderSerialiser deserializes valid data correctly.
        """
        valid_data = {
            'customer': self.customer.id,
            'item': 'Phone',
            'amount': '499.99'
        }
        serialiser = OrderSerialiser(data=valid_data)
        self.assertTrue(serialiser.is_valid())

    def test_deserialization_invalid_data(self):
        """
        Test that OrderSerialiser raises a ValidationError for invalid data.
        """
        invalid_data = {
            'customer': self.customer.id,
            'item': '',
            'amount': 'invalid_amount'
        }
        serializer = OrderSerialiser(data=invalid_data)
        self.assertFalse(serializer.is_valid())

    def test_read_only_id_field(self):
        """
        Test that the 'id' field is read-only.
        """
        data = {
            'id': '12345',
            'item': 'Tablet',
            'amount': '299.99'
        }
        serializer = OrderSerialiser(instance=self.order, data=data)
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertNotEqual(order.id, '12345')
        self.assertEqual(order.id, self.order.id)
        self.assertEqual(order.item, 'Tablet')
        self.assertEqual(float(order.amount), 299.99)
