from saml2.saml import assertion_from_string
from saml2.samlp import Response, response_from_string
from saml2 import saml, sigver, class_name
from saml2.s_utils import factory, do_attribute_statement
from saml2.sigver import get_xmlsec_cryptobackend

__author__ = 'rolandh'

PUB_KEY = "test.pem"
PRIV_KEY = "test.key"

crypto = get_xmlsec_cryptobackend(search_paths=["/opt/local/bin"])
sec = sigver.SecurityContext(crypto, key_file=PRIV_KEY,
                             cert_file=PUB_KEY, debug=1)

_assertion = factory(saml.Assertion,
                     version="2.0",
                     id="11111",
                     issue_instant="2009-10-30T13:20:28Z",
                     signature=sigver.pre_signature_part("11111", 
                                                         sec.my_cert, 1),
                     attribute_statement=do_attribute_statement(
                         {("", "", "surName"): ("Foo", ""),
                          ("", "", "givenName"): ("Bar", "")}))

response = factory(Response,
                   assertion=_assertion,
                   id="22222",
                   signature=sigver.pre_signature_part("22222", sec.my_cert))

to_sign = [(_assertion, _assertion.id, ''),
           (response, response.id, '')]

print "**UNSIGNED RESPONSE*********** (type %s)" % (type(response))
print response
s_response = sec.multiple_signatures("%s" % response, to_sign)
print "***SIGNED RESPONSE********** (type %s)" % (type(s_response))
print s_response

assert s_response is not None
response = response_from_string(s_response)
print "**PARSED SIGNED RESPONSE*********** (type %s)" % (type(response))
print response
item = sec.check_signature(response, class_name(response), s_response,
                           must=True)
assert isinstance(item, Response)
assert item.id == "22222"

s_assertion = str(response.assertion[0])

print "***SIGNED_ASSERTION********** (type %s)" % (type(s_assertion))
print s_assertion
print "*************"

ass = assertion_from_string(s_assertion)
print "**PARSED SIGNED ASSERTION*********** (type %s)" % (type(ass))
print ass
ci = "".join(sigver.cert_from_instance(ass)[0].split())
assert ci == sec.my_cert

assert ass.version == "2.0"
assert ass.id == "11111"

s_ass = item.assertion[0]
res = sec.check_signature(s_ass, class_name(s_ass), s_response, must=True)
assert res
res = sec._check_signature(s_response, s_ass, class_name(s_ass), s_response)
assert res