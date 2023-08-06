from saml2 import BINDING_SOAP
from saml2.samlp import NewID
from saml2.saml import NameID, NAMEID_FORMAT_TRANSIENT
from saml2.client import Saml2Client
from saml2.server import Server

# In the scenario supported by the Name Identifier Management profile, an
# identity provider has exchanged some form of persistent identifier for a
# principal with a service provider, allowing them to share a common
# identifier for some length of time. Subsequently, the identity provider may
# wish to notify the service provider of a change in the format and/or value
# that it will use to identify the same principal in the future.
# Alternatively the service provider may wish to attach its own "alias" for
# the principal in order to ensure that the identity provider will include it
# when communicating with it in the future about the principal. Finally, one
# of the providers may wish to inform the other that it will no longer issue
# or accept messages using a particular identifier. To implement these
# scenarios, a profile of the SAML Name Identifier Management protocol is used.

__author__ = 'rolandh'

sp = Saml2Client(config_file="servera_conf")
idp = Server(config_file="idp_all_conf")

binding, destination = sp.pick_binding("manage_name_id_service",
                                       entity_id=idp.config.entityid)

nameid = NameID(format=NAMEID_FORMAT_TRANSIENT, text="foobar")
newid = NewID(text="Barfoo")

mid = sp.create_manage_name_id_request(destination, name_id=nameid,
                                       new_id=newid)

print mid
rargs = sp.apply_binding(binding, "%s" % mid, destination, "")

# --------- @IDP --------------

_req = idp.parse_manage_name_id_request(rargs["data"], binding)

print _req.message

mnir = idp.create_manage_name_id_response(_req.message, None)

if binding != BINDING_SOAP:
    binding, destination = idp.pick_binding("manage_name_id_service",
                                            entity_id=sp.config.entityid)
else:
    destination = ""

respargs = idp.apply_binding(binding, "%s" % mnir, destination, "")

print respargs

# ---------- @SP ---------------

_response = sp.parse_manage_name_id_response(respargs["data"], binding)

print _response.response