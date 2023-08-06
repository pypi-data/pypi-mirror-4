# -*- coding: utf-8 -*-

from saml2.mdstore import MetadataStore
from saml2.mdstore import destinations
from saml2.mdstore import name

from saml2 import BINDING_SOAP
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_ARTIFACT

from saml2 import md
from saml2 import saml
from saml2.attribute_converter import ac_factory, d_to_local_name
from saml2.attribute_converter import to_local_name

from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui
import xmldsig
import xmlenc

try:
    from saml2.sigver import get_xmlsec_binary
    xmlsec_path = get_xmlsec_binary(["/opt/local/bin"])
except ImportError:
    xmlsec_path = '/usr/bin/xmlsec1'


ONTS = {
    saml.NAMESPACE: saml,
    mdui.NAMESPACE: mdui,
    mdattr.NAMESPACE: mdattr,
    dri.NAMESPACE: dri,
    ui.NAMESPACE: ui,
    idpdisc.NAMESPACE: idpdisc,
    md.NAMESPACE: md,
    xmldsig.NAMESPACE: xmldsig,
    xmlenc.NAMESPACE: xmlenc
}

ATTRCONV = ac_factory("attributemaps")

METADATACONF = {
    "1": {
        "local": ["swamid-1.0.xml"]
    },
    "2": {
        "local": ["InCommon-metadata.xml"]
    },
    "3": {
        "local": ["extended.xml"]
    },
    "7": {
        "local": ["metadata_sp_1.xml", "InCommon-metadata.xml"],
        "remote": [{"url": "https://kalmar2.org/simplesaml/module.php/aggregator/?id=kalmarcentral2&set=saml2",
                    "cert": "kalmar2.pem"}]
    },
    "4": {
        "local": ["metadata_example.xml"]
    },
    "5": {
        "local": ["metadata.aaitest.xml"]
    },
    "6": {
        "local": ["metasp.xml"]
    }
}

#UMU_IDP = 'https://idp.umu.se/saml2/idp/metadata.php'
#mds = MetadataStore(ONTS.values(), ATTRCONV, xmlsec_path,
#                    disable_ssl_certificate_validation=True)
#
#mds.imp(METADATACONF["1"])
#assert len(mds) == 1 # One source
#idps = mds.with_descriptor("idpsso")
#assert idps.keys()
#idpsso = mds.single_sign_on_service(UMU_IDP)
#assert len(idpsso) == 1
#assert destinations(idpsso) == ['https://idp.umu.se/saml2/idp/SSOService.php']
#
#_name = name(mds[UMU_IDP])
#assert _name == u'Umeå University (SAML2)'
#certs =  mds.certs(UMU_IDP, "idpsso", "signing")
#assert len(certs) == 1
#
#sps = mds.with_descriptor("spsso")
#
#wants = mds.attribute_requirement('https://connect8.sunet.se/shibboleth')
#lnamn = [d_to_local_name(mds.attrc, attr) for attr in wants["optional"]]
##assert _eq(lnamn,
##           ['mail', 'givenName', 'eduPersonPrincipalName', 'sn',
##            'eduPersonScopedAffiliation'])
#
#wants = mds.attribute_requirement('https://beta.lobber.se/shibboleth')
#assert wants["required"] == []
#lnamn = [d_to_local_name(mds.attrc, attr) for attr in wants["optional"]]
#assert _eq(lnamn,
#           ['eduPersonScopedAffiliation', 'eduPersonEntitlement',
#            'eduPersonPrincipalName', 'sn', 'mail', 'givenName'])


#mds = MetadataStore(ONTS.values(), ATTRCONV, xmlsec_path,
#                    disable_ssl_certificate_validation=True)
#
#mds.imp(METADATACONF["2"])
#
#print mds.entities()
#assert mds.entities() == 169
#idps = mds.with_descriptor("idpsso")
#print idps.keys()
#assert len(idps) == 53 # !!!!???? < 10%
#assert mds.single_sign_on_service('urn:mace:incommon:uiuc.edu') == []
#idpsso = mds.single_sign_on_service('urn:mace:incommon:alaska.edu')
#assert len(idpsso) == 1
#print idpsso
#assert destinations(idpsso) == ['https://idp.alaska.edu/idp/profile/SAML2/Redirect/SSO']
#
#sps = mds.with_descriptor("spsso")
#
#acs_sp = []
#for nam, desc in sps.items():
#    if "attribute_consuming_service" in desc:
#        acs_sp.append(nam)
#
#assert len(acs_sp) == 0
#
## Look for attribute authorities
#aas = mds.with_descriptor("attribute_authority")
#
#print aas.keys()
#assert len(aas) == 53

#mds = MetadataStore(ONTS.values(), ATTRCONV, xmlsec_path,
#                    disable_ssl_certificate_validation=True)
#
#mds.imp(METADATACONF["3"])
## No specific binding defined
#
#ents = mds.with_descriptor("spsso")
#print len(ents)
#for binding in [BINDING_SOAP, BINDING_HTTP_POST, BINDING_HTTP_ARTIFACT,
#                BINDING_HTTP_REDIRECT]:
#    endps = mds.single_logout_service(ents.keys()[0], "spsso", binding=binding)
#    assert endps

mds = MetadataStore(ONTS.values(), ATTRCONV, xmlsec_path,
                    disable_ssl_certificate_validation=True)

mds.imp(METADATACONF["6"])

assert len(mds.keys()) == 1
assert mds.keys() == ['urn:mace:umu.se:saml:roland:sp']
#assert _eq(mds['urn:mace:umu.se:saml:roland:sp'].keys(), [
#    'valid_until',"organization","spsso",
#    'contact_person'])
print mds['urn:mace:umu.se:saml:roland:sp']["spsso"][0].keyswv()
(req,opt) = mds.attribute_requirement('urn:mace:umu.se:saml:roland:sp')
print req
assert len(req) == 3
assert len(opt) == 1
assert opt[0].name == 'urn:oid:2.5.4.12'
assert opt[0].friendly_name == 'title'
assert _eq([n.name for n in req],['urn:oid:2.5.4.4', 'urn:oid:2.5.4.42',
                                  'urn:oid:0.9.2342.19200300.100.1.3'])
assert _eq([n.friendly_name for n in req],['surName', 'givenName', 'mail'])
