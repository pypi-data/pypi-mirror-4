from saml2 import element_to_extension_element
from saml2.samlp import LogoutRequest
from saml2.saml import Issuer, NameID
from saml2.samlp import artifact_response_from_string
from saml2.samlp import ArtifactResponse
from saml2.samlp import Status
from saml2.samlp import StatusCode
from saml2.samlp import SessionIndex

__author__ = 'rolandh'

#items = [NameID(sp_name_qualifier="sp0", text="foo"),
#         NameID(sp_name_qualifier="sp1", text="bar"),
#         Audience(text="http://example.org")]
#
#ec = ExtensionContainer()
#ec.add_extension_elements(items)

AR = """<samlp:ArtifactResponse
xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
xmlns="urn:oasis:names:tc:SAML:2.0:assertion"
ID="_FQvGknDfws2Z" Version="2.0"
InResponseTo="_6c3a4f8b9c2d"
IssueInstant="2004-01-21T19:00:49Z">
<Issuer>https://IdentityProvider.com/SAML</Issuer>
<samlp:Status>
<samlp:StatusCode
Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
</samlp:Status>
<samlp:LogoutRequest ID="d2b7c388cec36fa7c39c28fd298644a8"
IssueInstant="2004-01-21T19:00:49Z"
Version="2.0">
<Issuer>https://IdentityProvider.com/SAML</Issuer>
<NameID Format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent">005a06e0-ad82-110d-a556-004005b13a2b</NameID>
<samlp:SessionIndex>1</samlp:SessionIndex>
</samlp:LogoutRequest>
</samlp:ArtifactResponse>"""

ar = artifact_response_from_string(AR)
print ar

issuer = Issuer(text="https://IdentityProvider.com/SAML")
status_code = StatusCode(value="urn:oasis:names:tc:SAML:2.0:status:Success")
status = Status(status_code=status_code)
name_id = NameID(format="urn:oasis:names:tc:SAML:2.0:nameid-format:persistent",
                 text="005a06e0-ad82-110d-a556-004005b13a2b")
session_index = SessionIndex(text="1")

logout_request = LogoutRequest(id="d2b7c388cec36fa7c39c28fd298644a8",
                               issuer=issuer,
                               name_id=name_id,
                               session_index=session_index)

ee = element_to_extension_element(logout_request)

ar2 = ArtifactResponse(id="_FQvGknDfws2Z", version="2.0",
                       in_response_to="_6c3a4f8b9c2d",
                       issue_instant="2004-01-21T19:00:49Z",
                       status=status,
                       extension_elements=[ee])

print ar2