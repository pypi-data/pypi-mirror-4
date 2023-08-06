from saml2.mdie import to_dict
from saml2.saml import NAME_FORMAT_URI, Attribute
from saml2.assertion import Policy

__author__ = 'rolandh'

from saml2.extension import mdui
from saml2.extension import idpdisc
from saml2.extension import dri
from saml2.extension import mdattr
from saml2.extension import ui
from saml2 import saml, attribute_converter, assertion
from saml2 import md
import xmldsig
import xmlenc

ONTS = [saml, mdui, mdattr, dri, ui, idpdisc, md, xmldsig, xmlenc]

#gn = to_dict(md.RequestedAttribute(name="urn:oid:2.5.4.42",
#                                   friendly_name="givenName",
#                                   name_format=NAME_FORMAT_URI),ONTS)
#
#sn = to_dict(md.RequestedAttribute(name="urn:oid:2.5.4.4",
#                                   friendly_name="surName",
#                                   name_format=NAME_FORMAT_URI), ONTS)
#
#mail = to_dict(md.RequestedAttribute(name="urn:oid:0.9.2342.19200300.100.1.3",
#                                     friendly_name="mail",
#                                     name_format=NAME_FORMAT_URI), ONTS)
#
#conf = {
#    "default": {
#        "lifetime": {"minutes":15},
#        "attribute_restrictions": None # means all I have
#    },
#    "urn:mace:umu.se:saml:roland:sp": {
#        "lifetime": {"minutes": 5},
#        "attribute_restrictions":{
#            "givenName": None,
#            "surName": None,
#            "mail": [".*@.*\.umu\.se"],
#            }
#    }}
#
#policy = Policy(conf)
#
#ava = {"givenName":"Derek",
#       "surName": "Jeter",
#       "mail":"derek@example.com"}
#
#pava = policy.filter(ava, 'urn:mace:umu.se:saml:roland:sp', [mail], [gn, sn])
#
#ava = {"givenName":"Derek",
#       "surName": "Jeter"}
#
#assert ava == pava
#
## it wasn't there to begin with
#pava = policy.filter(ava, 'urn:mace:umu.se:saml:roland:sp', [gn, sn, mail])

r = [Attribute(friendly_name="surName",
                       name="urn:oid:2.5.4.4",
                       name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri"),
     Attribute(friendly_name="givenName",
                       name="urn:oid:2.5.4.42",
                       name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")]
o = [Attribute(friendly_name="title",
                       name="urn:oid:2.5.4.12",
                       name_format="urn:oasis:names:tc:SAML:2.0:attrname-format:uri")]

acs = attribute_converter.ac_factory("attributemaps")

rava = attribute_converter.ava_fro(acs, r)
oava = attribute_converter.ava_fro(acs, o)

ava = { "sn":["Hedberg"], "givenName":["Roland"],
        "eduPersonAffiliation":["staff"],"uid":["rohe0002"]}

ava = assertion.filter_on_demands(ava, rava, oava)
print ava
assert ava == {'givenName': ['Roland'], 'sn': ['Hedberg']}