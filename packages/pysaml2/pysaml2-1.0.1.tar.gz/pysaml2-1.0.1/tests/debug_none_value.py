from saml2.mdie import to_dict, from_dict
from saml2.saml import AttributeValue
from saml2.validate import valid_instance
from saml2  import saml, samlp

__author__ = 'rolandh'

xmlstr = """<ns0:AttributeValue xmlns:ns0="urn:oasis:names:tc:SAML:2.0:assertion">foo</ns0:AttributeValue>"""

xmlstr_none = """<ns0:AttributeValue xmlns:ns0="urn:oasis:names:tc:SAML:2.0:assertion" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"></ns0:AttributeValue>"""

av = saml.attribute_value_from_string(xmlstr_none)

print av

x = valid_instance(av)

# Special case
null = AttributeValue()
null.verify()
print null

av = AttributeValue(2)
av.verify()

print av

onts = {
    saml.NAMESPACE: saml,
    samlp.NAMESPACE: samlp
}
_d = to_dict(null, onts.values())

_av = from_dict(_d, onts)

print _av