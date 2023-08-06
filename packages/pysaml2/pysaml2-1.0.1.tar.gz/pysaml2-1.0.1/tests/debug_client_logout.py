from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2.time_util import in_a_while

__author__ = 'rolandh'

conf = SPConfig()
conf.load_file("server_conf")
client = Saml2Client(conf)

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
