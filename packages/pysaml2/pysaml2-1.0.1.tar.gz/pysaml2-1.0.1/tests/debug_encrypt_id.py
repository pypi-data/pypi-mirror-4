#!/usr/bin/env python

__author__ = 'rohe0002'

from saml2.encdec import encrypt_id
from saml2 import samlp

prior = open("saml2_response.xml").read()
response = samlp.response_from_string(prior)

XMLSEC = "/opt/local/bin/xmlsec1"
xmltext = encrypt_id(response, XMLSEC, "kalmar2.pem", "ident2")
print xmltext