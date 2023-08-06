from saml2 import md
from saml2.config import Config
from saml2.metadata import entity_descriptor

fil = "idp_all_conf"
cnf = Config().load_file(fil, metadata_construction=True)
ed = entity_descriptor(cnf)

assert isinstance(ed, md.EntityDescriptor)
