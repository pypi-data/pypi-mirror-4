#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging

from saml2 import BINDING_HTTP_REDIRECT, BINDING_SOAP, BINDING_HTTP_POST
from saml2.config import SPConfig, IdPConfig, Config
from saml2.metadata import MetaData
from py.test import raises

from saml2 import root_logger

sp1 = {
    "entityid" : "urn:mace:umu.se:saml:roland:sp",
    "service": {
        "sp": {
            "endpoints" : {
                "assertion_consumer_service" : ["http://lingon.catalogix.se:8087/"],
            },
            "name": "test",
            "idp" : {
                "urn:mace:example.com:saml:roland:idp": {'single_sign_on_service':
                {'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect':
                 'http://localhost:8088/sso/'}},
            }
        }
    },
    "key_file" : "mykey.pem",
    "cert_file" : "mycert.pem",
    #"xmlsec_binary" : "/opt/local/bin/xmlsec1",
    "metadata": { 
        "local": ["metadata.xml", 
                    "urn-mace-swami.se-swamid-test-1.0-metadata.xml"],
    },
    "virtual_organization" : {
        "coip":{
            "nameid_format" : "urn:oasis:names:tc:SAML:2.0:nameid-format:transient",
            "common_identifier": "eduPersonPrincipalName",
            "attribute_auth": [
                "https://coip-test.sunet.se/idp/shibboleth",
            ]
        }
    },
    "attribute_map_dir": "attributemaps",
    "only_use_keys_in_metadata": True,
}

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
    #"xmlsec_binary" : "/opt/local/bin/xmlsec1",
}

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
    #"xmlsec_binary" : "/usr/local/bin/xmlsec1",
}

