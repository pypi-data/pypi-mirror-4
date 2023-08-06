from saml2 import samlp, sigver

__author__ = 'rolandh'

SIGNED = "saml_signed.xml"
UNSIGNED = "saml_unsigned.xml"
FALSE_SIGNED = "saml_false_signed.xml"
SIMPLE_SAML_PHP_RESPONSE = "simplesamlphp_authnresponse.xml"

xml_response = open(SIGNED).read()
response = samlp.response_from_string(xml_response)
assertion = response.assertion[0]
certs = sigver.cert_from_instance(assertion)
assert len(certs) == 1
