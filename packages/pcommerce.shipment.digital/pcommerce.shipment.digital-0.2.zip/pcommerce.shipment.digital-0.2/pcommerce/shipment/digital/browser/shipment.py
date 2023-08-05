from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from pcommerce.shipment.digital.browser.base import DigitalBase
from pcommerce.shipment.digital.data import DigitalShipmentData

class DigitalShipment(DigitalBase):
    
    def renders(self):
        return False
    
    def process(self):
        self.data = DigitalShipmentData()
        props = getToolByName(self.context, 'portal_properties').pcommerce_properties
        self.data.pretaxcharge = props.getProperty('digital_pretaxcharge', 0.0)
        self.data.posttaxcharge = props.getProperty('digital_posttaxcharge', 0.0)
        return self.data
