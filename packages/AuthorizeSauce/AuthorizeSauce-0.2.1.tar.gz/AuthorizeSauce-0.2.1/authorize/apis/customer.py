from decimal import Decimal
import urllib

from suds import WebFault
from suds.client import Client

from authorize.apis.transaction import parse_response
from authorize.exceptions import AuthorizeConnectionError, \
    AuthorizeResponseError


PROD_URL = 'https://api.authorize.net/soap/v1/Service.asmx?WSDL'
TEST_URL = 'https://apitest.authorize.net/soap/v1/Service.asmx?WSDL'

class CustomerAPI(object):
    def __init__(self, login_id, transaction_key, debug=True, test=False):
        self.url = TEST_URL if debug else PROD_URL
        self.login_id = login_id
        self.transaction_key = transaction_key
        self.transaction_options = urllib.urlencode({
            'x_version': '3.1',
            'x_test_request': 'Y' if test else 'F',
            'x_delim_data': 'TRUE',
            'x_delim_char': ';',
        })

    @property
    def client(self):
        # Lazy instantiation of SOAP client, which hits the WSDL url
        if not hasattr(self, '_client'):
            self._client = Client(self.url)
        return self._client

    @property
    def client_auth(self):
        if not hasattr(self, '_client_auth'):
            self._client_auth = self.client.factory.create(
                'MerchantAuthenticationType')
            self._client_auth.name = self.login_id
            self._client_auth.transactionKey = self.transaction_key
        return self._client_auth

    def _make_call(self, service, *args):
        # Provides standard API call error handling
        method = getattr(self.client.service, service)
        try:
            response = method(self.client_auth, *args)
        except WebFault as e:
            raise AuthorizeConnectionError('Error contacting SOAP API.')
        if response.resultCode != 'Ok':
            error = response.messages[0][0]
            e = AuthorizeResponseError('%s: %s' % (error.code, error.text))
            e.full_response = {
                'response_code': error.code,
                'response_text': error.text,
            }
            raise e
        return response

    def create_saved_profile(self, internal_id, payments=None):
        """
        Creates a user profile to which you can attach saved payments.
        Requires an internal_id to uniquely identify this user. If a list of
        saved payments is provided, as generated by create_saved_payment,
        these will be automatically added to the user profile. Returns the
        user profile id.
        """
        profile = self.client.factory.create('CustomerProfileType')
        profile.merchantCustomerId = internal_id
        if payments:
            payment_array = self.client.factory.create(
                'ArrayOfCustomerPaymentProfileType')
            payment_array.CustomerPaymentProfileType = payments
            profile.paymentProfiles = payment_array
        response = self._make_call('CreateCustomerProfile', profile, 'none')
        profile_id = response.customerProfileId
        payment_ids = None
        if payments:
            payment_ids = response.customerPaymentProfileIdList[0]
        return profile_id, payment_ids

    def create_saved_payment(self, credit_card, address=None, profile_id=None):
        """
        Creates a payment profile. If profile_id is provided, this payment
        profile will be created in Authorize.net attached to that profile.
        If it is not provided, the payment profile will be returned and can
        be provided in a list to the create_profile call.
        """
        # Create the basic payment profile with credit card details
        payment_profile = self.client.factory.create(
            'CustomerPaymentProfileType')
        customer_type_enum = self.client.factory.create('CustomerTypeEnum')
        payment_profile.customerType = customer_type_enum.individual
        payment_type = self.client.factory.create('PaymentType')
        credit_card_type = self.client.factory.create('CreditCardType')
        credit_card_type.cardNumber = credit_card.card_number
        credit_card_type.expirationDate = '{0.exp_year}-{0.exp_month:0>2}' \
            .format(credit_card)
        credit_card_type.cardCode = credit_card.cvv
        payment_type.creditCard = credit_card_type
        payment_profile.payment = payment_type

        # Customer billing name and address are optional fields
        if credit_card.first_name:
            payment_profile.billTo.firstName = credit_card.first_name
        if credit_card.last_name:
            payment_profile.billTo.lastName = credit_card.last_name
        if address and address.street:
            payment_profile.billTo.address = address.street
        if address and address.city:
            payment_profile.billTo.city = address.city
        if address and address.state:
            payment_profile.billTo.state = address.state
        if address and address.zip_code:
            payment_profile.billTo.zip = address.zip_code
        if address and address.country:
            payment_profile.billTo.country = address.country

        # If a profile id is provided, create saved payment on that profile
        # Otherwise, return an object for a later call to create_saved_profile
        if profile_id:
            response = self._make_call('CreateCustomerPaymentProfile',
                profile_id, payment_profile, 'none')
            return response.customerPaymentProfileId
        else:
            return payment_profile

    def delete_saved_profile(self, profile_id):
        self._make_call('DeleteCustomerProfile', profile_id)

    def delete_saved_payment(self, profile_id, payment_id):
        self._make_call('DeleteCustomerPaymentProfile',
            profile_id, payment_id)

    def auth(self, profile_id, payment_id, amount):
        transaction = self.client.factory.create('ProfileTransactionType')
        auth = self.client.factory.create('ProfileTransAuthOnlyType')
        amount = Decimal(str(amount)).quantize(Decimal('0.01'))
        auth.amount = str(amount)
        auth.customerProfileId = profile_id
        auth.customerPaymentProfileId = payment_id
        transaction.profileTransAuthOnly = auth
        response = self._make_call('CreateCustomerProfileTransaction',
            transaction, self.transaction_options)
        return parse_response(response.directResponse)

    def capture(self, profile_id, payment_id, amount):
        transaction = self.client.factory.create('ProfileTransactionType')
        capture = self.client.factory.create('ProfileTransAuthCaptureType')
        amount = Decimal(str(amount)).quantize(Decimal('0.01'))
        capture.amount = str(amount)
        capture.customerProfileId = profile_id
        capture.customerPaymentProfileId = payment_id
        transaction.profileTransAuthCapture = capture
        response = self._make_call('CreateCustomerProfileTransaction',
            transaction, self.transaction_options)
        return parse_response(response.directResponse)

    def credit(self, profile_id, payment_id, amount):
        # Creates an "unlinked credit" (as opposed to refunding a previous transaction)
        transaction = self.client.factory.create('ProfileTransactionType')
        credit = self.client.factory.create('ProfileTransRefundType')
        amount = Decimal(str(amount)).quantize(Decimal('0.01'))
        credit.amount = str(amount)
        credit.customerProfileId = profile_id
        credit.customerPaymentProfileId = payment_id
        transaction.profileTransRefund = credit
        response = self._make_call('CreateCustomerProfileTransaction',
            transaction, self.transaction_options)
        return parse_response(response.directResponse)
