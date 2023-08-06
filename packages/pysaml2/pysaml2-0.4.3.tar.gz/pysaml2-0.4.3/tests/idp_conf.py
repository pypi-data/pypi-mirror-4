from saml2 import BINDING_SOAP, BINDING_HTTP_REDIRECT, BINDING_HTTP_POST
from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2.saml import NAME_FORMAT_URI

try:
    from xmlsec_location import xmlsec_path
except ImportError:
    xmlsec_path = '/opt/local/bin/xmlsec1'


CONFIG = {
    "entityid" : "urn:mace:example.com:saml:roland:idp",
    "name" : "Rolands IdP",
    "service": {
        "idp": {
            "endpoints" : {
                "single_sign_on_service" : [
                        ("http://localhost:8088/sso", BINDING_HTTP_REDIRECT)],
                "single_logout_service": [
                        ("http://localhost:8088/slo", BINDING_SOAP),
                        ("http://localhost:8088/slop",BINDING_HTTP_POST)]
            },
            "policy": {
                "default": {
                    "lifetime": {"minutes":15},
                    "attribute_restrictions": None, # means all I have
                    "name_form": NAME_FORMAT_URI,
                },
                "urn:mace:example.com:saml:roland:sp": {
                    "lifetime": {"minutes": 5},
                    "nameid_format": NAMEID_FORMAT_PERSISTENT,
                    # "attribute_restrictions":{
                    #     "givenName": None,
                    #     "surName": None,
                    # }
                }
            },
            "subject_data": "subject_data.db",
        },
    },
    "debug" : 1,
    "key_file" : "test.key",
    "cert_file" : "test.pem",
    "xmlsec_binary" : xmlsec_path,
    "metadata": {
        "local": ["metadata.xml", "vo_metadata.xml"],
    },
    "attribute_map_dir" : "attributemaps",
    "organization": {
        "name": "Exempel AB",
        "display_name": [("Exempel AB","se"),("Example Co.","en")],
        "url":"http://www.example.com/roland",
    },
    "contact_person": [{
        "given_name":"John",
        "sur_name": "Smith",
        "email_address": ["john.smith@example.com"],
        "contact_type": "technical",
        },
    ],
}
