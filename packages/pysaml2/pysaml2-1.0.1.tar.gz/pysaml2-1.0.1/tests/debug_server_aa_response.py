from saml2.server import Server

__author__ = 'rolandh'

IDENTITY = {"eduPersonAffiliation": ["staff", "member"],
            "surName": ["Jeter"], "givenName": ["Derek"],
            "mail": ["foo@gmail.com"], "title": "The man"}

server = Server("restrictive_idp_conf")

aa_policy = server.conf.getattr("policy", "idp")
response = server.create_aa_response("aaa", "http://example.com/sp/",
                                     "urn:mace:example.com:sp:1",
                                     IDENTITY.copy())

assert response is not None
