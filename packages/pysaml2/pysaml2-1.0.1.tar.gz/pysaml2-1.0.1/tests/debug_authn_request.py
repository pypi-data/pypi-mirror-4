from urlparse import parse_qs
from urlparse import urlparse
from saml2 import BINDING_HTTP_REDIRECT
from saml2 import BINDING_HTTP_POST
from saml2 import BINDING_HTTP_ARTIFACT
from saml2.client import Saml2Client
from saml2.saml import NAMEID_FORMAT_TRANSIENT
from saml2.saml import AUTHN_PASSWORD
from saml2.samlp import NameIDPolicy, STATUS_SUCCESS
from saml2.samlp import AuthnRequest
from saml2.server import Server

__author__ = 'rolandh'

TAG1 = "name=\"SAMLRequest\" value="

def get_msg(hinfo, binding, response=False):
    if binding == BINDING_HTTP_POST:
        _inp = hinfo["data"][3]
        i = _inp.find(TAG1)
        i += len(TAG1) + 1
        j = _inp.find('"', i)
        msg = _inp[i:j]
    elif binding == BINDING_HTTP_ARTIFACT:
        # either by POST or by redirect
        if hinfo["data"]:
            _inp = hinfo["data"][3]
            i = _inp.find(TAG1)
            i += len(TAG1) + 1
            j = _inp.find('"', i)
            msg = _inp[i:j]
        else:
            parts = urlparse(hinfo["headers"][0][1])
            msg = parse_qs(parts.query)["SAMLRequest"][0]
    else: # BINDING_HTTP_REDIRECT
        parts = urlparse(hinfo["headers"][0][1])
        msg = parse_qs(parts.query)["SAMLRequest"][0]

    return msg

# =============================================================================

sp = Saml2Client(config_file="servera_conf")
idp = Server(config_file="idp_all_conf")

relay_state = "FOO"

# ------- @SP ----------


binding, dest = sp.pick_binding("single_sign_on_service",
                                [BINDING_HTTP_REDIRECT], "idp",
                                entity_id=idp.config.entityid)

orig_req = sp.create_authn_request(dest,
                                   binding=binding,
                                   nameid_format=NAMEID_FORMAT_TRANSIENT)

outstanding = {orig_req.id: "/"}
hinfo = sp.apply_binding(BINDING_HTTP_REDIRECT, "%s" % orig_req, dest,
                         relay_state="RS1")

# ------- @IDP ----------

# parse the request
msg = get_msg(hinfo, binding)

req = idp.parse_authn_request(msg, binding)
orig_entity = req.message.issuer.text
assert orig_entity == sp.config.entityid
# Create an AuthnRequest response

name_id = idp.ident.transient_nameid( "id12", sp.config.entityid)

binding, destination = idp.pick_binding("assertion_consumer_service",
                                        entity_id=orig_entity)

assert destination == req.message.assertion_consumer_service_url

resp = idp.create_authn_response({"eduPersonEntitlement": "Short stop",
                                  "surName": "Jeter",
                                  "givenName": "Derek",
                                  "mail": "derek.jeter@nyy.mlb.com",
                                  "title": "The man"},
                                 req.message.id,
                                 destination,
                                 orig_entity,
                                 name_id=name_id,
                                 authn=(AUTHN_PASSWORD,
                                        "http://www.example.com/login"))

hinfo = idp.apply_binding(binding, "%s" % resp, destination, relay_state)

# ------- @SP ----------

msg = get_msg(hinfo, binding)

resp = sp.parse_authn_request_response(msg, binding, outstanding)

response = resp.response

assert response.status.status_code.value == STATUS_SUCCESS
assert response.issuer.text == idp.config.entityid
assert response.assertion[0].subject.name_id.format == NAMEID_FORMAT_TRANSIENT
assert response.assertion[0].subject.name_id.sp_name_qualifier == sp.config.entityid
