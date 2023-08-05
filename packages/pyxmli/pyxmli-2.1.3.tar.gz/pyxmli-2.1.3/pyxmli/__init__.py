# -*- coding: utf-8 -*-
__all__ = ('quantize', 'CURRENCIES', 'INVOICE_DUE', 'INVOICE_CANCELED',
           'INVOICE_PAID', 'INVOICE_IRRECOVERABLE', 'UNITS', 'RATE_TYPE_FIXED',
           'RATE_TYPE_PERCENTAGE', 'COUNTRIES',
           'DELIVERY_METHOD_EMAIL', 'DELIVERY_METHOD_SNAILMAIL',
           'DELIVERY_METHOD_SMS', 'DELIVERY_METHOD_STATUS_PENDING',
           'DELIVERY_METHOD_STATUS_SENT', 'DELIVERY_METHOD_STATUS_BOUNCED',
           'DELIVERY_METHOD_STATUS_CONFIRMED', 'PAYMENT_METHOD_CARD',
           'PAYMENT_METHOD_CHEQUE', 'PAYMENT_METHOD_CASH', 'Interval',
           'Address', 'Contact', 'Shipping', 'Invoice', 'DeliveryMethod',
           'Payment', 'Group', 'Line', 'Discount', 'Tax',
           'PyXMLiError', 'InvoiceError', 'GroupError', 'DeliveryMethodError',
           'PaymentError', 'LineError', 'TreatmentError')


import re
from xml.dom.minidom import Document
from datetime import datetime, date, time
from decimal import (Decimal, getcontext, Context, ROUND_HALF_UP,
                     DivisionByZero, InvalidOperation)
from pyxmli import version as PYXMLI_VERSION
try:
    from cStringIO import cStringIO as StringIO
except ImportError:
    from StringIO import StringIO


INFINITY = Decimal('inf')
ZERO = Decimal('0')
PRECISION = 2

'''
Important note:
PyXMLi rounds up line totals separately. This makes it easier for your customers
to understand how you got to a total.
'''
def quantize(d, places=None):
    if type(d) != Decimal:
        d = Decimal(str(d))
    global PRECISION
    places = places or PRECISION
    return d.quantize(Decimal(str(10 ** -abs(places))),
                      rounding=ROUND_HALF_UP).normalize()


XMLi_VERSION = '2.0'
DEFAULT_NAMESPACE = 'http://xmli.org'
AGENT = "PyXMLi %s" % PYXMLI_VERSION.VERSION
CURRENCIES = ['AED', 'ALL', 'ANG', 'ARS', 'AUD', 'AWG', 'BBD', 'BDT', 'BGN',
              'BHD', 'BIF', 'BMD', 'BND', 'BOB', 'BRL', 'BTN', 'BWP', 'BYR',
              'BZD', 'CAD', 'CHF', 'CLP', 'CNY', 'COP', 'CRC', 'CUP', 'CVE',
              'CZK', 'DJF', 'DKK', 'DOP', 'DZD', 'ECS', 'EEK', 'EGP', 'ERN',
              'ETB', 'EUR', 'FJD', 'GBP', 'GHC', 'GIP', 'GMD', 'GNF', 'GTQ',
              'GYD', 'HKD', 'HNL', 'HRK', 'HTG', 'HUF', 'IDR', 'ILS', 'INR',
              'IQD', 'IRR', 'ISK', 'JMD', 'JOD', 'JPY', 'KES', 'KHR', 'KMF',
              'KPW', 'KRW', 'KWD', 'KYD', 'KZT', 'LAK', 'LBP', 'LKR', 'LRD',
              'LSL', 'LTL', 'LVL', 'LYD', 'MAD', 'MDL', 'MKD', 'MLT', 'MMK',
              'MNT', 'MOP', 'MRO', 'MUR', 'MVR', 'MWK', 'MXN', 'MYR', 'NAD',
              'NGN', 'NIO', 'NOK', 'NPR', 'NZD', 'OMR', 'PAB', 'PEN', 'PGK',
              'PHP', 'PKR', 'PLN', 'PYG', 'QAR', 'RON', 'RUB', 'RWF', 'SAR',
              'SBD', 'SCR', 'SDG', 'SEK', 'SGD', 'SHP', 'SIT', 'SKK', 'SLL',
              'SOS', 'STD', 'SVC', 'SYP', 'SZL', 'THB', 'TND', 'TOP', 'TRY',
              'TTD', 'TWD', 'TZS', 'UAH', 'UGX', 'USD', 'UYU', 'VEB', 'VND',
              'VUV', 'WST', 'XAF', 'XAG', 'XCD', 'XCP', 'XOF', 'XPD', 'XPF',
              'XPT', 'YER', 'ZAR', 'ZMK', 'ZWD']
INVOICE_PAID = 'paid'
INVOICE_DUE = "due"
INVOICE_CANCELED = "canceled"
INVOICE_IRRECOVERABLE = "irrecoverable"
UNITS = ['BO', 'CL', 'CMK', 'CMQ', 'CM', 'CT', 'DL', 'DM', 'E4', 'CQ', 'GAL',
         'GRM', 'TB', 'HUR', 'KGM', 'KM', 'LTR', 'MGM', 'MLT', 'MMT', 'MTK',
         'MTR', 'NT', 'PK', 'RO', 'TNE', 'ZZ']
