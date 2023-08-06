from saml2 import BINDING_HTTP_REDIRECT
from saml2.s_utils import UnsupportedBinding
from saml2.server import Server
from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2.time_util import in_a_while

def _logout_request(conf_file):
    conf = SPConfig()
    conf.load_file(conf_file)
    sp = Saml2Client(conf)

    soon = in_a_while(days=1)
    sinfo = {
        "name_id": "foba0001",
        "issuer": "urn:mace:example.com:saml:roland:idp",
        "not_on_or_after" : soon,
        "user": {
            "givenName": "Leo",
            "surName": "Laport",
            }
    }
    sp.users.add_information_about_person(sinfo)

    return sp.create_logout_request(
        subject_id = "foba0001",
        destination = "http://localhost:8088/slo",
        issuer_entity_id = "urn:mace:example.com:saml:roland:idp",
        reason = "I'm tired of this")

server = Server("idp_slo_redirect_conf")
request = _logout_request("sp_slo_redirect_conf")
print request
bindings = [BINDING_HTTP_REDIRECT]
response = server.create_logout_response(request, bindings)
try:
    binding, destination = server.pick_binding("single_logout_service",
                                               bindings, "spsso", request)
except UnsupportedBinding:
    pass
