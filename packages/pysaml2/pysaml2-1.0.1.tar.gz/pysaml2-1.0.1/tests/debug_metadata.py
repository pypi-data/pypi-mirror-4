from saml2 import mdstore
from saml2.attribute_converter import ac_factory
from saml2 import saml
from saml2 import md

__author__ = 'rolandh'

ATTRCONV = ac_factory("attributemaps")
SWAMI_METADATA = "swamid-1.0.xml"
INCOMMON_METADATA = "InCommon-metadata.xml"

def _read_file(name):
    try:
        return open(name).read()
    except IOError:
        name = "tests/"+name
        return open(name).read()

ms = mdstore.MetadataStore([md,saml], attrc=ATTRCONV)
ms.imp({"local":["idp_conf_utf8.xml"]})

print ms