RATE_TYPE_FIXED = "fixed"
RATE_TYPE_PERCENTAGE = "percentage"
COUNTRIES = ["AF", "AX", "AL", "DZ", "AS", "AD", "AO", "AI", "AQ", "AG", "AR",
             "AM", "AW", "AU", "AT", "AZ", "BS", "BH", "BD", "BB", "BY", "BE",
             "BZ", "BJ", "BM", "BT", "BO", "BA", "BW", "BV", "BR", "IO", "BN",
             "BG", "BF", "BI", "KH", "CM", "CA", "CV", "KY", "CF", "TD", "CL",
             "CN", "CX", "CC", "CO", "KM", "CG", "CD", "CK", "CR", "CI", "HR",
             "CU", "CY", "CZ", "DK", "DJ", "DM", "DO", "EC", "EG", "SV", "GQ",
             "ER", "EE", "ET", "FK", "FO", "FJ", "FI", "FR", "GF", "PF", "TF",
             "GA", "GM", "GE", "DE", "GH", "GI", "GR", "GL", "GD", "GP", "GU",
             "GT", "GG", "GN", "GW", "GY", "HT", "HM", "HN", "HK", "HU", "IS",
             "IN", "ID", "IR", "IQ", "IE", "IM", "IL", "IT", "JM", "JP", "JE",
             "JO", "KZ", "KE", "KI", "KW", "KG", "LA", "LV", "LB", "LS", "LR",
             "LY", "LI", "LT", "LU", "MO", "MK", "MG", "MW", "MY", "MV", "ML",
             "MT", "MH", "MQ", "MR", "MU", "YT", "MX", "FM", "MD", "MC", "MN",
             "ME", "MS", "MA", "MZ", "MM", "NA", "NR", "NP", "NL", "AN", "NC",
             "NZ", "NI", "NE", "NG", "NU", "NF", "MP", "KP", "NO", "OM", "PK",
             "PW", "PS", "PA", "PG", "PY", "PE", "PH", "PN", "PL", "PT", "PR",
             "QA", "RE", "RO", "RU", "RW", "SH", "KN", "LC", "PM", "VC", "WS",
             "SM", "ST", "SA", "SN", "RS", "CS", "SC", "SL", "SG", "SK", "SI",
             "SB", "SO", "ZA", "GS", "KR", "ES", "LK", "SD", "SR", "SJ", "SZ",
             "SE", "CH", "SY", "TW", "TJ", "TZ", "TH", "TL", "TG", "TK", "TO",
             "TT", "TN", "TR", "TM", "TC", "TV", "UG", "UA", "AE", "GB", "US",
             "UM", "UY", "UZ", "VU", "VA", "VE", "VN", "VG", "VI", "WF", "YE",
             "ZM", "ZW"]
DELIVERY_METHOD_EMAIL = 'email'
DELIVERY_METHOD_SNAILMAIL = 'snailmail'
DELIVERY_METHOD_SMS = 'sms'
DELIVERY_METHOD_STATUS_PENDING = 'pending'
DELIVERY_METHOD_STATUS_SENT = 'sent'
DELIVERY_METHOD_STATUS_BOUNCED = 'bounced'
DELIVERY_METHOD_STATUS_CONFIRMED = 'confirmed'
PAYMENT_METHOD_OTHER = 'other'
PAYMENT_METHOD_CARD = 'card'
PAYMENT_METHOD_CHEQUE = 'cheque'
PAYMENT_METHOD_CASH = 'cash'


XML_NAMESPACE_PATTERN = re.compile(r'^(?P<prefix>\w+):' \
                                   '(?P<uri>http(?:s)?:\/\/[a-z.-_]+)$',
                                   re.IGNORECASE)


def to_unicode(text):
    '''
    Converts an input text to a unicode object.
    @param text:object Input text
    @return: unicode
    '''
    return text.decode("UTF-8") if type(text) == str else unicode(text)


def to_byte_string(text):
    '''
    Converts an input text to a unicode object.
    @param text:object Input text
    @return: unicode
    '''
    return text.encode("UTF-8") if type(text) == unicode else str(text)


def is_empty_or_none(s):
    '''
    Returns a value indicating whether the string is empty or none
    @param s:str String to check.
    @return: bool
    '''
    if s is None:
        return True

    try:
        return len(s) == 0
    except:
        return False


def date_to_datetime(d):
    '''
    date to datetime conversion.
    '''
    if isinstance(d, datetime):
        return d

    return datetime.combine(d, time())


def datetime_to_string(d):
    '''
    Gets a string representation of a datetime instance.
    @param date:datetime Datetime instance
    @return: str
    '''
    return d.strftime("%Y-%m-%dT%H:%M:%S%z")


def date_to_string(d):
    '''
    Gets a string representation of a datetime instance.
    @param date:datetime Datetime instance
    @return: str
    '''
    return d.strftime("%Y-%m-%d%z")


class PyXMLiError(Exception):
    pass


class InvoiceError(PyXMLiError):
    pass


class GroupError(PyXMLiError):
    pass


class DeliveryMethodError(PyXMLiError):
    pass


class PaymentError(PyXMLiError):
    pass


class LineError(PyXMLiError):
    pass


class TreatmentError(PyXMLiError):
    pass


class XMLiElement(object):
    '''
    Represents an XMLi element.
    '''
    def _create_text_node(self, root, name, value, cdata=False):
        '''
        Creates and adds a text node
        @param root:Element Root element
        @param name:str Tag name
        @param value:object Text value
        @param cdata:bool A value indicating whether to use CDATA or not.
        @return:Node
        '''
        if is_empty_or_none(value):
            return

        if type(value) == date:
            value = date_to_string(value)

        if type(value) == datetime:
            value = datetime_to_string(value)

        if isinstance(value, Decimal):
            value = "0" if not value else str(value)

        tag = root.ownerDocument.createElement(name)
        value = value.decode('utf-8')
        if cdata:
            tag.appendChild(root.ownerDocument.createCDATASection(value))
        else:
            tag.appendChild(root.ownerDocument.createTextNode(value))

        return root.appendChild(tag)

    def duplicate(self):
        '''
        Returns a copy of the current XMLiElement.
        '''
        raise NotImplementedError('Not Implemented')

    def to_xml(self):
        '''
        Returns a DOM element containing the XML representation of the XMLi
        element.
        @return: Element
        '''
        raise NotImplementedError('Not implemented')

    def to_string(self, indent="", newl="", addindent=""):
        '''
        Returns a string representation of the XMLi element.
        @return: str
        '''
        buf = StringIO()
        self.to_xml().writexml(buf, indent=indent, addindent=addindent,
                               newl=newl)
        return buf.getvalue()

    def __str__(self):
        '''
        Returns a string representation of the XMLi element.
        @return: str
        '''
        return self.to_string()


