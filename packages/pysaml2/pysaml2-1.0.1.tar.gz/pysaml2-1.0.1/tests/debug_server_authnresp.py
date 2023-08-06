import base64
from saml2.saml import NAMEID_FORMAT_PERSISTENT, AUTHN_PASSWORD
from saml2.samlp import NameIDPolicy
from saml2.client import Saml2Client
from saml2 import config, BINDING_HTTP_POST
from saml2.server import Server

__author__ = 'rolandh'

server = Server("idp_conf")

conf = config.SPConfig()
conf.load_file("server_conf")
client = Saml2Client(conf)

IDP = "urn:mace:example.com:saml:roland:idp"
AUTHN = (AUTHN_PASSWORD, "http://www.example.com/login")

ava = { "givenName": ["Derek"], "surName": ["Jeter"],
        "mail": ["derek@nyy.mlb.com"], "title":["The man"]}

nameid_policy=NameIDPolicy(allow_create="false",
                                 format=NAMEID_FORMAT_PERSISTENT)

resp = server.create_authn_response(identity=ava,
                                         in_response_to="id1",
                                         destination="http://lingon.catalogix.se:8087/",
                                         sp_entity_id="urn:mace:example.com:saml:roland:sp",
                                         name_id_policy=nameid_policy,
                                         userid="foba0001@example.com",
                                         authn=AUTHN)

resp_str = "%s" % resp

resp_str = base64.encodestring(resp_str)

authn_response = client.parse_authn_request_response(
    resp_str, BINDING_HTTP_POST,
    {"id1":"http://foo.example.com/service"})
