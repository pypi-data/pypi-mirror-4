from saml2.client import Saml2Client
from saml2 import config, ecp

__author__ = 'rohe0002'

conf = config.SPConfig()
conf.load_file("server_conf")
client = Saml2Client(conf)

ssid, soap_req = ecp.ecp_auth_request(client,
                                      "urn:mace:example.com:saml:roland:idp",
                                      "id1")