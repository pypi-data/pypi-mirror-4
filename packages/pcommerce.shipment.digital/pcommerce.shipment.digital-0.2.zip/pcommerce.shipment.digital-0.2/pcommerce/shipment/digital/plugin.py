from zope.interface import implements, Interface
from zope.component import adapts

from pcommerce.core import PCommerceMessageFactory as _
from pcommerce.core.interfaces import IShipmentMethod
from pcommerce.shipment.digital.interfaces import IDigitalShipment

class DigitalShipment(object):
    implements(IShipmentMethod, IDigitalShipment)
    adapts(Interface)
    
    title = _('Digital')
    description = _('Instantly setup after successful payment')
    icon = '++resource++pcommerce_shipment_digital_icon.gif'
    logo = '++resource++pcommerce_shipment_digital_logo.png'
    
    def __init__(self, context):
        self.context = context
    
    def mailInfo(self, order, lang=None, customer=False):
        return _('Instantly setup after successful payment')
