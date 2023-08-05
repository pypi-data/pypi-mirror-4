# -*- coding: utf-8 -*-
import os
from datetime import datetime, date, timedelta
from pyxmli import (Invoice, Group, Line, Tax, Discount, Address, Payment,
                    DeliveryMethod, INVOICE_PAID, RATE_TYPE_FIXED,
                    RATE_TYPE_PERCENTAGE, DELIVERY_METHOD_EMAIL)
from pyxmli.xmldsig import verify



'''
XMLi is an open source invoice serialization format.
PyXMLI attempts to reproduce its structure and the container pattern
it's based on.

    Invoice
        Group
            Line
                Tax
                Discount
'''

invoice = Invoice(identifier='123',
                  name="Online shopping on Guitar Heroes Store",
                  description="Perfect gears for a quick jam.",
                  currency="USD",
                  status=INVOICE_PAID,
                  date=datetime.now(),
                  due_date=date.today() + timedelta(days=60),
                  mentions='Guitar Heros Store LLC.',
                  terms='All order changes or cancellations should be ' \
                  'reported prior to shipping and by phone on ' \
                  '1-555-555-5555. Email is not accepted.', #optional
                  domain="greendizer.com")

#Seller
invoice.seller.identifier = '12345'
invoice.seller.name = "Guitar Heroes Store"
invoice.seller.email = "contact@guitar-heroes-store.com"
invoice.seller.address = Address(street_address="Boulevard du Lido",
                                 city="Casablanca",
                                 zipcode="20100",
                                 country="MA")

#Billing contact and address
invoice.buyer.identifier = '12345'
invoice.buyer.name = "Stevie Ray Vaughan"
invoice.buyer.email = "stevie@ray-vaughan.com"
invoice.buyer.address = Address(street_address="E Riverside Dr",
                                city="Austin",
                                state='TX',
                                zipcode="78704",
                                country="US")

#Shipping recipient and address (optional)
invoice.shipping.recipient = invoice.buyer

#Groups allow you to structure your invoice and organize your items 
#in categories. An invoice must at least have one Group instance.
group = Group()
invoice.groups.append(group)

'''
About taxes and discounts:

Every component - and especially taxes and discounts - of the XMLi format has 
been designed to be flexible enough to cover a wide range of countries, 
industries and different scenarios.

Things you should know:
    1. Both are applied on a line per line basis
    2. Both are expressed as a fixed value, or as a percentage of the gross
        total of the line 
    3. Taxes are calculated on the amount left after the discounts
        have been applied
    4. You can't express a discount by adding an invoice line with
        a negative total
'''

#Define a Discount instance that we'll attach to one or many invoice lines
promo_code = Discount(name='Promo Code',
                      description="$30 discount",
                      rate=30,
                      rate_type=RATE_TYPE_FIXED)

#Define a Tax instance that we'll attach to one or many invoice lines  
vat = Tax(name='VAT',
          description="Sales Tax",
          rate=8.25,
          rate_type=RATE_TYPE_PERCENTAGE)

#Instantiate a line to describe an invoice item, and add it to a group
group.lines.append(Line(name="SRV Fender Stratocaster",
                        description="SRV's collaboration with Fender",
                        quantity=1, unit_price=2399.99))

group.lines.append(Line(name="Marshall AS100D Amplifier",
                        description='50 Watt + 50 Watt, 2x8" combo with ' \
                        'two high fidelity, polymer dome tweeters.',
                        quantity=1, unit_price=699.99))

group.lines.append(Line(name="Dunlop JH1B wah-wah pedal",
                        description='Reproduce the famous tones of Hendrix ' \
                        'wah solos from the late 60s.',
                        quantity=1, unit_price=129.99))

#Attach taxes and discounts to lines 
for line in group.lines:
    line.taxes.append(vat)
    line.discounts.append(promo_code)
    
invoice.payments.append(Payment(amount=invoice.total,))

invoice.deliveries.append(DeliveryMethod(method=DELIVERY_METHOD_EMAIL))

#Sign the invoice using RSA encryption keys ('ssh-keygen -t rsa -b 1024')
keys_dir = os.path.join(os.path.dirname(__file__), 'tests')
signed = invoice.to_signed_str(open(os.path.join(keys_dir, 'id_rsa'), 'rb'), 
                               open(os.path.join(keys_dir, 'id_rsa.pub'), 'rb'))
print signed
print verify(signed)
