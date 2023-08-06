from saml2.validate import valid_instance
from saml2 import metadata, md
from saml2.config import SPConfig

import servera_conf

__author__ = 'rolandh'

conf = SPConfig().load(servera_conf.CONFIG, metadata_construction=True)

spsso = metadata.do_spsso_descriptor(conf)

assert isinstance(spsso, md.SPSSODescriptor)

valid_instance(spsso)

print spsso