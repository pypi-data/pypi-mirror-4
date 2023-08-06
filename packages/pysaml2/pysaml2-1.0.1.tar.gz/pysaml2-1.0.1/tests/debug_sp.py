import base64
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.samlp import NameIDPolicy
from s2repoze.plugins.sp import make_plugin
from saml2.server import Server

__author__ = 'rolandh'

trans_name_policy = NameIDPolicy(format=NAMEID_FORMAT_TRANSIENT,
                                 allow_create="true")

sp = make_plugin("rem", saml_conf="server_conf")
server = Server(config_file="idp_conf")

# Create a SAMLResponse
ava = { "givenName": ["Derek"], "surName": ["Jeter"],
        "mail": ["derek@nyy.mlb.com"], "title":["The man"]}

resp_str = "%s" % server.create_authn_response(ava, "id1",
                                                    "http://lingon.catalogix.se:8087/",
                                                    "urn:mace:example.com:saml:roland:sp",
                                                    trans_name_policy,
                                                    "foba0001@example.com")

resp_str = base64.encodestring(resp_str)
sp.outstanding_queries = {"id1":"http://www.example.com/service"}
session_info = sp._eval_authn_response({},{"SAMLResponse":resp_str})

assert len(session_info) > 1
