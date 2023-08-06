import json
import logging
import urlparse

import requests


class BitPayError(RuntimeError):
    """BitPay API error
    
    """
    def __init__(self, message, type):
        RuntimeError.__init__(self, message)
        self.type = type


class BitPayAPI(object):
    
    ENDPOINT = 'bitpay.com/api/'

    INVOICE_STATUS_NEW = 'new'
    INVOICE_STATUS_PAID = 'paid'
    INVOICE_STATUS_CONFIRMED = 'confirmed'
    INVOICE_STATUS_COMPLETE = 'complete'
    INVOICE_STATUS_EXPIRED = 'expired'
    INVOICE_STATUS_INVALID = 'invalid'
    INVOICE_STATUS_ALL = [
        INVOICE_STATUS_NEW,
        INVOICE_STATUS_PAID,
        INVOICE_STATUS_CONFIRMED,
        INVOICE_STATUS_COMPLETE,
        INVOICE_STATUS_EXPIRED,
        INVOICE_STATUS_INVALID,
    ]

    TRANSACTION_SPEED_HIGH = 'high'
    TRANSACTION_SPEED_MEDIUM = 'medium'
    TRANSACTION_SPEED_LOW = 'low'
    TRANSACTION_SPEED_ALL = [
        TRANSACTION_SPEED_HIGH,
        TRANSACTION_SPEED_MEDIUM,
        TRANSACTION_SPEED_LOW,
    ]
     
    def __init__(
        self, 
        api_key, 
        endpoint=None, 
        verify_ssl=True, 
        logger=None
    ):
        self.logger = logger or logging.getLogger(__name__)
        self.api_key = api_key
        self.verify_ssl = verify_ssl
        self._endpoint = endpoint or self.ENDPOINT

    def _check_result(self, r, raise_error=True):
        result = r.json()
        self.logger.info('Result: %s', result)
        if raise_error and 'error' in result:
            error = result['error']
            raise BitPayError(error['message'], error['type'])
        return result
        
    @property
    def base_url(self):
        return 'https://' + self._endpoint

    def create_invoice(
        self, 
        price, 
        currency, 
        posData=None, 
        notificationURL=None,
        transactionSpeed=None, 
        fullNotifications=None, 
        notificationEmail=None, 
        redirectURL=None, 
        orderId=None, 
        itemDesc=None, 
        itemCode=None, 
        physical=None, 
        buyerName=None, 
        buyerAddress1=None, 
        buyerAddress2=None, 
        buyerCity=None, 
        buyerState=None, 
        buyerZip=None, 
        buyerCountry=None, 
        buyerEmail=None, 
        buyerPhone=None, 
        raise_error=True, 
    ):
        """Create an BitPay invoice

        """
        params = dict(
            price=price, 
            currency=currency, 
        )

        param_keys = [
            'posData', 
            'notificationURL',
            'transactionSpeed', 
            'fullNotifications', 
            'notificationEmail', 
            'redirectURL', 
            'orderId', 
            'itemDesc', 
            'itemCode', 
            'physical', 
            'buyerName', 
            'buyerAddress1', 
            'buyerAddress2', 
            'buyerCity', 
            'buyerState', 
            'buyerZip', 
            'buyerCountry', 
            'buyerEmail', 
            'buyerPhone', 
        ]
        for key in param_keys:
            value = locals()[key]
            if value is not None:
                params[key] = value

        url = urlparse.urljoin(self.base_url, 'invoice')
        self.logger.info('Connect to %s', url)
        data = json.dumps(params)
        self.logger.debug('Post body: %s', data)

        r = requests.post(
            url, 
            headers={'content-type': 'application/json'},
            data=data,
            auth=(self.api_key, ''),
            verify=self.verify_ssl,
        )
        return self._check_result(r, raise_error)

    def get_invoice_status(self, id, raise_error=True):
        """Get invocie status and return

        """
        url = urlparse.urljoin(self.base_url, 'invoice' + '/' + id)
        self.logger.info('Connect to %s', url)
        r = requests.get(
            url, 
            auth=(self.api_key, ''),
            verify=self.verify_ssl,
        )
        return self._check_result(r, raise_error)
