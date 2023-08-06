__author__ = 'rolandh'

_str = """<ns0:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/"><ns0:Body><ns1:FuddleMuddle xmlns:ns1="http://example.org/"  /></ns0:Body></ns0:Envelope>"""
thingy = """<ns0:LogoutRequest Destination="http://localhost:8088/slo/soap" ID="id-4781b303ef6dcd25c2aca7b72dd9c903" IssueInstant="2013-01-19T09:58:33Z" Version="2.0" xmlns:ns0="urn:oasis:names:tc:SAML:2.0:protocol"><ns1:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity" xmlns:ns1="urn:oasis:names:tc:SAML:2.0:assertion">http://localhost:8087/sp.xml</ns1:Issuer><ns1:NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent" NameQualifier="" SPNameQualifier="http://localhost:8087/sp.xml" xmlns:ns1="urn:oasis:names:tc:SAML:2.0:assertion">8045d671bda47cffc21ceb664aec2bf1befb977a2126a6cf11f3f3377597aa9f</ns1:NameID></ns0:LogoutRequest>"""

DUMMY_NAMESPACE = "http://example.org/"
PREFIX = '<?xml version="1.0" encoding="UTF-8"?>'

i = _str.find(DUMMY_NAMESPACE)
j = _str.rfind("xmlns:", 0, i)
cut1 = _str[j:i+len(DUMMY_NAMESPACE)+1]
_str = _str.replace(cut1, "")
first = _str.find("<%s:FuddleMuddle" % (cut1[6:9],))
last = _str.find(">", first+14)
cut2 = _str[first:last+1]
res = _str.replace(cut2,thingy)
print res
