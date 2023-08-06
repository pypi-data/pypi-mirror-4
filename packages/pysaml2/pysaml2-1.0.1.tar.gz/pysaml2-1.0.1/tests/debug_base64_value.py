from saml2 import saml

__author__ = 'rolandh'

BASIC_BASE64_AV = """<?xml version="1.0" encoding="utf-8"?>
<Attribute xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
NameFormat="urn:oasis:names:tc:SAML:2.0:attrname-format:basic"
Name="FirstName">
<AttributeValue
xsi:type="xs:base64Binary">VU5JTkVUVA==</AttributeValue>
</Attribute>"""

attribute = saml.attribute_from_string(BASIC_BASE64_AV)
print attribute
assert attribute.attribute_value[0].text == "VU5JTkVUVA=="
assert attribute.attribute_value[0].get_type() == "xs:base64Binary"
