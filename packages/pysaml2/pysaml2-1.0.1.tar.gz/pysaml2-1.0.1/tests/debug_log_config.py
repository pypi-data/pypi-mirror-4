from saml2.client import Saml2Client
from saml2.config import config_factory

__author__ = 'rohe0002'

conf = config_factory("sp", "server_conf")

scl = Saml2Client(config=conf, identity_cache="identity_cache")


