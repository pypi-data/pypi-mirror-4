import base64
from saml2.s_utils import decode_base64_and_inflate
from saml2.samlp import logout_response_from_string, STATUS_SUCCESS, \
    response_from_string, logout_request_from_string
from saml2.time_util import in_a_while
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.client import Saml2Client
from fakeIDP import FakeIDP
from saml2.config import SPConfig

__author__ = 'rolandh'

server = FakeIDP("idp_all_conf")

conf = SPConfig()
conf.load_file("servera_conf")
client = Saml2Client(conf)

client.send = server.receive

id, req_args = client.prepare_for_authenticate(
                                    "urn:mace:example.com:saml:roland:idp",
                                    "http://www.example.com/relay_state")

print response

#response = client.do_attribute_query("urn:mace:example.com:saml:roland:idp",
#                                     "_e7b68a04488f715cda642fbdd90099f5",
#                                     attribute={"eduPersonAffiliation":None},
#                                     nameid_format=NAMEID_FORMAT_TRANSIENT)

session_info = {
    "name_id": "123456",
    "issuer": "urn:mace:example.com:saml:roland:idp",
    "not_on_or_after": in_a_while(minutes=15),
    "ava": {
        "givenName": "Anders",
        "surName": "Andersson",
        "mail": "anders.andersson@example.com"
    }
}
client.users.add_information_about_person(session_info)
entity_ids = client.users.issuers_of_info("123456")
assert entity_ids == ["urn:mace:example.com:saml:roland:idp"]
resp = client.global_logout("123456", "Tired", in_a_while(minutes=5))
print resp
assert resp
assert len(resp) == 1
assert resp.keys() == entity_ids
item = resp[entity_ids[0]]
assert isinstance(item, tuple)
assert item[0] == [('Content-type', 'text/html')]
lead = "name=\"SAMLRequest\" value=\""
body = item[1][3]
i = body.find(lead)
i += len(lead)
j = i + body[i:].find('"')
info = body[i:j]
xml_str = base64.b64decode(info)
#xml_str = decode_base64_and_inflate(info)
req = logout_request_from_string(xml_str)
print req
assert req.reason == "Tired"
