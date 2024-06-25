from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from customer_orders_app.models import Customer, Order
from customer_orders_app.sms_sender import send_sms
from django.contrib.auth.models import User
from unittest.mock import patch


class CustomerListViewTests(APITestCase):
    def setUp(self):
        """
        Create some sample customers for testing.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

        self.customer1 = Customer.objects.create(
            name="John Doe",
            phone_number="+254703045840"
        )
        self.customer2 = Customer.objects.create(
            name="Jane Doe",
            phone_number="+254703045841"
        )
        self.url = reverse('all_customers')

    def test_customer_list(self):
        """
        Ensure the customer list view returns a list of customers.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_result(self):
        '''
        test results from the url
        '''
        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 2)
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(
            response.data['results'][0]['name'],
            self.customer1.name)
        self.assertEqual(
            response.data['results'][0]['phone_number'],
            self.customer1.phone_number)
        self.assertEqual(
            response.data['results'][1]['name'],
            self.customer2.name)
        self.assertEqual(
            response.data['results'][1]['phone_number'],
            self.customer2.phone_number)

    def test_pagination(self):
        """
        test the pagination
        """
        for n, _ in enumerate(range(3, 13), start=0):
            Customer.objects.create(
                name="Jane Doe", phone_number=f"+25470304587{n}")

        response = self.client.get(self.url)
        self.assertEqual(response.data['count'], 12)
        self.assertEqual(response.data['previous'], None)
        self.assertTrue(response.data['next'])

    def test_customer_list_empty(self):
        """
        Ensure the customer list view returns an empty list when no
        customers exist.
        """
        Customer.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertEqual(len(response.data['results']), 0)

        self.assertEqual(response.data['previous'], None)
        self.assertEqual(response.data['next'], None)


class CustomerDetailViewTests(APITestCase):
    def setUp(self):
        """
        Create a customer and some orders for testing.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

        self.customer = Customer.objects.create(
            name="John Doe",
            phone_number="+254703045843"
        )
        self.order1 = Order.objects.create(
            customer=self.customer,
            item="bike",
            amount=1221.00
        )
        self.order2 = Order.objects.create(
            customer=self.customer,
            item="helmet",
            amount=120.00
        )
        self.url = reverse('view_customer_info', args=[self.customer.id])

    def tearDown(self) -> None:
        Customer.objects.all().delete()

    def test_get_customer_details(self):
        """
        Ensure the customer detail view returns the correct customer
        details and related orders.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data['Customer_details']['id'], str(
                self.customer.id))
        self.assertEqual(
            response.data['Customer_details']['name'],
            self.customer.name)
        self.assertEqual(
            response.data['Customer_details']['phone_number'],
            self.customer.phone_number)

    def test_orders(self):
        response = self.client.get(self.url)
        self.assertEqual(len(response.data['orders']), 2)
        self.assertEqual(response.data['orders'][0]['item'], self.order1.item)
        self.assertEqual(
            float(
                response.data['orders'][0]['amount']),
            self.order1.amount)
        self.assertEqual(response.data['orders'][1]['item'], self.order2.item)
        self.assertEqual(
            float(
                response.data['orders'][1]['amount']),
            self.order2.amount)

    def _test_with_non_existant_id(self, arg0):
        non_existent_id = arg0
        url = reverse('view_customer_info', args=[non_existent_id])
        return self.client.get(url)

    def test_get_customer_not_found(self):
        """
        Ensure the customer detail view returns a 404 error when the
        customer does not exist.
        """
        response = self._test_with_non_existant_id(
            'eb6dac37-ba91-46f0-a34b-ac32e0dbe535'
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(
            response.data['error'],
            'No Customer matches the given query.')

    def test_with_non_uuid_id_string(self):
        response = self._test_with_non_existant_id('null')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            response.data['error'],
            "['“null” is not a valid UUID.']")


