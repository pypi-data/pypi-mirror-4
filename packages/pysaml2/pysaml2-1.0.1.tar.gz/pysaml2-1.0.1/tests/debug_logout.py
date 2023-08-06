from saml2.samlp import response_from_string
from saml2 import time_util, BINDING_HTTP_REDIRECT
from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2.s_utils import decode_base64_and_inflate
from saml2.server import Server

__author__ = 'rolandh'

def _logout_request(conf_file):
    conf = SPConfig()
    conf.load_file(conf_file)
    sp = Saml2Client(conf)

    soon = time_util.in_a_while(days=1)
    sinfo = {
        "name_id": "foba0001",
        "issuer": "urn:mace:example.com:saml:roland:idp",
        "not_on_or_after" : soon,
        "user": {
            "givenName": "Leo",
            "surName": "Laport",
            }
    }
    sp.users.add_information_about_person(sinfo)

    return sp.create_logout_request(
        subject_id = "foba0001",
        destination = "http://localhost:8088/slo",
        issuer_entity_id = "urn:mace:example.com:saml:roland:idp",
        reason = "I'm tired of this")

server = Server("idp_slo_redirect_conf")
request = _logout_request("sp_slo_redirect_conf")
print request
binding = BINDING_HTTP_REDIRECT
response = server.create_logout_response(request, binding)
item = server.use_http_get(response, response.destination, "/relay_state")
assert isinstance(item, tuple)
assert item[0] == [('Content-type', 'text/html')]
lead = "name=\"SAMLRequest\" value=\""
body = item[1][3]
i = body.find(lead)
i += len(lead) +1
j = i + body[i:].find('"')
info = body[i:j]
xml_str = decode_base64_and_inflate(info)
resp = response_from_string(xml_str)
print resp