class ExtensibleXMLiElement(XMLiElement):
    '''
    Represents an XMLi element that can be extended with its own set of
    custom tags.
    '''
    def __init__(self, **kwargs):
        '''
        Initializes a new instance of the ExtensibleXMLiElement class.
        '''
        super(ExtensibleXMLiElement, self).__init__(**kwargs)
        self.__custom_elements = {}

    def __getitem__(self, namespace):
        '''
        Gets the items of a specific namespace.
        @param namespace:XMLNamespace
        @return: dict
        '''
        if not XML_NAMESPACE_PATTERN.match(namespace):
            raise ValueError('Invalid namespace format. Use ' \
                             'myprefix:http://www.example.com''')

        if namespace not in self.__custom_elements:
            self.__custom_elements[namespace] = {}

        return self.__custom_elements[namespace]

    def __delitem__(self, namespace):
        '''
        Deletes the items of a specific namespace.
        @param namespace:XMLNamespace
        @return: dict
        '''
        if namespace not in self.__custom_elements:
            del self.__custom_elements[namespace]

    def __createElementNS(self, root, uri, name, value):
        '''
        Creates and returns an element with a qualified name and a name space
        @param root:Element Parent element
        @param uri:str Namespace URI
        @param tag:str Tag name.
        '''
        tag = root.ownerDocument.createElementNS(to_byte_string(uri),
                                                 to_byte_string(name))
        tag.appendChild(root.ownerDocument
                        .createCDATASection(to_byte_string(value)))
        return root.appendChild(tag)

    def to_xml(self, root):
        '''
        Returns a DOM element contaning the XML representation of the
        ExtensibleXMLiElement
        @param root:Element Root XML element.
        @return: Element
        '''
        if not len(self.__custom_elements):
            return

        for uri, tags in self.__custom_elements.items():
            prefix, url = uri.split(":", 1)
            for name, value in tags.items():
                self.__createElementNS(root, url, prefix + ":" + name, value)

        return root


class Interval(object):
    '''
    Represents an line treatment base interval
    '''
    def __init__(self, lower=0, upper=INFINITY):
        '''
        Initializes a new instance of the Interval class.
        @param lower:float Lower limit
        @param upper:flaot Upper limit
        '''
        self.lower = Decimal(str(lower))
        self.upper = Decimal(str(upper))

    @property
    def amplitude(self):
        '''
        Gets the interval amplitude
        @return: Decimal
        '''
        return self.upper - self.lower

    def to_string(self):
        '''
        Returns an XMLi representation of the interval
        @return: str
        '''
        return "[%s,%s]" % (self.lower,
                            '' if self.upper != INFINITY else self.upper)

    def __str__(self):
        '''
        Returns an XMLi representation of the interval
        @return: str
        '''
        return self.to_string()


class Address(ExtensibleXMLiElement):
    '''
    Represents a postal address
    '''
    def __init__(self, street_address=None, city=None,
                 zipcode=None, state=None, country=None):
        '''
        Initializes a new instance of the Address class.
        @param number:str Street number
        @param street:str Street name
        @param city:str City
        @param zipcode:str Zipcode
        @param state:str State
        @param country:str Country
        '''
        super(Address, self).__init__()
        self.street_address = street_address
        self.city = city
        self.zipcode = zipcode
        self.state = state
        self.__country = None
        if country: self.country = country

    def __set_country(self, value):
        '''
        Sets the country
        @param value:str
        '''
        if value not in COUNTRIES:
            raise ValueError('''Country code must be a valid ISO 3166-1
                            alpha-2 string''')

        self.__country = value

    country = property(lambda self: self.__country, __set_country)

    def duplicate(self):
        '''
        Returns a copy of the current address.
        @returns: Address
        '''
        return self.__class__(street_address=self.street_address,
                              city=self.city, zipcode=self.zipcode,
                              state=self.state, country=self.country)

    def to_xml(self, name="address"):
        '''
        Returns a DOM Element containing the XML representation of the
        address.
        @return:Element
        '''
        for n, v in {"street_address": self.street_address, "city": self.city,
                     "country": self.country}.items():
            if is_empty_or_none(v):
                raise ValueError("'%s' attribute cannot be empty or None." % n)

        doc = Document()
        root = doc.createElement(name)
        self._create_text_node(root, "streetAddress", self.street_address, True)
        self._create_text_node(root, "city", self.city, True)
        self._create_text_node(root, "zipcode", self.zipcode)
        self._create_text_node(root, "state", self.state, True)
        self._create_text_node(root, "country", self.country)
        return root


class Contact(ExtensibleXMLiElement):
    '''
    Represents a contact in Greendizer
    '''
    def __init__(self, name=None, identifier=None, phone=None,
                 require_id=True, address=Address()):
        '''
        Initializes a new instance of the Contact Element
        @param name:str Contact name
        @param identifier:str Contact id
        @param phone:str Contact phone number
        @param address:Address Contact address
        '''
        super(Contact, self).__init__()
        self.__require_id = require_id
        self.name = name
        self.phone = phone
        self.__identifier = None
        if identifier:
            self.identifier = identifier
        self.address = address

    def __set_identifier(self, value):
        '''
        Sets the ID of the contact
        @param value:str
        '''
        if is_empty_or_none(value):
            raise ValueError("Invalid identifier")

        self.__identifier = value

    identifier = property(lambda self: self.__identifier, __set_identifier)

    def duplicate(self):
        '''
        Returns a copy of the current contact element.
        @returns: Contact
        '''
        return self.__class__(name=self.name, identifier=self.identifier,
                              phone=self.phone, require_id=self.__require_id,
                              address=self.address.duplicate())

    def to_xml(self, tag_name="buyer"):
        '''
        Returns an XMLi representation of the object.
        @param tag_name:str Tag name
        @return: Element
        '''
        for n, v in {"name": self.name, "address": self.address}.items():
            if is_empty_or_none(v):
                raise ValueError("'%s' attribute cannot be empty or None." % n)

        if self.__require_id and is_empty_or_none(self.identifier):
            raise ValueError("identifier attribute cannot be empty or None.")

        doc = Document()
        root = doc.createElement(tag_name)
        self._create_text_node(root, "id", self.identifier)
        self._create_text_node(root, "name", self.name, True)
        if self.phone:
            self._create_text_node(root, "phone", self.phone, True)
        root.appendChild(self.address.to_xml())
        return root