IDP2 = {
    "entityid" : "urn:mace:umu.se:saml:roland:idp",
    "name" : "Rolands IdP",
    "service": {
        "idp": {
            "endpoints": {
                "single_sign_on_service" : ["http://localhost:8088/"],
                "single_logout_service" : [("http://localhost:8088/", BINDING_HTTP_REDIRECT)],
            },
            "policy":{
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
    #"xmlsec_binary" : "/usr/local/bin/xmlsec1",
}

PDP = {
    "entityid" : "http://example.org/pysaml2/pdp",
    "name" : "Rolands PdP",
    "service": {
        "pdp": {
            "endpoints": {
                "authz_service" : [("http://example.org/pysaml2/pdp/authz",
                                   BINDING_SOAP)],
            },
        }
    },
    "key_file" : "test.key",
    "cert_file" : "test.pem",
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

ECP_SP = {
    "entityid" : "urn:mace:umu.se:saml:roland:ecpsp",
    "name" : "Rolands ECP_SP",
    "service": {
        "sp": {
            "endpoints" : {
                "assertion_consumer_service" : ["http://lingon.catalogix.se:8087/"],
            },
            "ecp" : {
                "130.239.": "http://example.com/idp",
            }
        }
    },
    #"xmlsec_binary" : "/opt/local/bin/xmlsec1",
}

def _eq(l1,l2):
    return set(l1) == set(l2)

def test_1():
    c = SPConfig().load(sp1)
    c.context = "sp"
    print c
    assert c.endpoints
    assert c.name
    assert c.idp
    md = c.metadata
    assert isinstance(md, MetaData)

    assert len(c.idp) == 1
    assert c.idp.keys() == ["urn:mace:example.com:saml:roland:idp"]
    assert c.idp.values() == [{'single_sign_on_service':
        {'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect':
         'http://localhost:8088/sso/'}}]

    assert c.only_use_keys_in_metadata

def test_2():
    c = SPConfig().load(sp2)
    c.context = "sp"

    print c
    assert c.endpoints
    assert c.idp
    assert c.optional_attributes
    assert c.name
    assert c.required_attributes

    assert len(c.idp) == 1
    assert c.idp.keys() == [""]
    assert c.idp.values() == ["https://example.com/saml2/idp/SSOService.php"]
    assert c.only_use_keys_in_metadata is None
    
def test_minimum():
    minimum = {
        "entityid" : "urn:mace:example.com:saml:roland:sp",
        "service": {
            "sp": {
                "endpoints" : {
                    "assertion_consumer_service" : ["http://sp.example.org/"],
                },
                "name" : "test",
                "idp": {
                    "" : "https://example.com/idp/SSOService.php",
                },
            }
        },
        #"xmlsec_binary" : "/usr/local/bin/xmlsec1",
    }

    c = SPConfig().load(minimum)
    c.context = "sp"

    assert c is not None
    
def test_idp_1():
    c = IdPConfig().load(IDP1)
    c.context = "idp"

    print c
    assert c.endpoint("single_sign_on_service")[0] == 'http://localhost:8088/'

    attribute_restrictions = c.policy.get_attribute_restriction("")
    assert attribute_restrictions["eduPersonAffiliation"][0].match("staff")

def test_idp_2():
    c = IdPConfig().load(IDP2)
    c.context = "idp"

    print c
    assert c.endpoint("single_logout_service",
                      BINDING_SOAP) == []
    assert c.endpoint("single_logout_service",
                        BINDING_HTTP_REDIRECT) == ["http://localhost:8088/"]

    attribute_restrictions = c.policy.get_attribute_restriction("")
    assert attribute_restrictions["eduPersonAffiliation"][0].match("staff")
    
def test_wayf():
    c = SPConfig().load_file("server_conf")
    c.context = "sp"

    idps = c.idps()
    assert idps == {'urn:mace:example.com:saml:roland:idp': 'Example Co.'}
    idps = c.idps(["se","en"])
    assert idps == {'urn:mace:example.com:saml:roland:idp': 'Exempel AB'}

    c.setup_logger()

    assert root_logger.level != logging.NOTSET
    assert root_logger.level == logging.WARNING
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0],
                        logging.handlers.RotatingFileHandler)
    handler = root_logger.handlers[0]
    assert handler.backupCount == 5
    assert handler.maxBytes == 100000
    assert handler.mode == "a"
    assert root_logger.name == "pySAML2"
    assert root_logger.level == 30

def test_conf_syslog():
    c = SPConfig().load_file("server_conf_syslog")
    c.context = "sp"

    # otherwise the logger setting is not changed
    root_logger.level = logging.NOTSET
    root_logger.handlers = []
    
    print c.logger
    c.setup_logger()

    assert root_logger.level != logging.NOTSET
    assert root_logger.level == logging.INFO
    assert len(root_logger.handlers) == 1
    assert isinstance(root_logger.handlers[0],
                        logging.handlers.SysLogHandler)
    handler = root_logger.handlers[0]
    print handler.__dict__
    assert handler.facility == "local3"
    assert handler.address == ('localhost', 514)
    if sys.version >= (2, 7):
        assert handler.socktype == 2
    else:
        pass
    assert root_logger.name == "pySAML2"
    assert root_logger.level == 20

#noinspection PyUnresolvedReferences
def test_3():
    cnf = Config()
    cnf.load_file("sp_1_conf")
    assert cnf.entityid == "urn:mace:example.com:saml:roland:sp"
    assert cnf.debug == 1
    assert cnf.key_file == "test.key"
    assert cnf.cert_file == "test.pem"
    #assert cnf.xmlsec_binary ==  "/usr/local/bin/xmlsec1"
    assert cnf.accepted_time_diff == 60
    assert cnf.secret == "0123456789"
    assert cnf.metadata is not None
    assert cnf.attribute_converters is not None

def test_sp():
    cnf = SPConfig()
    cnf.load_file("sp_1_conf")
    assert cnf.single_logout_services("urn:mace:example.com:saml:roland:idp",
                            BINDING_HTTP_POST) == ["http://localhost:8088/slo"]
    assert cnf.endpoint("assertion_consumer_service") == \
                                            ["http://lingon.catalogix.se:8087/"]
    assert len(cnf.idps()) == 1

def test_dual():
    cnf = Config().load_file("idp_sp_conf")
    assert cnf.serves() == ["sp", "idp"]

    spcnf = cnf.copy_into("sp")
    assert isinstance(spcnf, SPConfig)
    assert spcnf.context == "sp"

    idpcnf = cnf.copy_into("idp")
    assert isinstance(idpcnf, IdPConfig)
    assert idpcnf.context == "idp"

def test_ecp():
    cnf = SPConfig()
    cnf.load(ECP_SP)
    assert cnf.endpoint("assertion_consumer_service") == \
                                            ["http://lingon.catalogix.se:8087/"]
    eid = cnf.ecp_endpoint("130.239.16.3")
    assert eid == "http://example.com/idp"
    eid = cnf.ecp_endpoint("130.238.20.20")
    assert eid is None