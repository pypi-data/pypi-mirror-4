from saml2.client import Saml2Client
from saml2.config import SPConfig
from saml2.s_utils import deflate_and_base64_encode
from saml2.s_utils import OtherError
from saml2.s_utils import error_status_factory
from saml2.server import Server

__author__ = 'rolandh'

server = Server("idp_conf")

conf = SPConfig()
conf.load_file("server_conf")
client = Saml2Client(conf)

authn_request = client.create_authn_request(destination="http://www.example.com")

intermed = deflate_and_base64_encode("%s" % authn_request)
try:
    server.parse_authn_request(intermed)
    status = None
except OtherError, oe:
    print oe.args
    status = error_status_factory(oe)
