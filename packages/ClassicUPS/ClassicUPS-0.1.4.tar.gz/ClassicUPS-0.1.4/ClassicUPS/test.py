from pprint import pprint
from ups import UPSConnection

ups = UPSConnection(license_number='4CAB8ABB7BE1346B',
                    user_id='classicspecs',
                    password='classic5S',
                    shipper_number='F75W38',
                    debug=True)
#r = ups.tracking_info('1Z602F9A0306292201')
#print r.delivered

to_addr = {
    'name': 'Jay',
    'address1': '85 n 3rd st',
    'address2': 'suite 112',
    'city': 'brooklyn',
    'state': 'NY',
    'country': 'US',
    'postal_code': '11249',
    'phone': '9198898223',
}

from_addr = {
    'name': 'Jay',
    'address1': '4409 knightsbridge way',
    'city': 'raleigh',
    'state': 'NC',
    'country': 'US',
    'postal_code': '11249',
    'phone': '9192120396',
}
from_addr = to_addr

dimensions = {
    'length': '3',
    'width': '3',
    'height': '3',
}

weight = '1'

#r = ups.create_shipment(from_addr, to_addr, dimensions, weight, reference_numbers=['hello', 'world'], file_format='ZPL')
#r = ups.create_shipment(from_addr, to_addr, dimensions, weight, reference_numbers=['hello', 'world'], file_format='EPL')
r = ups.create_shipment(from_addr, to_addr, dimensions, weight, reference_numbers=['hello'], file_format='EPL', shipping_service='2dayair')

#r.save_html('output/')

fd = open('out.epl', 'wb')
r.save_label(fd)
fd.close()

#pprint(r.confirm_result.dict_response)

#print r.tracking_number
#pprint(r.accept_result.dict_response)
