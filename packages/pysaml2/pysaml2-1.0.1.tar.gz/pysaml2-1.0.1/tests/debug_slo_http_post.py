import base64
from saml2.server import Server
from saml2.time_util import in_a_while
from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2 import BINDING_HTTP_POST

__author__ = 'rolandh'

server = Server("idp_conf")

conf = SPConfig()
conf.load_file("server_conf")
client = Saml2Client(conf)

soon = in_a_while(days=1)
sinfo = {
    "name_id": "foba0001",
    "issuer": "urn:mace:example.com:saml:roland:idp",
    "not_on_or_after" : soon,
    "user": {
        "givenName": "Leo",
        "surName": "Laport",
        }
}
client.users.add_information_about_person(sinfo)

logout_request = client.create_logout_request(
    destination = "http://localhost:8088/slop",
    subject_id="foba0001",
    issuer_entity_id = "urn:mace:example.com:saml:roland:idp",
    reason = "I'm tired of this")

intermed = base64.b64encode("%s" % logout_request)

#saml_soap = make_soap_enveloped_saml_thingy(logout_request)
request = server.parse_logout_request(intermed, BINDING_HTTP_POST)
assert request
