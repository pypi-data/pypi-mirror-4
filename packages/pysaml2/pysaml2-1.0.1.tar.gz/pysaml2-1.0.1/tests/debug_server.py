from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2.samlp import STATUS_SUCCESS, NameIDPolicy
from saml2 import config, s_utils
from saml2.server import Server
from saml2.client import Saml2Client

__author__ = 'rolandh'

server = Server("idp_conf")

conf = config.SPConfig()
conf.load_file("sp_1_conf")
client = Saml2Client(conf)

id, authn_request = client.create_authn_request(id = "id1",
                                                destination="http://localhost:8088/sso")

print authn_request
intermed = s_utils.deflate_and_base64_encode("%s" % authn_request)

response = server.parse_authn_request(intermed)

name_id = server.ident.transient_nameid(
    "urn:mace:example.com:saml:roland:sp",
    "id12")

resp = server.create_response(
    "id12",                         # in_response_to
    "http://localhost:8087/",       # consumer_url
    "urn:mace:example.com:saml:roland:sp", # sp_entity_id
    {"eduPersonEntitlement": "Short stop",
     "surName": "Jeter",
     "givenName": "Derek",
     "mail": "derek.jeter@nyy.mlb.com",
     }, # identity
    name_id,
    policy= server.conf.getattr("policy")
)

assert resp.destination == "http://localhost:8087/"
assert resp.in_response_to == "id12"
assert resp.status
assert resp.status.status_code.value == STATUS_SUCCESS
assert resp.assertion
assert resp.assertion
assertion = resp.assertion
print assertion
assert assertion.authn_statement
assert assertion.conditions
assert assertion.attribute_statement
attribute_statement = assertion.attribute_statement
print attribute_statement
assert len(attribute_statement.attribute) == 4

exc = s_utils.MissingValue("eduPersonAffiliation missing")
resp = server.create_error_response("id12", "http://localhost:8087/",exc )

print resp

ava = { "givenName": ["Derek"], "surname": ["Jeter"],
        "mail": ["derek@nyy.mlb.com"]}

nameid_policy=NameIDPolicy(allow_create="false",
                           format=NAMEID_FORMAT_PERSISTENT)

resp = server.create_authn_response(identity=ava, in_response_to="id1",
                                    destination="http://lingon.catalogix.se:8087/",
                                    sp_entity_id="urn:mace:example.com:saml:roland:sp",
                                    name_id_policy=nameid_policy,
                                    userid="foba0001@example.com")

print resp