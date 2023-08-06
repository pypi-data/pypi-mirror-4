from saml2.samlp import STATUS_AUTHN_FAILED
from saml2.config import config_factory
from saml2 import BINDING_HTTP_POST
from saml2.response import authn_response
from saml2.server import Server

__author__ = 'rolandh'

IDENTITY = {"eduPersonAffiliation": ["staff", "member"],
            "surName": ["Jeter"], "givenName": ["Derek"],
            "mail": ["foo@gmail.com"],
            "title": ["shortstop"]}

server = Server("idp_conf")
name_id = server.ident.transient_nameid("urn:mace:example.com:saml:roland:sp",
                                        "id12")

policy = server.config.getattr("policy", "idp")
_resp_ = server.create_error_response(
    "id12",                       # in_response_to
    "http://lingon.catalogix.se:8087/",   # consumer_url
    (STATUS_AUTHN_FAILED, "No user"))

conf = config_factory("sp", "server_conf")
conf.only_use_keys_in_metadata = False
ar = authn_response(conf, "http://lingon.catalogix.se:8087/")
ar.asynchop = False
ar.loads("%s" % _resp_)
ar.verify()