from saml2.server import Server
from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2.saml import NAMEID_FORMAT_TRANSIENT

__author__ = 'rolandh'

server = Server("idp_conf")

conf = SPConfig()
conf.load_file("server_conf")
client = Saml2Client(conf)

#resp = client.do_attribute_query("urn:mace:example.com:saml:roland:idp",
#                                 "_e7b68a04488f715cda642fbdd90099f5",
#                                 nameid_format=NAMEID_FORMAT_TRANSIENT)

# since no one is answering on the other end
#assert resp is None

response = client.do_authenticate("urn:mace:example.com:saml:roland:idp",
                                  "http://www.example.com/relay_state")
assert response[0] == "Location"

