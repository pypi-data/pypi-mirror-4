import urllib, math

from zope.interface import implements, Interface
from zope.component import adapts, getMultiAdapter

from Products.CMFCore.utils import getToolByName

from paypal import PayPalConfig

from pcommerce.core.interfaces import IPaymentMethod
from pcommerce.core.interfaces import IShoppingCart
from pcommerce.core.currency import CurrencyAware
from pcommerce.core import PCommerceMessageFactory as _

from pcommerce.payment.paypal.interfaces import IPaypalPayment

from pcommerce.payment.paypal import config

from paypal import PayPalInterface

class PaypalPayment(object):
    implements(IPaymentMethod, IPaypalPayment)
    adapts(Interface)
    
    title = _(u'Paypal')
    description = _('Payment using Paypal')
    icon = u'++resource++pcommerce_payment_paypal_icon.gif'
    logo = u'++resource++pcommerce_payment_paypal_logo.gif'
    
    def __init__(self, context):
        self.context = context
        self.props = getToolByName(self.context, 'portal_properties').paypal_properties
        
    def __getattr__(self, name):
        if self.props.hasProperty(name):
            return self.props.getProperty(name)
        raise AttributeError
    
    def mailInfo(self, order, lang=None, customer=False):
        return _('paypal_mailinfo', default=u"Payment processed over Paypal")

    def verifyPayment(self, order):
        """"""
        # TODO: Done before, not yet needed
        return True

    def get_paypal_interface_obj(self):
        context = self.context 
        props = getToolByName(context, 'portal_properties').paypal_properties
        
        #TODO: Need to be moved in configlet with description
        # Enter your test account's API details here. You'll need the 3-token
        # credentials, not the certificate stuff.
        #CONFIG = PayPalConfig(API_USERNAME = "sschuppen.de",
        #                      API_PASSWORD = "117066",
        #                      API_SIGNATURE = "AuyTYUFGIfqpMeM0seVte",
        #                      DEBUG_LEVEL=0)

        CONFIG = PayPalConfig(API_USERNAME = props.api_username,
                      API_PASSWORD = props.api_password,
                      API_SIGNATURE = props.api_signature,
                      API_ENVIRONMENT = props.test and 'SANDBOX' or 'PRODUCTION',
                      DEBUG_LEVEL=0)

        return PayPalInterface(config=CONFIG)
        
    def action(self, order):
        """"""
        url = '%s/' % (self.context.absolute_url())
        props = getToolByName(self.context, 'portal_properties').pcommerce_properties
        props_paypal = getToolByName(self.context, 'portal_properties').paypal_properties
        portal_state = getMultiAdapter((self.context, self.context.REQUEST), name=u'plone_portal_state')
        lang = self.context.REQUEST.get('LANGUAGE', portal_state.default_language())
        price = CurrencyAware(order.totalincl)
        interface = self.get_paypal_interface_obj()
        cart = IShoppingCart(self.context)
        cart_products = cart.getProducts()
        product_titles = []
        for product in cart_products:
            product_titles.append(product['title'] + ' ' )
        button_params = {
            'BUTTONCODE': 'ENCRYPTED',
            'BUTTONTYPE': 'BUYNOW',
            'BUTTONSUBTYPE': 'SERVICES',
            'BUYNOWTEXT': 'PAYNOW',
            'L_BUTTONVAR0': 'notify_url=%s' % props_paypal.ipn_notify_url,
            'L_BUTTONVAR1': 'amount=%.2f' % float(price.getRoundedValue()),
            'L_BUTTONVAR2': 'item_name=%s' % "".join(product_titles),
            'L_BUTTONVAR3': 'item_number=%s' % order.orderid,
            'L_BUTTONVAR4': 'return=%s' % url + 'payment.success',
            'L_BUTTONVAR5': 'cancel_return=%s' % url + 'payment.cancel',
            'L_BUTTONVAR6': 'no_shipping=1',
            'L_BUTTONVAR7': 'no_note=1',
            'L_BUTTONVAR8': 'rm=1',
            'L_BUTTONVAR11': 'currency_code=EUR'
        }
        response = interface.bm_create_button(**button_params)
        return response.EMAILLINK
