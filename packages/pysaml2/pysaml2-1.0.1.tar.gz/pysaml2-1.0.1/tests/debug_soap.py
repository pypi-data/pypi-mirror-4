from saml2 import BINDING_SOAP
from saml2.server import Server

__author__ = 'rolandh'

txt = """<?xml version='1.0' encoding='UTF-8'?>
<ns0:Envelope xmlns:ns0="http://schemas.xmlsoap.org/soap/envelope/" ><ns0:Body>
<ns0:LogoutRequest xmlns:ns0="urn:oasis:names:tc:SAML:2.0:protocol" xmlns:ns1="urn:oasis:names:tc:SAML:2.0:assertion" Destination="http://localhost:8088/logout_soap" ID="id-29c2924575e4868be784e75f90cc4cc0" IssueInstant="2013-01-05T09:25:48Z" Version="2.0"><ns1:Issuer Format="urn:oasis:names:tc:SAML:2.0:nameid-format:entity">http://lingon.ladok.umu.se:8087/sp.xml</ns1:Issuer><ns1:NameID>id-914783631df0102d24fed9904d0b1738</ns1:NameID></ns0:LogoutRequest></ns0:Body></ns0:Envelope>"""

server = Server("idp_all_conf")

req_info = server.parse_logout_request(txt, BINDING_SOAP)
