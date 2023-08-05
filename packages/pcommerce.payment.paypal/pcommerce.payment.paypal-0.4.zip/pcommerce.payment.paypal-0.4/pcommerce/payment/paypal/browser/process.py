from xml.dom import minidom

from Products.Five.browser import BrowserView

from Products.CMFCore.utils import getToolByName
import transaction

from pcommerce.core.interfaces import IPaymentProcessor
from pcommerce.core.interfaces import IOrderRegistry
from time import time
from urllib import urlencode
from urllib2 import urlopen, Request

import logging
logger = logging.getLogger("Plone")

class ProcessPaypal(BrowserView):
    """process Paypal payments
    """

    def __call__(self):
        lang = self.request.get('QUERY_STRING', None)
        if not lang:
            lang = None
        data = self.request.form
        # If there is no txn_id in the received arguments don't proceed
        if not "txn_id" in data:
            return "No Parameters"
 
        # Verify the data received with Paypal
        if not self.verify_ipn(data):
            logger.info("pcommerce.payment.paypal: Error with paypal verify")
            return "Error with paypal" 
        else:
            processor = IPaymentProcessor(self.context)
            return processor.processOrder(data['item_number1'], 'pcommerce.payment.paypal', lang)

    def verify_ipn(self,data):
        # prepares provided data set to inform PayPal we wish to validate the response
        data["cmd"] = "_notify-validate"
        params = urlencode(data)

        props = getToolByName(self.context, 'portal_properties').paypal_properties
        # sends the data and request to the PayPal Sandbox
        paypalurl = self.getPayPalURL()
        req = Request(paypalurl, params)
        req.add_header("Content-type", "application/x-www-form-urlencoded")
        # reads the response back from PayPal
        response = urlopen(req)
        status = response.read()
        # If not verified
        if not status == "VERIFIED":
            return False
 
        # if not the correct receiver ID
        if not data["receiver_id"] == props.receiver_id:
            return False
 
        # if not the correct currency
        if not data["mc_currency"] == "EUR":
            return False
        # already processed?
        order_registry = IOrderRegistry(self.context)
        order = order_registry.getOrder(int(data['item_number1']))
        try:
            if order.txn_id == data['txn_id']:
                logger.info("pcommerce.payment.paypal: Transaction already processed")
                return False
        except:
            order.txn_id = data['txn_id'] 
            transaction.commit() 
        # otherwise...
        return True

    def getPayPalURL(self):
        """"""
        context = self.context 
        props = getToolByName(context, 'portal_properties').paypal_properties
        if props.test:
            return """https://www.sandbox.paypal.com/cgi-bin/webscr"""
        return """https://www.paypal.com/cgi-bin/webscr"""
