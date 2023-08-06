from saml2.sigver import SecurityContext, get_xmlsec_binary

__author__ = 'rolandh'

FALSE_SIGNED = "saml_false_signed.xml"
PUB_KEY = "test.pem"
PRIV_KEY = "test.key"

xmlexec = get_xmlsec_binary(["/opt/local/bin"])
sec = SecurityContext(xmlexec, key_file=PRIV_KEY,
                             cert_file=PUB_KEY, debug=1)

res = sec.correctly_signed_response(open(FALSE_SIGNED).read())

print res