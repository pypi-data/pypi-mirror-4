from saml2 import BINDING_HTTP_POST
from saml2.config import SPConfig, IdPConfig, Config

__author__ = 'rolandh'

cnf = SPConfig()
cnf.load_file("sp_1_conf")
loc = cnf.single_logout_services("urn:mace:example.com:saml:roland:idp",
                                  BINDING_HTTP_POST)
assert loc == ["http://localhost:8088/slo"]

sp2 = {
    "entityid" : "urn:mace:umu.se:saml:roland:sp",
    "name" : "Rolands SP",
    "service": {
        "sp": {
            "endpoints" : {
                "assertion_consumer_service" : ["http://lingon.catalogix.se:8087/"],
                },
            "required_attributes": ["surName", "givenName", "mail"],
            "optional_attributes": ["title"],
            "idp": {
                "" : "https://example.com/saml2/idp/SSOService.php",
                }
        }
    },
    "xmlsec_binary" : "/opt/local/bin/xmlsec1",
}

c = SPConfig().load(sp2)
c.context = "sp"

print c
assert c._sp_endpoints
assert c.getattr("endpoints", "sp")
assert c._sp_idp
assert c._sp_optional_attributes
assert c.getattr("name", "sp")
assert c._sp_required_attributes

IDP1 = {
    "entityid" : "urn:mace:umu.se:saml:roland:idp",
    "name" : "Rolands IdP",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service" : ["http://localhost:8088/"],
                },
            "policy": {
                "default": {
                    "attribute_restrictions": {
                        "givenName": None,
                        "surName": None,
                        "eduPersonAffiliation": ["(member|staff)"],
                        "mail": [".*@example.com"],
                        }
                },
                "urn:mace:umu.se:saml:roland:sp": None
            },
            }
    },
    "xmlsec_binary" : "/opt/local/bin/xmlsec1",
}

ic = IdPConfig().load(IDP1)
ic.context = "idp"

print ic
ep = ic.endpoint("single_sign_on_service")[0]
assert ep == 'http://localhost:8088/'
attribute_restrictions = ic.getattr("idp", "policy").get_attribute_restriction("")

c = SPConfig().load_file("server_conf")
c.context = "sp"

idps = c.idps()

cnf = Config().load_file("idp_sp_conf")
print cnf