class Shipping(ExtensibleXMLiElement):
    '''
    Represents the shipping details of the invoice.
    '''
    def __init__(self, recipient=Contact(require_id=False)):
        '''
        Initializes a new instance of the Shipping class.
        @param address:Address Shipping address
        '''
        super(Shipping, self).__init__()
        self.recipient = recipient

    def to_xml(self):
        '''
        Returns an XMLi representation of the shipping details.
        @return: Element
        '''
        for n, v in {"recipient": self.recipient}.items():
            if is_empty_or_none(v):
                raise ValueError("'%s' attribute cannot be empty or None." % n)

        doc = Document()
        root = doc.createElement("shipping")
        root.appendChild(self.recipient.to_xml("recipient"))
        return root


class Invoice(ExtensibleXMLiElement):
    '''
    Represents an Invoice object in the XMLi.
    '''
    def __init__(self, identifier=None, name=None, description=None,
                 currency=None, status=INVOICE_DUE, date=date.today(),
                 due_date=None, terms=None, seller=Contact(),
                 buyer=Contact(), shipping=None, mentions=None, domain=None,):
        '''
        Initializes a new instance of the Invoice class.
        @param identifier:str Invoice ID
        @param name:str Invoice name.
        @param description:str Invoice description.
        @param currency:str Currency
        @param status:str Invoice status.
        @param date:datetime Invoice date.
        @param due_date:date Invoice's due date.
        @param terms:str Specific terms of the invoice
        @param seller:Contact Sender of the invoice
        @param buyer:Contact Recipient of the invoice.
        @param shipping:Shipping Shipping details of the invoice.
        @param mentions:str Mandatory legal mentions on the invoice.
        @param domain:str Domain owning this invoice
        sending a notification to a customer or not. 
        '''
        self.__identifier = None
        self.__date = None
        self.__due_date = None
        self.__name = None
        self.__description = None
        self.__currency = None
        self.__deliveries = []
        self.__groups = []
        self.__payments = []

        super(Invoice, self).__init__()
        self.__shipping = shipping
        if identifier:
            self.identifier = identifier
        if name:
            self.name = name
        if currency:
            self.currency = currency
        self.seller = seller
        self.buyer = buyer
        self.description = description
        self.status = status
        self.date = date
        self.due_date = due_date or (self.date if type(self.date) == date else
                                     date.date())
        self.terms = terms
        self.mentions = mentions
        self.domain = domain

    @property
    def groups(self):
        '''
        Gets the list of groups
        @return: list
        '''
        return self.__groups

    @property
    def deliveries(self):
        '''
        Gets the list of delivery modes configured for this invoice.
        @return: list
        '''
        return self.__deliveries

    @property
    def payments(self):
        '''
        Gets the list of payments.
        @return: list
        '''
        return self.__payments

    @property
    def shipping(self):
        '''
        Gets the shipping details of the invoice.
        '''
        if not self.__shipping:
            self.__shipping = Shipping()
        return self.__shipping

    def __set_identifier(self, value):
        '''
        Sets the ID of the invoice.
        @param value:str
        '''
        if not value or not len(value):
            raise ValueError("Invalid invoice ID")

        self.__identifier = value

    def __set_name(self, value):
        '''
        Sets the name of the invoice.
        @param value:str
        '''
        if not value or not len(value):
            raise ValueError("Invalid invoice name")

        self.__name = value

    def __set_status(self, value):
        '''
        Sets the status of the invoice.
        @param value:str
        '''
        if value not in [INVOICE_DUE, INVOICE_PAID, INVOICE_CANCELED,
                         INVOICE_IRRECOVERABLE]:
            raise ValueError("Invalid invoice status")

        self.__status = value

    def __set_date(self, value):
        '''
        Sets the invoice date.
        @param value:datetime
        '''
        value = date_to_datetime(value)
        if value > datetime.now():
            raise ValueError("Date cannot be in the future.")

        if self.__due_date and value.date() > self.__due_date:
            raise ValueError("Date cannot be posterior to the due date.")

        self.__date = value

    def __set_due_date(self, value):
        '''
        Sets the due date of the invoice.
        @param value:date
        '''
        if type(value) != date:
            raise ValueError('Due date must be an instance of date.')

        if self.__date.date() and value < self.__date.date():
            raise ValueError("Due date cannot be anterior to the invoice " \
                             "date.")

        self.__due_date = value

    def __set_currency(self, value):
        '''
        Sets the currency of the invoice.
        @param value:str
        '''
        if value not in CURRENCIES:
            raise ValueError("Currency code must a valid ISO-4214 string")

        self.__currency = value

    @property
    def total_discounts(self):
        '''
        Gets the total amount of discounts of the invoice.
        @return: Decimal
        '''
        return self.compute_discounts()

    def compute_discounts(self, precision=None):
        '''
        Returns the total discounts of this group.
        @param precision: int Number of decimals
        @return: Decimal
        '''
        return sum([group.compute_discounts(precision) for group
                    in self.__groups])

    @property
    def total_taxes(self):
        '''
        Gets the total amount of taxes of the invoice.
        @return: Decimal
        '''
        return self.compute_taxes()

    def compute_taxes(self, precision=None):
        '''
        Returns the total amount of taxes for this group.
        @param precision: int Number of decimal places
        @return: Decimal
        '''
        return sum([group.compute_taxes(precision) for group in self.__groups])

    @property
    def total_payments(self):
        '''
        Gets the total amount of payments of the invoice.
        @return: Decimal
        '''
        return self.compute_payments()

    def compute_payments(self, precision=None):
        '''
        Returns the total amount of payments made to this invoice.
        @param precision:int Number of decimal places
        @return: Decimal
        '''
        return quantize(sum([payment.amount for payment in self.__payments]),
                        precision)

    @property
    def remaining(self):
        '''
        Gets the total remaining of the invoice.
        @returns: Decimal
        '''
        return self.compute_remainings()

    def compute_remainings(self, precision=None):
        '''
        Gets the remaining of the invoice
        @param precision: int Number of decimal places
        @return: Decimal
        '''
        return self.compute_total(precision) - self.compute_payments(precision)

    @property
    def total(self):
        '''
        Gets the total of the invoice.
        @return: Decimal
        '''
        return self.compute_total()

    def compute_total(self, precision=None):
        '''
        Gets the total of the invoice with a defined decimal precision
        @param precision: int Number of decimal places
        @return: Decimal
        '''
        return quantize(sum([group.compute_total(precision) for group
                             in self.__groups]), places=precision) or ZERO

    identifier = property(lambda self: self.__identifier, __set_identifier)
    name = property(lambda self: self.__name, __set_name)
    status = property(lambda self: self.__status, __set_status)
    currency = property(lambda self: self.__currency, __set_currency)
    date = property(lambda self: self.__date, __set_date)
    due_date = property(lambda self: self.__due_date, __set_due_date)

    def duplicate(self):
        '''
        Returns a copy of the current group, including its lines.
        @returns: Group
        '''
        instance = self.__class__(identifier=self.identifier,
                                  name=self.name, description=self.description,
                                  currency=self.currency, status=self.status,
                                  date=self.date, due_date=self.due_date,
                                  terms=self.terms,
                                  seller=self.seller.duplicate(),
                                  buyer=self.buyer.duplicate(),
                                  shipping=self.shipping.duplicate(),
                                  mentions=self.mentions,)
        for group in self.groups:
            instance.groups.append(group.duplicate())
        for method in self.deliveries:
            instance.deliveries.append(method.duplicate())
        for payment in self.payments:
            instance.payments.append(payment.duplicate())

        return instance

    def to_xml(self):
        '''
        Returns a DOM element containing the XML representation of the invoice
        @return:Element
        '''
        if not len(self.groups):
            raise InvoiceError("An invoice must have at least one group " \
                                   "of lines.")

        for n, v in {"identifier": self.identifier,
                     "name": self.name, "currency": self.currency,
                     "seller": self.seller, "buyer":self.buyer,
                     "status": self.status, "date": self.date,
                     "due_date": self.due_date, "identifier": self.identifier,
                     "mentions": self.mentions, 'domain': self.domain}.items():
            if is_empty_or_none(v):
                raise InvoiceError("'%s' attribute cannot be empty or " \
                                       "None." % n)

        total_invoice = self.total
        total_payments = sum([payment.amount for payment in self.payments])
        if total_payments > total_invoice:
            raise InvoiceError('The sum of the payments declared ' \
                                   '(%f %s) can\'t be superior to the ' \
                                   'total of the invoice (%f %s).' %
                                   (total_payments, self.currency,
                                    total_invoice, self.currency))
        if self.status == INVOICE_PAID and total_payments < total_invoice:
            raise InvoiceError('The invoice can only be marked as paid ' \
                                   'if the sum of its payments (%f %s) is ' \
                                   'equal to its total (%f %s).' %
                                   (total_payments, self.currency,
                                    total_invoice, self.currency))

        doc = Document()
        root = doc.createElement("invoice")
        root.setAttribute('xmlns', DEFAULT_NAMESPACE)
        root.setAttribute("domain", self.domain)
        root.setAttribute("version", XMLi_VERSION)
        root.setAttribute("agent", AGENT)

        #Adding custom elements
        super(Invoice, self).to_xml(root)

        self._create_text_node(root, "id", self.identifier)
        self._create_text_node(root, "name", self.name, True)
        self._create_text_node(root, "description", self.description, True)
        self._create_text_node(root, "date", self.date)
        self._create_text_node(root, "dueDate", self.due_date)
        self._create_text_node(root, "currency", self.currency)
        self._create_text_node(root, "status", self.status)
        root.appendChild(self.seller.to_xml("seller"))
        root.appendChild(self.buyer.to_xml("buyer"))
        if self.__shipping:
            root.appendChild(self.shipping.to_xml())
        self._create_text_node(root, "terms", self.terms, True)
        self._create_text_node(root, "mentions", self.mentions, True)

        if len(self.__payments):
            payments = doc.createElement("payments")
            for payment in self.__payments:
                payments.appendChild(payment.to_xml())
            root.appendChild(payments)

        if len(self.deliveries):
            deliveries = doc.createElement('deliveries')
            for delivery in self.__deliveries:
                deliveries.appendChild(delivery.to_xml())
            root.appendChild(deliveries)

        body = doc.createElement("body")
        root.appendChild(body)

        groups = doc.createElement("groups")
        body.appendChild(groups)
        for group in self.__groups:
            if not issubclass(group.__class__, Group):
                raise InvoiceError('group of type %s is not an instance ' \
                                       'or a subclass of %s' %
                                       (group.__class__.__name__,
                                        Group.__name__))
            groups.appendChild(group.to_xml())

        return root

    def to_signed_str(self, private, public, passphrase=None):
        '''
        Returns a signed version of the invoice.
        @param private:file Private key file-like object
        @param public:file Public key file-like object
        @param passphrase:str Private key passphrase if any.
        @return: str
        '''
        from pyxmli import xmldsig
        try:
            from Crypto.PublicKey import RSA
        except ImportError:
            raise ImportError('PyCrypto 2.5 or more recent module is ' \
                              'required to enable XMLi signing.\n' \
                              'Please visit: http://pycrypto.sourceforge.net/')
            
        if not isinstance(private, RSA._RSAobj):
            private = RSA.importKey(private.read(), passphrase=passphrase)
        
        if not isinstance(public, RSA._RSAobj):
            public = RSA.importKey(public.read())
            
        return to_unicode(xmldsig.sign(to_byte_string(self.to_string()),
                                       private, public))


