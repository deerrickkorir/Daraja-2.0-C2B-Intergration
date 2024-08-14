from flask import Flask, request
import requests
from requests.auth import HTTPBasicAuth
import json
from datetime import datetime
import base64

app = Flask(__name__)

base_url = ''  # Set this to your base URL if needed
consumer_key = 'dTfQANAtqn6zSF9ipcQWTLxlL7oRWyJKxXyiuXG4a5YkZSXq'  # Replace with your actual consumer key
consumer_secret = 'ZGUFh4XjJbXNsoapTVXWgOwiMwe9fGepo2LzaaNDb46iWskbPr7riwyfGQHhY2SM'  # Replace with your actual consumer secret

@app.route('/')
def home():
    return 'Hello World!'

@app.route('/access_token')
def get_access_token():
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = response.json()
    return data.get('access_token', 'Error obtaining access token')

@app.route('/register')
def register_urls():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/registerurl'
    access_token = _access_token()
    my_endpoint = base_url + "c2b/"
    headers = { "Authorization": f"Bearer {access_token}" }
    r_data = {
        "ShortCode": "600383",
        "ResponseType": "Completed",
        "ConfirmationURL": my_endpoint + 'con',
        "ValidationURL": my_endpoint + 'val'
    }

    response = requests.post(endpoint, json=r_data, headers=headers)
    return response.json()

@app.route('/simulate')
def test_payment():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/c2b/v1/simulate'
    access_token = _access_token()
    headers = { "Authorization": f"Bearer {access_token}" }

    data_s = {
        "Amount": 100,
        "ShortCode": "600383",
        "BillRefNumber": "test",
        "CommandID": "CustomerPayBillOnline",
        "Msisdn": "254708374149"
    }

    response = requests.post(endpoint, json=data_s, headers=headers)
    return response.json()

@app.route('/b2c')
def make_payment():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/b2c/v1/paymentrequest'
    access_token = _access_token()
    headers = { "Authorization": f"Bearer {access_token}" }
    my_endpoint = base_url + "/b2c/"

    data = {
        "InitiatorName": "apitest342",
        "SecurityCredential": "SQFrXJpsdlADCsa986yt5KIVhkskagK+1UGBnfSu4Gp26eFRLM2eyNZeNvsqQhY9yHfNECES3xyxOWK/mG57Xsiw9skCI9egn5RvrzHOaijfe3VxVjA7S0+YYluzFpF6OO7Cw9qxiIlynYS0zI3NWv2F8HxJHj81y2Ix9WodKmCw68BT8KDge4OUMVo3BDN2XVv794T6J82t3/hPwkIRyJ1o5wC2teSQTgob1lDBXI5AwgbifDKe/7Y3p2nn7KCebNmRVwnsVwtcjgFs78+2wDtHF2HVwZBedmbnm7j09JO9cK8glTikiz6H7v0vcQO19HcyDw62psJcV2c4HDncWw==",
        "CommandID": "BusinessPayment",
        "Amount": "200",
        "PartyA": "601342",
        "PartyB": "254708374149",
        "Remarks": "Pay Salary",
        "QueueTimeOutURL": my_endpoint + "timeout",
        "ResultURL": my_endpoint + "result",
        "Occasion": "Salary"
    }

    response = requests.post(endpoint, json=data, headers=headers)
    return response.json()

@app.route('/lnmo', methods=['POST'])
def init_stk():
    endpoint = 'https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest'
    access_token = _access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    password = f"174379{timestamp}your_shortcode_password"  # Ensure this is formatted correctly
    datapass = base64.b64encode(password.encode('utf-8')).decode('utf-8')

    data = {
        "BusinessShortCode": "174379",
        "Password": datapass,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "PartyA": "0723751325",  # Your phone number
        "PartyB": "174379",
        "PhoneNumber": "0723751325",  # Your phone number
        "CallBackURL": base_url + "/lnmo/result",
        "AccountReference": "TestPay",
        "TransactionDesc": "Payment Description",
        "Amount": 2
    }

    try:
        print(f"Sending request to {endpoint}")
        print(f"Request Headers: {headers}")
        print(f"Request Data: {json.dumps(data)}")
        
        response = requests.post(endpoint, json=data, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        try:
            response_json = response.json()
        except requests.exceptions.JSONDecodeError:
            response_json = {"error": "Response not in JSON format"}
        
        print(f"Response: {response_json}")
        return response_json
    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {errh}")
        return {"error": "HTTP Error", "details": str(errh)}, 400
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {e}")
        return {"error": "Request Error", "details": str(e)}, 400

@app.route('/lnmo/result', methods=['POST'])
def lnmo_result():
    data = request.get_data()
    with open('lnmo.json', 'a') as f:
        f.write(data.decode())
    return {"status": "success"}

@app.route('/b2c/result', methods=['POST'])
def result_b2c():
    data = request.get_data()
    with open('b2c.json', 'a') as f:
        f.write(data.decode())
    return {"status": "success"}

@app.route('/b2c/timeout', methods=['POST'])
def b2c_timeout():
    data = request.get_json()
    with open('b2ctimeout.json', 'a') as f:
        f.write(json.dumps(data))
    return {"status": "success"}

@app.route('/c2b/val', methods=['POST'])
def validate():
    data = request.get_data()
    with open('data_v.json', 'a') as f:
        f.write(data.decode())
    return {"status": "success"}

@app.route('/c2b/con', methods=['POST'])
def confirm():
    data = request.get_json()
    with open('data_c.json', 'a') as f:
        f.write(json.dumps(data))
    return {"status": "success"}

def _access_token():
    endpoint = 'https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials'
    response = requests.get(endpoint, auth=HTTPBasicAuth(consumer_key, consumer_secret))
    data = response.json()
    return data.get('access_token', 'Error obtaining access token')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
