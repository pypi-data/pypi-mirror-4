from saml2.mdstore import MetadataStore
from saml2.saml import Assertion, Issuer
from saml2 import sigver
from saml2 import class_name
from saml2 import time_util
from saml2 import saml, samlp
from saml2.s_utils import factory, do_attribute_statement
from saml2.sigver import xmlsec_version, get_xmlsec_binary, cert_from_instance

__author__ = 'rolandh'

PUB_KEY = "test.pem"
PRIV_KEY = "test.key"

xmlexec = get_xmlsec_binary(["/opt/local/bin"])

md = MetadataStore([saml, samlp], None, xmlexec)
md.load("local", "metadata_cert.xml")

sec = sigver.SecurityContext(xmlexec, key_file=PRIV_KEY,
#                             cert_file=PUB_KEY, debug=1)
                             cert_file=PUB_KEY, debug=1, metadata=md)

_assertion = factory(Assertion, version="2.0", id="11111",
                     issue_instant="2009-10-30T13:20:28Z",
                     signature=sigver.pre_signature_part("11111",
                                                         sec.my_cert, 1),
                     attribute_statement=do_attribute_statement({
                          ("","","surName"): ("Foo",""),
                          ("","","givenName") :("Bar",""),
                          }),
                     issuer=Issuer(text=md.keys()[0])
                    )
ass = _assertion
print ass
sign_ass = sec.sign_assertion_using_xmlsec("%s" % ass,
                                                nodeid=ass.id)
#print sign_ass
sass = saml.assertion_from_string(sign_ass)
#print sass

m_cert = md.certs(_assertion.issuer.text.strip(), "any")
i_cert = cert_from_instance(sass)

assert m_cert == i_cert

assert sass.version == "2.0"
assert sass.id == "11111"
assert time_util.str_to_time(sass.issue_instant)

print xmlsec_version(xmlexec)

item = sec.check_signature(sass, class_name(sass), sign_ass)

assert isinstance(item, saml.Assertion)
