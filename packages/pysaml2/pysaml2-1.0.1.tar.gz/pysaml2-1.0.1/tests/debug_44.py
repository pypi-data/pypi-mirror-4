from saml2.saml import AUTHN_PASSWORD
from saml2.config import config_factory
from saml2.response import authn_response
from saml2.server import Server

IDENTITY = {"eduPersonAffiliation": ["staff", "member"],
            "surName": ["Jeter"], "givenName": ["Derek"],
            "mail": ["foo@gmail.com"],
            "title": ["shortstop"]}

server = Server("idp_conf")
name_id = server.ident.transient_nameid(
    "urn:mace:example.com:saml:roland:sp","id12")

_resp_ = server.create_authn_response(
                        IDENTITY,
                        "id12",                       # in_response_to
                        "http://lingon.catalogix.se:8087/",   # consumer_url
                        "urn:mace:example.com:saml:roland:sp", # sp_entity_id
                        name_id = name_id,
                        authn=(AUTHN_PASSWORD, "http://www.example.com/login"))

_sign_resp_ = server.create_authn_response(
                        IDENTITY,
                        "id12",                       # in_response_to
                        "http://lingon.catalogix.se:8087/",   # consumer_url
                        "urn:mace:example.com:saml:roland:sp", # sp_entity_id
                        name_id = name_id, sign_assertion=True,
                        authn=(AUTHN_PASSWORD, "http://www.example.com/login"))

conf = config_factory("sp", "server_conf")
conf.only_use_keys_in_metadata = False
ar = authn_response(conf, "http://lingon.catalogix.se:8087/")

xml_response = "%s" % (_resp_,)
ar.outstanding_queries = {"id12": "http://localhost:8088/sso"}
ar.timeslack = 10000
ar.loads(xml_response, decode=False)
ar.verify()
