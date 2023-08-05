import requests
import json

from . import data
from . import errors
from . import version

class Gateway(object):
    SANDBOX_URL = "https://gateway.sandbox.fatzebra.com.au/v1.0/"
    LIVE_URL = "https://gateway.fatzebra.com.au/v1.0/"

    def __init__(self, username="TEST", token="TEST", sandbox=True):
        """
        Initialize the gateway

        Keyword arguments:
            username - the gateway username (default: "TEST")
            token    - the gateway token (default: "TEST")
            sandbox  - enable or disable sandbox mode (default: True)
        """
        self.username = username
        self.token = token
        self.sandbox = sandbox

    def purchase(self, amount, reference, card_holder, card_number, expiry,
                 security_code, customer_ip):
        """
        Perform a Purchase transaction.

        Keyword arguments:
            amount        - the amount for the transaction (integer) -
                            decimal amounts must be converted to integers:
                            int(2.99 * 100)
            reference     - the unique transaction reference
            card_holder   - the card holders name
            card_number   - the credit card number
            expiry        - the credit card expiry date in the format of
                            mm/yyyy (e.g. 05/2013)
            security_code - the card security code
            customer_ip   - the customer/card holders IP address

        Returns fatzebra.data.Purchase or raises fatzebra.errors.GatewayError
        if request fails.
        """
        payload = {
            'amount': amount,
            'reference': reference,
            'card_holder': card_holder,
            'card_number': card_number,
            'card_expiry': expiry,
            'cvv': security_code,
            'customer_ip': customer_ip
        }
        json_data = self._make_request('post', 'purchases', payload)

        if json_data["successful"]:
            return data.Purchase(json_data["response"])
        else:
            raise errors.GatewayError(json_data["errors"])

    def purchase_with_token(self, amount, reference, token, security_code,
                            customer_ip):
        """
        Perform a Purchase transaction with a tokenized card.

        Keyword arguments:
            amount        - the amount for the transaction (integer) -
                            decimal amounts must be converted to integers:
                            int(2.99 * 100)
            reference     - the unique transaction reference
            token         - the card token
            security_code - the card security code (optional - pass null)
            customer_ip   - the customer/card holders IP address

        Returns fatzebra.data.Purchase or raises fatzebra.errors.GatewayError
        if request fails.
        """
        payload = {
            'amount': amount,
            'reference': reference,
            'card_token': token,
            'cvv': security_code,
            'customer_ip': customer_ip
        }
        json_data = self._make_request('post', 'purchases', payload)

        if json_data["successful"]:
            return data.Purchase(json_data["response"])
        else:
            raise errors.GatewayError(json_data["errors"])

    def tokenize(self, card_holder, card_number, expiry, security_code):
        """
        Tokenize a card for future transactions

        Keyword arguments:
            card_holder   - the card holders name
            card_number   - the credit card number
            expiry        - the card expiry date in the format of mm/yyyy
                            (e.g. 05/2014)
            security_code - the card security code (aka cvv, csc, cv2 etc)
        """
        payload = {
            'card_number': card_number,
            'card_holder': card_holder,
            'card_expiry': expiry,
            'cvv': security_code
        }
        json_data = self._make_request('post', "credit_cards", payload)

        if json_data["successful"]:
            return data.CreditCard(json_data["response"])
        else:
            raise errors.GatewayError(json_data["errors"])

    def refund(self, transaction_id, amount, reference):
        """
        Refunds a transaction based off of its original transaction id

        Keyword arguments:
            transaction_id - the Fat Zebra transaction ID (xxx-P-xxxxxxxx)
            amount         - the amount to be refunded, as an integer
            reference      - your reference for the refund
        """

        payload = {
            'transaction_id': transaction_id,
            'amount': amount,
            'reference': reference
        }
        json_data = self._make_request('post', 'refunds', payload)

        if json_data["successful"]:
            return data.Refund(json_data["response"])
        else:
            raise errors.GatewayError(json_data["errors"])

    def _make_request(self, method='post', uri='purchases', payload=None):
        """ Makes the request to the gateway, and handles the responses """
        payload = payload or {}
        response = requests.request(
            method.lower(),
            self._uri(uri),
            auth=(self.username, self.token),
            data=json.dumps(payload),
            verify=True,
            headers=self._headers()
        )
        if response.status_code == 201 or response.status_code == 200:
            return response.json
        else:
            if response.status_code == 401:
                raise errors.AuthenticationError()
            else:
                raise errors.GatewayUnknownResponseError(
                    response.status_code, response.raw)

    def _uri(self, method='purchases'):
        """ Generate the URI for the request based on the settings """
        gw = self._gateway()
        return gw + method

    def _gateway(self):
        """ Get the gateway URL """
        return (Gateway.SANDBOX_URL if self.sandbox else Gateway.LIVE_URL)

    def _headers(self):
        """ Builds the headers for the request """
        return {
            "User-Agent": "Python Library %s" % version.VERSION,
            "Content-type": "application/json"
        }