class DeliveryMethod(ExtensibleXMLiElement):
    '''
    Represents an invoice deliveries method
    '''
    def __init__(self, method=DELIVERY_METHOD_EMAIL,
                 status=DELIVERY_METHOD_STATUS_PENDING,
                 date=datetime.utcnow(), ref=None):
        super(DeliveryMethod, self).__init__()
        self.__method = method
        self.__status = status
        self.__date = date
        self.ref = ref

    def __set_method(self, value):
        '''
        Sets the method to use.
        @param value: str
        '''
        if value not in [DELIVERY_METHOD_EMAIL, DELIVERY_METHOD_SMS,
                         DELIVERY_METHOD_SNAILMAIL]:
            raise ValueError("Invalid deliveries method '%s'" % value)

        self.__method = value

    def __set_status(self, value):
        '''
        Sets the deliveries status of this method.
        @param value: str
        '''
        if value not in [DELIVERY_METHOD_STATUS_PENDING,
                         DELIVERY_METHOD_STATUS_SENT,
                         DELIVERY_METHOD_STATUS_CONFIRMED,
                         DELIVERY_METHOD_STATUS_BOUNCED]:
            raise ValueError("Invalid deliveries method status '%s'" % value)

        self.__status = value

    def __set_date(self, value):
        '''Sets at which the status changed for the last time.'''
        self.__date = value

    method = property(lambda self: self.__method, __set_method)
    status = property(lambda self: self.__status, __set_status)
    date = property(lambda self: self.__date, __set_date)

    def duplicate(self):
        '''
        Returns a copy of this deliveries method.
        @return: DeliveryMethod
        '''
        return self.__class__(self.method, self.status, self.date, self.ref)

    def to_xml(self):
        '''
        Returns a DOM representation of the deliveries method
        @returns: Element
        '''
        for n, v in { "method": self.method, "status": self.status,
                     "date":self.date}.items():
            if is_empty_or_none(v):
                raise DeliveryMethodError("'%s' attribute cannot be " \
                                       "empty or None." % n)

        doc = Document()
        root = doc.createElement("delivery")
        super(DeliveryMethod, self).to_xml(root)
        self._create_text_node(root, "method", self.method)
        self._create_text_node(root, "status", self.status)
        self._create_text_node(root, "reference", self.ref, True)
        self._create_text_node(root, "date", self.date)
        return root


