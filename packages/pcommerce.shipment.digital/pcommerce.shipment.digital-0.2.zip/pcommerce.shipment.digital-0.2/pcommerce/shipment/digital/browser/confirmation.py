from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from pcommerce.shipment.digital.browser.base import DigitalBase

class DigitalConfirmation(DigitalBase):
    template = ViewPageTemplateFile('confirmation.pt')
