'''
Defines unittest for models
'''

from django.test import TestCase
from customer_orders_app.models import Customer, Order
import uuid
from django.db.utils import (
    DataError, IntegrityError,
)
from django.core.exceptions import ValidationError
from datetime import timezone


class ModelsTestCase(TestCase):

    def setUp(self):
        self.customer = Customer(name="John Doe", phone_number="+1234567890")
        self.customer.save()

    def test_customer_creation(self):

        self.assertEqual(self.customer.name, "John Doe")
        self.assertEqual(self.customer.phone_number, "+1234567890")
        self.assertIsInstance(self.customer.id, uuid.UUID)
        self.assertFalse(self.customer.orders.all())

    def test_str_method(self):
        self.assertEqual(str(self.customer), "John Doe")

    def test_integer_name_validation(self):
        """
        test when an interger is passed
        """
        with self.assertRaises(ValueError) as error:
            self.customer.name = 12.454
            self.customer.save()

    def test_list_name_validation(self):
        """
        Tests if a ValueError is raised when trying to set
        the customer name to a list containing 'name'.
        """
        with self.assertRaises(ValueError) as error:
            self.customer.name = [12.454]
            self.customer.save()

    def test_none_name_validation(self):
        """
        Tests if a ValueError is raised when trying to set
        the customer name to None.
        """
        with self.assertRaises(ValueError):
            self.customer.name = None
            self.customer.save()

    def test_long_string_name_validation(self):
        """
        Tests if a ValueError is raised when trying to set
        the customer name to a very long string.
        """
        with self.assertRaises(DataError):
            self.customer.name = 'b' * 60
            self.customer.save()

    def test_tuple_name_validation(self):
        """
        Tests if a ValueError is raised when trying to set the
        customer name to a tuple containing 'name'.
        """
        with self.assertRaises(ValueError):
            self.customer.name = ('name',)
            self.customer.save()

    def test_dictionary_name_validation(self):
        """
        Tests if a ValueError is raised when trying to set
        the customer name to a dictionary.
        """
        with self.assertRaises(ValueError):
            self.customer.name = {}
            self.customer.save()

    def test_id_is_unique(self):
        customer1 = Customer.objects.create(
            name="John Doe", phone_number="+1234567890")
        customer2 = Customer.objects.create(
            name="John Doe", phone_number="+1234567890")

        self.assertNotEqual(customer1.id, customer2.id)

    def test_Customer_order_rlationship(self):
        order = Order(
            customer=self.customer,
            item="Example Item",
            amount=99.99)
        order.save()
        order_set = self.customer.orders.all()

        self.assertTrue(order_set)
        self.assertEqual(1, len(order_set))
        self.assertEqual(order_set[0].item, "Example Item")
        self.assertEqual(float(order_set[0].amount), 99.99)

    def test_order_realtionship_wrong_values(self):
        with self.assertRaises(ValueError):
            order = Order(
                customer="Not a customer",
                item="Example Item",
                amount=99.99)
            order.save()


class OrderModelTest(TestCase):

    def setUp(self):
        self.customer = Customer.objects.create(
            name='John Doe', phone_number="+1234567890")
        self.order = Order.objects.create(
            customer=self.customer,
            item='Bike',
            amount=23232.00
        )

    def test_order_creation(self):
        """
        Test that an order can be created and is linked to a
        customer.
        """
        self.assertEqual(self.order.customer.name, 'John Doe')
        self.assertEqual(self.order.item, 'Bike')
        self.assertEqual(self.order.amount, 23232.00)

    def test_order_string_representation(self):
        """
        Test the string representation of the Order model.
        """
        self.assertEqual(str(self.order), 'Bike - 23232.0')

    def test_item_null(self):
        """
        Test validation when 'item' is null.
        """
        with self.assertRaises(IntegrityError):
            Order.objects.create(
                customer=self.customer,
                item=None,
                amount=23232.00
            )

    def test_amount_string(self):
        """
        Test validation when 'amount' is a string.
        """
        with self.assertRaises(IntegrityError):
            Order.objects.create(
                customer=self.customer,
                item='bike'
            )

    def test_amount_invalid_string(self):
        """
        Test validation when 'amount' is an invalid string.
        """
        with self.assertRaises(ValidationError):
            Order.objects.create(
                customer=self.customer,
                item='bike',
                amount='bikes'
            )

    def test_amount_none(self):
        """
        Test validation when 'amount' is None.
        """
        with self.assertRaises(IntegrityError):
            Order.objects.create(
                customer=self.customer,
                item='bike',
                amount=None
            )

    def test_amount_list(self):
        """
        Test validation when 'amount' is a list.
        """
        with self.assertRaises(ValidationError):
            Order.objects.create(
                customer=self.customer,
                item='bike',
                amount=[23232.00]
            )

    def test_order_amount_precision(self):
        """
        Test that the amount field handles precision correctly.
        """
        self.order.amount = 12345.679090
        self.order.save()
        self.assertEqual(self.order.amount, 12345.67909)

    def test_order_customer_relationship(self):
        """
        Test the foreign key relationship between Order and Customer.
        """
        self.assertEqual(self.order.customer, self.customer)
        self.assertEqual(self.customer.orders.count(), 1)
        self.assertEqual(self.customer.orders.first().item, 'Bike')

    def test_order_customer_relationship_validation(self):
        invalid_amounts = []
        with self.assertRaises(IntegrityError):
            self.order = Order.objects.create(
                customer=None,
                item='Bike',
                amount=23232.00
            )

        with self.assertRaises(ValueError):
            self.order = Order.objects.create(
                customer=[self.customer],
                item='Bike',
                amount=23232.00
            )

        with self.assertRaises(ValueError):
            self.order = Order.objects.create(
                customer='String',
                item='Bike',
                amount=23232.00
            )
