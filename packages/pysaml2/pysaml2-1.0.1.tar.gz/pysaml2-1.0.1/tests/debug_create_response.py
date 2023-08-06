from saml2.server import Server

__author__ = 'rolandh'

IDENTITY = {"eduPersonAffiliation": ["staff", "member"],
            "surName": ["Jeter"], "givenName": ["Derek"],
            "mail": ["foo@gmail.com"]}

server = Server("idp_conf")
name_id = server.ident.transient_nameid(
    "urn:mace:example.com:saml:roland:sp",
    "id12")

resp_ = server.create_response("id12", "http://lingon.catalogix.se:8087/",
                                "urn:mace:example.com:saml:roland:sp",
                                IDENTITY, name_id = name_id)
