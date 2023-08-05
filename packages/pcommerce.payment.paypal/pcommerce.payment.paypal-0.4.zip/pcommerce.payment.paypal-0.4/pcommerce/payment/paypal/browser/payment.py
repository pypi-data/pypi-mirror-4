from zope.interface import implements

from Products.Five.browser import BrowserView

from pcommerce.core.interfaces import IPaymentView

from pcommerce.payment.paypal.data import PaypalPaymentData

class PaypalPayment(BrowserView):
    implements(IPaymentView)
    
    def __init__(self, payment, request):
        self.payment = payment
        self.context = payment.context
        self.request = request
    
    def validate(self):
        return True
    
    def process(self):
        return PaypalPaymentData()
    
    def renders(self):
        return False