class Payment(ExtensibleXMLiElement):
    '''
    Represents a payment recorded for an invoice.
    '''
    def __init__(self, amount=None, method=PAYMENT_METHOD_OTHER,
                 ref=None, date=datetime.now()):
        '''
        Initializes a new instance of the Payment class.
        '''
        super(Payment, self).__init__()
        self.__amount = None
        if amount:
            self.amount = amount
        self.__method = method
        self.method = method
        self.ref = ref
        self.date = date

    def __set_amount(self, value):
        '''
        Sets the amount of the payment operation.
        @param value:float
        '''
        try:
            self.__amount = quantize(Decimal(str(value)))
        except:
            raise ValueError('Invalid amount value')

    def __set_method(self, value):
        '''
        Sets the amount of the payment.
        '''
        if value not in [PAYMENT_METHOD_OTHER, PAYMENT_METHOD_CARD,
                         PAYMENT_METHOD_CHEQUE, PAYMENT_METHOD_CASH, ]:
            raise ValueError('Invalid amount value')

        self.__method = value

    def __set_date(self, value):
        '''
        Sets the date of the payment.
        @param value:datetime
        '''
        if not issubclass(value.__class__, date):
            raise ValueError('Invalid date value')

        self.__date = value

    amount = property(lambda self: self.__amount, __set_amount)
    method = property(lambda self: self.__method, __set_method)
    date = property(lambda self: self.__date, __set_date)

    def duplicate(self):
        '''
        Returns a copy of the current group, including its lines.
        @returns: Group
        '''
        return self.__class__(amount=self.amount, date=self.date,
                              method=self.method, ref=self.ref)

    def to_xml(self):
        '''
        Returns a DOM representation of the payment.
        @return: Element
        '''
        for n, v in { "amount": self.amount, "date": self.date,
                     "method":self.method}.items():
            if is_empty_or_none(v):
                raise PaymentError("'%s' attribute cannot be empty or " \
                                       "None." % n)

        doc = Document()
        root = doc.createElement("payment")
        super(Payment, self).to_xml(root)
        self._create_text_node(root, "amount", self.amount)
        self._create_text_node(root, "method", self.method)
        self._create_text_node(root, "reference", self.ref, True)
        self._create_text_node(root, "date", self.date)
        return root


