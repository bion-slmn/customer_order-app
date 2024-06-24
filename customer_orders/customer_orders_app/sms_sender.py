
import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(format='%(asctime)s %(message)s',)
logger = logging.getLogger()

def send_sms(recipient_number: str, order_data: dict) ->None:
    """
    Sends an SMS notification to a recipient with order information.

    Args:
        recipient_number: The phone number of the recipient.
        order_data: A dictionary containing order information.

    Returns:
        None
    """
    url = 'https://api.sandbox.africastalking.com/version1/messaging'
    API_KEY = os.getenv("AFRICASTALKING_API_KEY")
    USERNAME = 'sandbox'
    message = f'Order for {order_data["item"]} at Kshs {order_data["amount"]} Created'

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'apiKey': API_KEY
    }

    data = {
        'username': USERNAME,
        'to': f'{recipient_number}',
        'message': message,
        'from': '44121'
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        print(response.status_code)
        
    except Exception as err:
        print(f"An error occurred: {err}")