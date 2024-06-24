import unittest
from customer_orders_app.sms_sender import send_sms
from unittest.mock import patch, Mock
import requests


class SendSmsTests(unittest.TestCase):
    
    @patch('customer_orders_app.sms_sender.requests.post')
    def test_send_sms_success(self, mock_post):
        """
        Test sending SMS successfully.
        """
        mock_response = Mock()
        mock_response.json.return_value = {'status': 'success'}
        mock_post.return_value = mock_response

        with patch('customer_orders_app.sms_sender.os.getenv', return_value='fake_api_key'):
            send_sms('+254701036054', {'item': 'food', 'amount': 11})

        mock_post.assert_called_once_with(
            'https://api.sandbox.africastalking.com/version1/messaging',
            headers={
                'Accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
                'apiKey': 'fake_api_key'
            },
            data={
                'username': 'sandbox',
                'to': '+254701036054',
                'message': 'Order for food at Ksh 11 Created',
                'from': '44121'
            }
        )

    @patch('customer_orders_app.sms_sender.requests.post')
    def test_send_sms_failure(self, mock_post):
        """
        Test sending SMS fails due to an HTTP error.
        """
        mock_post.side_effect = requests.exceptions.RequestException('HTTP error occurred')

        with patch('customer_orders_app.sms_sender.os.getenv', return_value='fake_api_key'):
            with self.assertLogs(level='INFO') as log:
                send_sms('+254701036054', {'item': 'food', 'amount': 11})
                self.assertIn('An error occurred: HTTP error occurred', log.output[0])

if __name__ == '__main__':
    unittest.main()