class Group(ExtensibleXMLiElement):
    '''
    Represents a group of lines in the XMLi.
    '''
    def __init__(self, name="", description=""):
        '''
        Initializes a new instance of the Group class.
        @param name:str Group name.
        @param description:str Group description.
        '''
        super(Group, self).__init__()
        self.name = name
        self.description = description
        self.__lines = []

    @property
    def lines(self):
        '''
        Gets the list of lines.
        @return: list
        '''
        return self.__lines

    @property
    def total_discounts(self):
        '''
        Gets the total amount of discounts of the group.
        @return: Decimal
        '''
        return self.compute_discounts()

    def compute_discounts(self, precision=None):
        '''
        Returns the total amount of discounts of this group.
        @param precision:int Total amount of discounts
        @return: Decimal
        '''
        return sum([line.compute_discounts(precision) for line in self.__lines])

    @property
    def total_taxes(self):
        '''
        Gets the total amount of taxes of the group.
        @return: Decimal
        '''
        return self.compute_taxes()

    def compute_taxes(self, precision=None):
        '''
        Returns the total amount of taxes of this group.
        @param precision:int Total amount of discounts
        @return: Decimal
        '''
        return sum([line.compute_taxes(precision) for line in self.__lines])

    @property
    def total(self):
        '''
        Gets the total of the group.
        @return: Decimal
        '''
        return self.compute_total()

    def compute_total(self, precision=None):
        '''
        Gets the total of the invoice with a defined decimal precision
        @param precision: int Number of decimal places
        @return: Decimal
        '''
        return quantize(sum([line.compute_total(precision) for line
                             in self.__lines]), places=precision) or ZERO

    def duplicate(self):
        '''
        Returns a copy of the current group, including its lines.
        @returns: Group
        '''
        instance = self.__class__(name=self.name, description=self.description)
        for line in self.lines:
            instance.lines.append(line.duplicate())
        return instance

    def to_xml(self):
        '''
        Returns a DOM representation of the group.
        @return: Element
        '''
        if not len(self.lines):
            raise GroupError("A group must at least have one line.")

        doc = Document()
        root = doc.createElement("group")
        super(Group, self).to_xml(root)
        self._create_text_node(root, "name", self.name, True)
        self._create_text_node(root, "description", self.description, True)

        lines = doc.createElement("lines")
        root.appendChild(lines)
        for line in self.__lines:
            if not issubclass(line.__class__, Line):
                raise GroupError('line of type %s is not an instance ' \
                                     'or a subclass of %s' %
                                     (line.__class__.__name__, Line.__name__))
            lines.appendChild(line.to_xml())

        return root


class Line(ExtensibleXMLiElement):
    '''
    Represents an invoice body line.
    '''
    def __init__(self, name=None, description="", unit=None, quantity=0,
                 date=date.today(), unit_price=0, gin=None, gtin=None,
                 sscc=None):
        '''
        Initializes a new instance of the Line class.
        '''
        super(Line, self).__init__()

        self.name = name
        self.description = description
        self.quantity = quantity
        self.date = date
        self.unit_price = unit_price
        self.unit = unit
        self.gin = gin
        self.gtin = gtin
        self.sscc = sscc
        self.__taxes = []
        self.__discounts = []

    @property
    def discounts(self):
        '''
        Gets the list of discounts
        @return: list
        '''
        return self.__discounts

    @property
    def taxes(self):
        '''
        Gets the list of taxes
        @return: list
        '''
        return self.__taxes

    def __set_name(self, value):
        '''
        Sets the line's product or service name.
        @param value:str
        '''
        if not value or not len(value):
            raise ValueError("Invalid product or service name")

        self.__name = value

    def __set_unit(self, value):
        '''
        Sets the unit of the line.
        @param value:str
        '''
        if value in UNITS:
            value = value.upper()

        self.__unit = value

    def __set_quantity(self, value):
        '''
        Sets the quantity
        @param value:str
        '''
        try:
            if value < 0:
                raise ValueError()

            self.__quantity = Decimal(str(value))
        except ValueError:
            raise ValueError("Quantity must be a positive number")

    def __set_unit_price(self, value):
        '''
        Sets the unit price
        @param value:str
        '''
        try:
            if value < 0:
                raise ValueError()

            self.__unit_price = Decimal(str(value))
        except ValueError:
            raise ValueError("Unit Price must be a positive number")

    @property
    def gross(self):
        '''
        Gets the gross total
        @return: Decimal
        '''
        return self.compute_gross()

    def compute_gross(self, precision=None):
        '''
        Returns the gross total of the line with a specific number of decimals
        @param precision: int number of decimal places
        @return: Decimal
        '''
        return quantize(self.unit_price * self.quantity, precision)

    @property
    def total_discounts(self):
        '''
        Gets the total amount of discounts applied to the current line.
        @return: Decimal
        '''
        return self.compute_discounts()

    def compute_discounts(self, precision=None):
        '''
        Returns the total amount of discounts for this line with a specific
        number of decimals.
        @param precision:int number of decimal places
        @return: Decimal
        '''
        gross = self.compute_gross(precision)
        return min(gross,
                   sum([d.compute(gross, precision) for d in self.__discounts]))

    @property
    def total_taxes(self):
        '''
        Gets the total amount of taxes applied to the current line.
        @return: Decimal
        '''
        return self.compute_taxes()

    def compute_taxes(self, precision=None):
        '''
        Returns the total amount of taxes for this line with a specific 
        number of decimals
        @param precision: int Number of decimal places
        @return: Decimal
        '''
        base = self.gross - self.total_discounts
        return quantize(sum([t.compute(base, precision) for t in self.__taxes]),
                        precision)

    @property
    def total(self):
        '''
        Gets the total of the line.
        @return: Decimal
        '''
        return self.compute_total()

    def compute_total(self, precision=None):
        '''
        Gets the total of the invoice with a defined decimal precision
        @param precision: int Number of decimal places
        @return: Decimal
        '''
        return quantize((self.compute_gross(precision) +
                        self.compute_taxes(precision) -
                        self.compute_discounts(precision)),
                        places=precision)

    name = property(lambda self: self.__name, __set_name)
    unit = property(lambda self: self.__unit, __set_unit)
    quantity = property(lambda self: self.__quantity, __set_quantity)
    unit_price = property(lambda self: self.__unit_price, __set_unit_price)

    def duplicate(self):
        '''
        Returns a copy of the current Line, including its taxes and discounts
        @returns: Line.
        '''
        instance = self.__class__(name=self.name, description=self.description,
                                  unit=self.unit, quantity=self.quantity,
                                  date=self.date, unit_price=self.unit_price,
                                  gin=self.gin, gtin=self.gtin, sscc=self.sscc)
        for tax in self.taxes:
            instance.taxes.append(tax.duplicate())
        for discount in self.discounts:
            instance.discounts.append(discount.duplicate())
        return instance

    def to_xml(self):
        '''
        Returns a DOM representation of the line.
        @return: Element
        '''
        for n, v in {"name": self.name, "quantity": self.quantity,
                     "unit_price": self.unit_price}.items():
            if is_empty_or_none(v):
                raise LineError("'%s' attribute cannot be empty or None." %
                                    n)

        doc = Document()
        root = doc.createElement("line")
        super(Line, self).to_xml(root)
        self._create_text_node(root, "date", self.date)
        self._create_text_node(root, "name", self.name, True)
        self._create_text_node(root, "description", self.description, True)
        self._create_text_node(root, "quantity", self.quantity)
        self._create_text_node(root, "unitPrice", self.unit_price)
        self._create_text_node(root, "unit", self.unit)
        self._create_text_node(root, "gin", self.gin)
        self._create_text_node(root, "gtin", self.gtin)
        self._create_text_node(root, "sscc", self.sscc)

        if len(self.__discounts):
            discounts = root.ownerDocument.createElement("discounts")
            root.appendChild(discounts)
            for discount in self.__discounts:
                if not issubclass(discount.__class__, Discount):
                    raise LineError('discount of type %s is not an ' \
                                    'instance or a subclass of %s' %
                                    (discount.__class__.__name__,
                                     Discount.__name__))
                discounts.appendChild(discount.to_xml())

        if len(self.__taxes):
            taxes = root.ownerDocument.createElement("taxes")
            root.appendChild(taxes)
            for tax in self.__taxes:
                if not issubclass(tax.__class__, Tax):
                    raise LineError('tax of type %s is not an instance ' \
                                        'or a subclass of %s' %
                                        (tax.__class__.__name__, Tax.__name__))
                taxes.appendChild(tax.to_xml())

        return root


