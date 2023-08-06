from saml2.client import Saml2Client
from saml2.discovery import DiscoveryServer


sp = Saml2Client(config_file="servera_conf")
url = sp.create_discovery_service_request("http://example.com/saml/disco",
                                          "https://example.com/saml/sp.xml",
                                          is_passive=True,
                                          returnIDParam="foo",
                                          return_url="https://example.com/saml/sp/disc")
ds = DiscoveryServer(config_file="disco_conf")
dsr = ds.parse_discovery_service_request(url)
args = dict([(key, dsr[key]) for key in ["returnIDParam", "return_url"]])
url = ds.create_discovery_service_response(
                                entity_id="https://example.com/saml/idp.xml",
                                **args)

idp_id = sp.parse_discovery_service_response(url, returnIDParam="foo")
assert idp_id == "https://example.com/saml/idp.xml"