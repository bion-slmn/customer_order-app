'''
Defines unittest for models
'''

from django.test import TestCase
from django.db.utils import IntegrityError
from customer_orders_app.models import Customer

class TestCustomer(TestCase):

    def setUp(self):
        name = "John Doe"
        self.customer = Customer.objects.create(name=name)

    def test_customer_str(self):
        result = str(self.customer)
        self.assertEqual(result, "John Doe")

    def test_customer_str_edge_case(self):
        name = "A" * 50
        self.customer.name = name
        self.customer.save()
        self.assertEqual(self.customer.name, name)

    def test_customer_invalid_name_none(self):
        with self.assertRaises(IntegrityError):
            Customer.objects.create(name=None)

    def test_customer_invalid_name_empty(self):
        with self.assertRaises(IntegrityError):
            Customer.objects.create(name="")

    def test_customer_invalid_name_exceeds_max_length(self):
        name = "A" * 52
        self.customer.name = name
        self.customer.save()
        # Expect the name to be truncated to max_length characters
        expected_truncated_name = "A" * 50
        self.assertEqual(self.customer.name, expected_truncated_name)
        print(self.customer)


if __name__ == '__main__':
    unittest.main()
