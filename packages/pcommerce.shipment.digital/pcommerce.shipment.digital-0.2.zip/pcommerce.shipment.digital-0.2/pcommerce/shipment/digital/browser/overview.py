from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from pcommerce.shipment.digital.browser.base import DigitalBase

class DigitalOverview(DigitalBase):
    template = ViewPageTemplateFile('overview.pt')
