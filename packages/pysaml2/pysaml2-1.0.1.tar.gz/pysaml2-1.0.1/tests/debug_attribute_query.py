from saml2.server import Server
from saml2.saml import NAMEID_FORMAT_TRANSIENT, NAMEID_FORMAT_PERSISTENT
from saml2.client import Saml2Client
from saml2.config import SPConfig
from fakeIDP import FakeIDP

__author__ = 'rolandh'

#IDP = "urn:mace:example.com:saml:roland:idp"
#server = FakeIDP("idp_all_conf")
#
#conf = SPConfig()
#conf.load_file("servera_conf")
#client = Saml2Client(conf)
#client.send = server.receive
#
#response = client.do_attribute_query(IDP, "_e7b68a04488f715cda642fbdd90099f5",
#                                     attribute={"eduPersonAffiliation":None},
#                                     nameid_format=NAMEID_FORMAT_TRANSIENT)
#
#print response

server = Server("idp_conf")

conf = SPConfig()
conf.load_file("server_conf")
client = Saml2Client(conf)

req = client.create_attribute_query("https://idp.example.com/idp/",
                                    "E8042FB4-4D5B-48C3-8E14-8EDD852790DD",
                                    nameid_format=NAMEID_FORMAT_PERSISTENT,
                                    id="id1")
reqstr = "%s" % req.to_string()
