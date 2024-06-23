from django.test import TestCase
from rest_framework.serializers import ValidationError
from customer_orders_app.models import Customer, Order
from customer_orders_app.serialisers import CustomerSerialiser, OrderSerialiser
import uuid

class CustomerSerialiserTests(TestCase):

    def setUp(self):
        self.customer_data = {
            'name': 'John Doe',
            'phone_number': '+1234567890'
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
            'phone_number': '+1234567890'
        }
        self.assertEqual(serializer.data, expected_data)

    def test_deserialization_valid_data(self):
        """
        Test that CustomerSerialiser deserializes valid data correctly.
        """
        valid_data = {
            'name': 'Jane Doe',
            'phone_number': '+9876543210'
        }
        serializer = CustomerSerialiser(data=valid_data)
        self.assertTrue(serializer.is_valid())
        customer = serializer.save()
        self.assertEqual(customer.name, 'Jane Doe')
        self.assertEqual(customer.phone_number, '+9876543210')

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
        with self.assertRaises(ValidationError):
            serializer.save()

    def test_read_only_id_field(self):
        """
        Test that the 'id' field is read-only.
        """
        data = {
            'id': '12345',
            'name': 'New Name',
            'phone_number': '+1234567890'
        }
        serializer = CustomerSerialiser(instance=self.customer, data=data)
        self.assertTrue(serializer.is_valid())
        customer = serializer.save()
        self.assertNotEqual(customer.id, '12345')
        self.assertEqual(customer.id, self.customer.id)
        self.assertEqual(customer.name, 'New Name')
        self.assertEqual(customer.phone_number, '+1234567890')


class OrderSerialiserTests(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(name='John Doe', phone_number='+1234567890')
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
            'id': str(self.order.id),
            'item': 'Laptop',
            'amount': '999.99',
            'created_at': self.order.created_at.strftime("%B %d, %Y, %I:%M %p"),
            'customer': {
                'id': str(self.customer.id),
                'name': 'John Doe',
                'phone_number': '+1234567890'
            }
        }
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
        serializer = OrderSerialiser(data=valid_data)
        self.assertTrue(serializer.is_valid())
        order = serializer.save()
        self.assertEqual(order.item, 'Phone')
        self.assertEqual(order.amount, 499.99)

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
        with self.assertRaises(ValidationError):
            serializer.save()

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
        self.assertEqual(order.amount, 299.99)
