import urllib
from saml2.saml import AUTHN_PASSWORD
from saml2 import BINDING_HTTP_POST
from saml2.client import Saml2Client
from fakeIDP import FakeIDP
from fakeIDP import unpack_form
from saml2.config import SPConfig

__author__ = 'rolandh'

server = FakeIDP("idp_all_conf")

conf = SPConfig()
conf.load_file("servera_conf")
client = Saml2Client(conf)

client.send = server.receive

id, http_args = client.prepare_for_authenticate(
                                        "urn:mace:example.com:saml:roland:idp",
                                        relay_state="really",
                                        binding=BINDING_HTTP_POST)

# Normally a response would now be sent back to the users web client

# Here I fake what the client will do
# create the form post

_dic = unpack_form(http_args["data"][3])
http_args["data"] = urllib.urlencode(_dic)
http_args["method"] = "POST"
http_args["dummy"] = _dic["SAMLRequest"]
http_args["headers"] = [('Content-type','application/x-www-form-urlencoded')]

response = client.send(**http_args)

##response = client.do_attribute_query("urn:mace:example.com:saml:roland:idp",
##                                     "_e7b68a04488f715cda642fbdd90099f5",
##                                     attribute={"eduPersonAffiliation":None},
##                                     nameid_format=NAMEID_FORMAT_TRANSIENT)
#
#session_info = {
#    "name_id": "123456",
#    "issuer": "urn:mace:example.com:saml:roland:idp",
#    "not_on_or_after": in_a_while(minutes=15),
#    "ava": {
#        "givenName": "Anders",
#        "surName": "Andersson",
#        "mail": "anders.andersson@example.com"
#    }
#}
#client.users.add_information_about_person(session_info)
#entity_ids = client.users.issuers_of_info("123456")
#assert entity_ids == ["urn:mace:example.com:saml:roland:idp"]

_dic = unpack_form(response["data"][3], "SAMLResponse")
resp = client.parse_authn_request_response(_dic["SAMLResponse"],
                                           BINDING_HTTP_POST,
                                           {id: "/"})
ac = resp.assertion.authn_statement[0].authn_context
assert ac.authenticating_authority[0].text == 'http://www.example.com/login'
assert ac.authn_context_class_ref.text == AUTHN_PASSWORD