class CustomerCreateViewTests(APITestCase):
    def setUp(self):
        """
        Set up the URL for creating customers.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

        self.url = reverse(
            'add-customer')  # Adjust the reverse lookup to your URL name

    def test_create_customer_success(self):
        """
        Ensure the customer creation endpoint creates a new
        customer successfully.
        """
        data = {
            "name": "John Doe",
            "phone_number": "+254702023042"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(response.data['phone_number'], data['phone_number'])
        self.assertTrue('id' in response.data)

    def test_create_customer_invalid_phone_number(self):
        """
        Ensure the customer creation endpoint returns errors for invalid data.
        """
        data = {
            "name": "bonee",
            "phone_number": "invalid_phone_number"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_phone_number(self):
        data = {
            "name": "bonee",
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_name(self):
        data = {
            "phone_number": "+254703054054"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_name_n_invalidPhone_number(self):
        data = {
            "phone_number": "+254703045843"
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_customer_missing_data(self):
        """
        Ensure the customer creation endpoint returns errors for missing data.
        """
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class CustomerUpdateViewTests(APITestCase):
    def setUp(self):
        """
        Create a sample customer for testing.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

        self.customer = Customer.objects.create(
            name="John Doe",
            phone_number="+254703045843"
        )
        self.url = reverse('update-customer', args=[self.customer.id])

    def test_update_customer_name_success(self):
        """
        Ensure the customer update endpoint successfully updates the
        customer's name.
        """
        data = {
            "name": "Jane Doe"
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])
        self.assertEqual(
            response.data['phone_number'],
            self.customer.phone_number)

    def test_update_customer_name_invalid_data(self):
        """
        Ensure the customer update endpoint returns errors for invalid data.
        """
        data = {
            "name": None
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_phoneNumber_invalid_data(self):
        """
        Ensure the customer update endpoint returns errors for invalid data.
        """
        data = {
            "phone_number": 1231312
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_customer_invalid_data(self):
        """
        Ensure the customer update endpoint returns errors for invalid data.
        """
        data = {
            "Not and attribute": "Nothing",
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.customer.name)
        self.assertEqual(
            response.data['phone_number'],
            self.customer.phone_number)

    def test_update_customer_name_not_found(self):
        """
        Ensure the customer update endpoint returns a 404 error when
        the customer does not exist.
        """
        non_existent_id = 'eb6dac37-ba91-46f0-a34b-ac32e0dbe535'
        url = reverse('update-customer', args=[non_existent_id])
        data = {
            "name": "Jane Doe"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_non_UUID(self):
        non_existent_id = 'string'
        url = reverse('update-customer', args=[non_existent_id])
        data = {
            "name": "Jane Doe"
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, 400)


class CustomerDeleteViewTests(APITestCase):
    def setUp(self):
        """
        Create a sample customer for testing.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

        self.customer = Customer.objects.create(
            name="John Doe",
            phone_number="+254703045843"
        )
        self.url = reverse('delete-customer', args=[self.customer.id])

    def test_delete_customer_success(self):
        """
        Ensure the customer delete endpoint successfully deletes the customer.
        """
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(Customer.objects.filter(id=self.customer.id).exists())

    def test_delete_customer_not_found(self):
        """
        Ensure the customer delete endpoint returns a 404 error when
        the customer does not exist.
        """
        non_existent_id = '12345678-1234-5678-1234-567812345678'
        url = reverse('delete-customer', args=[non_existent_id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderListViewTests(APITestCase):
    def setUp(self):
        """
        Create sample customers and orders for testing.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

        self.customer1 = Customer.objects.create(
            name="John Doe",
            phone_number="+254703045843"
        )
        self.customer2 = Customer.objects.create(
            name="Jane Doe",
            phone_number="+254703045842"
        )

        self.order1 = Order.objects.create(
            item="bike",
            amount=1221.00,
            customer=self.customer1
        )
        self.order2 = Order.objects.create(
            item="helmet",
            amount=121.00,
            customer=self.customer2
        )

        self.url = reverse('all_orders')

    def test_get_order_list_mmeta_data(self):
        """
        Ensure the order list endpoint returns a list of all orders
        with pagination.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])

    def test_result(self):
        response = self.client.get(self.url)
        results = response.data['results']
        self.assertEqual(len(results), 2)

    def test_first_result(self):

        response = self.client.get(self.url)
        results = response.data['results']
        self.assertEqual(results[0]['id'], str(self.order1.id))
        self.assertEqual(results[0]['item'], self.order1.item)
        self.assertEqual(float(results[0]['amount']), self.order1.amount)
        self.assertEqual(results[0]['customer']['id'], str(self.customer1.id))
        self.assertEqual(results[0]['customer']['name'], self.customer1.name)
        self.assertEqual(
            results[0]['customer']['phone_number'],
            self.customer1.phone_number)

    def test_second_result(self):
        response = self.client.get(self.url)
        results = response.data['results']
        self.assertEqual(results[1]['id'], str(self.order2.id))
        self.assertEqual(results[1]['item'], self.order2.item)
        self.assertEqual(float(results[1]['amount']), self.order2.amount)
        self.assertEqual(results[1]['customer']['id'], str(self.customer2.id))
        self.assertEqual(results[1]['customer']['name'], self.customer2.name)
        self.assertEqual(
            results[1]['customer']['phone_number'],
            self.customer2.phone_number)

    def test_pagination_order_list(self):
        """
        Ensure the order list endpoint supports pagination.
        """
        # Create more orders to test pagination
        for i in range(3, 13):
            Order.objects.create(
                item=f"item_{i}",
                amount=100.00 * i,
                customer=self.customer1
            )

        response = self.client.get(self.url, {'page': 2, 'page_size': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 12)
        self.assertIsNone(response.data['next'])
        self.assertIsNotNone(response.data['previous'])
        self.assertEqual(len(response.data['results']), 2)

    def test_empty_order_list(self):
        """
        Ensure the order list endpoint returns an empty list when
        there are no orders.
        """
        Order.objects.all().delete()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 0)
        self.assertIsNone(response.data['next'])
        self.assertIsNone(response.data['previous'])
        self.assertEqual(response.data['results'], [])


class ViewAnOrderTests(APITestCase):
    def setUp(self):
        """
        Create sample customers and orders for testing.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

        self.customer1 = Customer.objects.create(
            name="John Doe",
            phone_number="+254703045843"
        )
        self.customer2 = Customer.objects.create(
            name="Jane Doe",
            phone_number="+254703045844"
        )

        self.order1 = Order.objects.create(
            item="bike",
            amount=1221.00,
            customer=self.customer1
        )
        self.order2 = Order.objects.create(
            item="helmet",
            amount=121.00,
            customer=self.customer2
        )

        self.url = reverse('view_order')

    def test_get_order_by_order_id(self):
        """
        Ensure the endpoint retrieves order information based on order_id.
        """
        response = self.client.get(self.url, {'order_id': self.order1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['id'], str(self.order1.id))
        self.assertEqual(response.data['item'], self.order1.item)
        self.assertEqual(float(response.data['amount']), self.order1.amount)
        self.assertEqual(
            response.data['customer']['id'], str(
                self.customer1.id))

    def test_get_order_by_invalid_order_id(self):
        """
        Ensure the endpoint retrieves order information based on order_id.
        """
        response = self.client.get(
            self.url, {'order_id': 'd177ccaf-6c98-4d1c-b625-6fbaf4ae62c3'})
        self.assertEqual(response.status_code, 404)

    def test_get_order_by_empty_order_id(self):
        """
        Ensure the endpoint retrieves order information based on order_id.
        """
        response = self.client.get(self.url, {'order_id': ''})
        self.assertEqual(response.status_code, 400)

    def test_get_order_by_ztring_order_id(self):
        """
        Ensure the endpoint retrieves order information based on order_id.
        """
        response = self.client.get(self.url, {'order_id': 'string'})
        self.assertEqual(response.status_code, 400)

    def test_get_orders_by_customer_id(self):
        """
        Ensure the endpoint retrieves order information based on customer_id.
        """
        response = self.client.get(
            self.url, {'customer_id': self.customer1.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['id'], str(self.order1.id))
        self.assertEqual(response.data[0]['item'], self.order1.item)
        self.assertEqual(float(response.data[0]['amount']), self.order1.amount)
        self.assertEqual(
            response.data[0]['customer']['id'], str(
                self.customer1.id))

    def test_get_orders_missing_params(self):
        """
        Ensure the endpoint returns an error message when no
        parameters are provided.
        """
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, 'Please pass customer_id or order_id')

    def test_get_orders_invalid_customer_id(self):
        """
        Ensure the endpoint returns a 404 error when an invalid
        customer_id is provided.
        """
        response = self.client.get(
            self.url, {
                'customer_id': 'd177ccaf-6c98-4d1c-b625-6fbaf4ae62c3'})
        self.assertEqual(response.status_code, 404)

    def test_empty_customer_id(self):
        """
        Ensure the endpoint returns a 404 error when an invalid
        customer_id is provided.
        """
        response = self.client.get(self.url, {'customer_id': ''})
        self.assertEqual(response.status_code, 400)

    def test_string_customer_id(self):
        """
        Ensure the endpoint returns a 404 error when an invalid
        customer_id is provided.
        """
        response = self.client.get(self.url, {'customer_id': 'String'})
        self.assertEqual(response.status_code, 400)


class OrderCreateViewTests(APITestCase):
    def setUp(self):
        """
        Create sample customers for testing.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

        self.customer = Customer.objects.create(
            name="John Doe",
            phone_number="+254703045843"
        )

        self.url = reverse('add-order')

    @patch('customer_orders_app.views.django_rq.enqueue')
    def test_create_order_success(self, mock_enqueue):
        """
        Ensure the endpoint creates a new order successfully with valid data.
        """
        data = {
            'customer_id': str(self.customer.id),
            'item': 'phone',
            'amount': 1212
        }
        response = self.client.post(self.url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['item'], data['item'])
        self.assertEqual(response.data['amount'], '1212.00')
        self.assertEqual(response.data['customer']['id'], data['customer_id'])

        mock_enqueue.assert_called_once_with(
            send_sms, '+254703045843', {'item': 'phone', 'amount': 1212})

    def test_create_order_invalid_customer(self):
        """
        Ensure the endpoint returns a 404 error when an invalid
        customer_id is provided.
        """
        data = {
            'customer_id': 'd177ccaf-6c98-4d1c-b625-6fbaf4ae62c3',
            'item': 'phone',
            'amount': 1212
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_missing_customer(self):
        """
        Ensure the endpoint returns a 404 error when an missing
        customer_id is provided.
        """
        data = {

            'item': 'phone',
            'amount': 1212
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_create_order_missing_item(self):
        """
        Ensure the endpoint returns a 400 error when 'item' is missing.
        """
        data = {
            'customer_id': str(self.customer.id),
            'amount': 1212
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_missing_amount(self):
        """
        Ensure the endpoint returns a 400 error when 'amount' is missing.
        """
        data = {
            'customer_id': str(self.customer.id),
            'item': 'phone'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_invalid_amount(self):
        """
        Ensure the endpoint returns a 400 error when 'amount' is invalid.
        """
        data = {
            'customer_id': str(self.customer.id),
            'item': 'phone',
            'amount': 'invalid'
        }
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_order_empty_data(self):
        """
        Ensure the endpoint returns a 404 on missing data
        """
        data = {}
        response = self.client.post(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class OrderUpdateViewTests(APITestCase):
    def setUp(self):
        """
        Create a sample customer and order for testing.
        """
        self.user = User.objects.create_user(
            username='testuser', password='testpassword')
        self.client = APIClient()
        self.client.login(username='testuser', password='testpassword')

        self.customer = Customer.objects.create(
            name="John Doe",
            phone_number="+254703045843"
        )
        self.order = Order.objects.create(
            customer=self.customer,
            item="phone",
            amount=1212
        )
        self.url = reverse('update-order', args=[self.order.id])

    def test_update_order_success(self):
        """
        Ensure the endpoint updates an existing order successfully
        with valid data.
        """
        data = {
            'item': 'Laptop',
            'amount': 500000
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item'], data['item'])
        self.assertEqual(float(response.data['amount']), 500000.00)
        self.assertEqual(
            response.data['customer']['id'], str(
                self.customer.id))

    def test_update_order_partial_success(self):
        """
        Ensure the endpoint updates an existing order successfully
        with partial data.
        """
        data = {
            'item': 'Tablet'
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['item'], data['item'])
        self.assertEqual(float(response.data['amount']), 1212.00)

    def test_update_order_invalid_order_id(self):
        """
        Ensure the endpoint returns a 404 error when an invalid
        order_id is provided.
        """
        url = reverse(
            'update-order',
            args=['d177ccaf-6c98-4d1c-b625-6fbaf4ae62c3'])

        data = {
            'item': 'Laptop',
            'amount': 500000
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_order_invalid_data(self):
        """
        Ensure the endpoint returns a 400 error when invalid data is provided.
        """
        data = {
            'item': '',
            'amount': 'invalid-amount'
        }
        response = self.client.put(self.url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_order_no_data(self):
        """
        Ensure the endpoint returns a 400 error when no data is provided.
        """
        response = self.client.put(self.url, {}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['item'], 'phone')
        self.assertEqual(float(response.data['amount']), 1212.00)
