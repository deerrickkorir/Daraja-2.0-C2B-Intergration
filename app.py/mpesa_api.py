import requests
from requests.auth import HTTPBasicAuth

# Constants
CONSUMER_KEY = 'dTfQANAtqn6zSF9ipcQWTLxlL7oRWyJKxXyiuXG4a5YkZSXq'
CONSUMER_SECRET = 'ZGUFh4XjJbXNsoapTVXWgOwiMwe9fGepo2LzaaNDb46iWskbPr7riwyfGQHhY2SM'
ACCESS_TOKEN_ENDPOINT = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
C2B_TRANSACTION_ENDPOINT = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/safaricom-safaricom-safaricom/safaricom-safaricom'

def get_access_token():
    """
    Generate an access token for the M-Pesa API.
    """
    response = requests.get(ACCESS_TOKEN_ENDPOINT, auth=HTTPBasicAuth(CONSUMER_KEY, CONSUMER_SECRET))
    response_json = response.json()
    if response.status_code == 200:
        return response_json['access_token']
    else:
        raise Exception(f"Error getting access token: {response_json.get('error_description')}")

def initiate_c2b_transaction(access_token):
    """
    Initiate a C2B transaction using the M-Pesa API.
    """
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = {
        'Shortcode': '174379',  # Replace with your shortcode
        'Amount': '100',        # Amount to send
        'PhoneNumber': '254708374149',  # Phone number in international format
        'AccountReference': 'Test123',  # Your account reference
        'TransactionDesc': 'Payment for testing'  # Description of the transaction
    }
    
    response = requests.post(C2B_TRANSACTION_ENDPOINT, json=payload, headers=headers)
    return response.json()

def main():
    try:
        token = get_access_token()
        print(f'Access Token: {token}')
        
        transaction_response = initiate_c2b_transaction(token)
        print('Transaction Response:', transaction_response)
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
