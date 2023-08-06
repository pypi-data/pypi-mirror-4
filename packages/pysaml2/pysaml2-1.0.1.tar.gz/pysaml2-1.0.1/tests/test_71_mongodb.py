from saml2 import BINDING_HTTP_POST
from saml2.samlp import AuthnRequest, NameIDPolicy
from saml2.saml import NAMEID_FORMAT_TRANSIENT, AUTHN_PASSWORD
from saml2.client import Saml2Client
from saml2.server import Server

__author__ = 'rolandh'


def _eq(l1, l2):
    return set(l1) == set(l2)


def test_flow():
    sp = Saml2Client(config_file="servera_conf")
    idp = Server(config_file="idp_all_conf")

    relay_state = "FOO"
    # -- dummy request ---
    orig_req = sp.create_authn_request(idp.config.entityid)

    # == Create an AuthnRequest response

    rinfo = idp.response_args(orig_req, [BINDING_HTTP_POST])

    binding, destination = idp.pick_binding("assertion_consumer_service",
                                            [BINDING_HTTP_POST],
                                            entity_id=rinfo["sp_entity_id"])

    name_id = idp.ident.transient_nameid("id12", rinfo["sp_entity_id"])
    resp = idp.create_authn_response({"eduPersonEntitlement": "Short stop",
                                      "surName": "Jeter",
                                      "givenName": "Derek",
                                      "mail": "derek.jeter@nyy.mlb.com",
                                      "title": "The man"},
                                     "id-123456789",
                                     destination,
                                     rinfo["sp_entity_id"],
                                     name_id=name_id,
                                     authn=(AUTHN_PASSWORD,
                                            "http://www.example.com/login"))

    hinfo = idp.apply_binding(binding, "%s" % resp, destination, relay_state)

if __name__ == "__main__":
    test_flow()
