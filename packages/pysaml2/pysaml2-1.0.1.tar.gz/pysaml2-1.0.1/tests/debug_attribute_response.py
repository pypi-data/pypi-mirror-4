from saml2 import config
from saml2.samlp import response_from_string
from saml2.attribute_converter import to_local

__author__ = 'rohe0002'

conf = config.SPConfig()
conf.load_file("server_conf")

xml_response = open("attribute_response.xml").read()
resp = response_from_string(xml_response)

_attr_statem = resp.assertion[0].attribute_statement[0]
attribute_converters = conf._attr[""]["attribute_converters"]

ava = to_local(attribute_converters, _attr_statem)
print ava