class Treatment(XMLiElement):
    '''
    Represents a line treatment.
    '''
    def __init__(self, name=None, description=None, rate_type=RATE_TYPE_FIXED,
                 rate=0, interval=None):
        '''
        Initializes a new instance of the Treatment class.
        @param name:str Treatment name.
        @param rate:float Rate level
        @param rate_type:str Rate type
        '''
        super(Treatment, self).__init__()

        self.name = name
        self.description = description
        self.rate = rate
        self.rate_type = rate_type
        self.__interval = interval

    def __set_interval(self, value):
        '''
        Sets the treatment interval
        @param value:Interval
        '''
        if not isinstance(self, Interval):
            raise ValueError("'value' must be of type Interval")

        self.__interval = value

    def __set_name(self, value):
        '''
        Sets the name of the treatment.
        @param value:str
        '''
        if not value or not len(value):
            raise ValueError("Invalid name.")

        self.__name = value

    def __set_rate_type(self, value):
        '''
        Sets the rate type.
        @param value:str
        '''
        if value not in [RATE_TYPE_FIXED, RATE_TYPE_PERCENTAGE]:
            raise ValueError("Invalid rate type.")

        self.__rate_type = value

    def __set_rate(self, value):
        '''
        Sets the rate.
        @param value:float
        '''
        try:
            self.__rate = Decimal(str(value))
        except:
            raise ValueError("invalid rate value.")

    name = property(lambda self: self.__name, __set_name)
    rate_type = property(lambda self: self.__rate_type, __set_rate_type)
    interval = property(lambda self: self.__interval, __set_interval)
    rate = property(lambda self: self.__rate, __set_rate)

    def duplicate(self):
        '''
        Returns a copy of the current treatment.
        @returns: Treatment.
        '''
        return self.__class__(name=self.name, description=self.description,
                              rate_type=self.rate_type, rate=self.rate,
                              interval=self.interval)

    def compute(self, base, precision=None):
        '''
        Computes the amount of the treatment.
        @param base:float Gross
        @return: Decimal
        '''
        if base <= ZERO:
            return ZERO

        if self.rate_type == RATE_TYPE_FIXED:
            if not self.interval or base >= self.interval.lower:
                return quantize(self.rate, precision)
            return ZERO

        if not self.interval:
            return quantize(base * self.rate / 100, precision)

        if base > self.interval.lower:
            base = min(base, self.interval.upper) - self.interval.lower
            return quantize(base * self.rate / 100, precision)

        return ZERO

    def to_xml(self, name):
        '''
        Returns a DOM representation of the line treatment.
        @return: Element
        '''
        for n, v in {"rate_type": self.rate_type,
                     "rate": self.rate,
                     "name": self.name,
                     "description": self.description}.items():
            if is_empty_or_none(v):
                raise TreatmentError("'%s' attribute cannot be empty " \
                                         "or None." % n)

        doc = Document()
        root = doc.createElement(name)
        root.setAttribute("type", self.rate_type)
        root.setAttribute("name", to_byte_string(self.name))
        root.setAttribute("description", to_byte_string(self.description))
        if self.interval:
            root.setAttribute("base", self.interval)
        root.appendChild(doc.createTextNode(to_byte_string(self.rate)))
        return root


class Tax(Treatment):
    '''
    Represents a tax.
    '''
    def to_xml(self):
        '''
        Returns a DOM representation of the tax.
        @return: Element
        '''
        return super(Tax, self).to_xml("tax")

    def to_string(self, **kwargs):
        '''
        Returns a string representation of the tax.
        @return: str
        '''
        return super(Tax, self).to_string("tax", **kwargs)


class Discount(Treatment):
    '''
    Represents a discount.
    '''
    def compute(self, base, *args, **kwargs):
        '''
        Returns the value of the discount.
        @param base:float Computation base.
        @return: Decimal
        '''
        return min(base, super(Discount, self).compute(base, *args, **kwargs))

    def to_xml(self):
        '''
        Returns a DOM representation of the discount.
        @return: Element
        '''
        return super(Discount, self).to_xml("discount")

    def to_string(self, **kwargs):
        '''
        Returns a string representation of the discount.
        @return: str
        '''
        return super(Discount, self).to_string("discount", **kwargs)
