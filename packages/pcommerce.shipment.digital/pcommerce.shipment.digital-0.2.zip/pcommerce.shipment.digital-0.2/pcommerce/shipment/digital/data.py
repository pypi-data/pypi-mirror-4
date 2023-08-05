from pcommerce.core.data import ShipmentData

def DigitalShipmentData(as_customer=True, address=None):
    data = ShipmentData('pcommerce.shipment.digital')
    return data
