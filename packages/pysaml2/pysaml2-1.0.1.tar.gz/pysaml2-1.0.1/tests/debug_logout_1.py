import base64
from saml2.samlp import logout_request_from_string
from saml2.saml import NameID, NAMEID_FORMAT_TRANSIENT
from saml2.time_util import in_a_while
from saml2.client import Saml2Client
from saml2.config import SPConfig
from fakeIDP import FakeIDP
from fakeIDP import unpack_form

__author__ = 'rolandh'

nid = NameID(name_qualifier="foo", format=NAMEID_FORMAT_TRANSIENT,
             text="123456")

server = FakeIDP("idp_all_conf")

conf = SPConfig()
conf.load_file("servera_conf")
client = Saml2Client(conf)

client.send = server.receive

# information about the user from an IdP
session_info = {
    "name_id": nid,
    "issuer": "urn:mace:example.com:saml:roland:idp",
    "not_on_or_after": in_a_while(minutes=15),
    "ava": {
        "givenName": "Anders",
        "surName": "Andersson",
        "mail": "anders.andersson@example.com"
    }
}
client.users.add_information_about_person(session_info)
entity_ids = client.users.issuers_of_info(nid)
assert entity_ids == ["urn:mace:example.com:saml:roland:idp"]
resp = client.global_logout(nid, "Tired", in_a_while(minutes=5))
print resp
assert resp
assert len(resp) == 1
assert resp.keys() == entity_ids
http_args = resp[entity_ids[0]]
assert isinstance(http_args, dict)
assert http_args["headers"] == [('Content-type', 'text/html')]
info = unpack_form(http_args["data"][3])
xml_str = base64.b64decode(info["SAMLRequest"])
req = logout_request_from_string(xml_str)
print req
assert req.reason == "Tired"
