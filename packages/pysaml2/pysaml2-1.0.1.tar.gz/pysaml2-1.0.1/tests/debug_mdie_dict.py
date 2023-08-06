__author__ = 'rolandh'

from saml2 import saml
from saml2 import samlp
from saml2.client import Saml2Client
from saml2.server import Server
from saml2 import BINDING_HTTP_REDIRECT
from saml2.mdie import to_dict
from saml2.mdie import from_dict

sp = Saml2Client(config_file="servera_conf" )
idp = Server(config_file="idp_all_conf")

srvs = sp.metadata.single_sign_on_service(idp.config.entityid,
                                          BINDING_HTTP_REDIRECT)

destination=srvs[0]["location"]
req = sp.create_authn_request(destination, id = "id1")

onts = {
    saml.NAMESPACE: saml,
    samlp.NAMESPACE: samlp
}

_dict = to_dict(req,onts.values())

req2 = from_dict(_dict, onts)

print req2