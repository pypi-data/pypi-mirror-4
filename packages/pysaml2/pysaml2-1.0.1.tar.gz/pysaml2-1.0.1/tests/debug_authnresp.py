from saml2.response import authn_response
from saml2.config import config_factory

__author__ = 'rolandh'

XML_RESPONSE_FILE = "saml_signed.xml"

conf = config_factory("sp", "server_conf")
ar = authn_response(conf, "http://lingon.catalogix.se:8087/")

xml_response = open(XML_RESPONSE_FILE).read()
ID = "bahigehogffohiphlfmplepdpcohkhhmheppcdie"
ar.outstanding_queries = {ID: "http://localhost:8088/foo"}
ar.return_addr = "http://xenosmilus.umdc.umu.se:8087/login"
ar.entity_id = "xenosmilus.umdc.umu.se"
# roughly a year, should create the response on the fly
ar.timeslack = 315360000 # indecent long time
ar.loads(xml_response, decode=False)
ar.verify()
