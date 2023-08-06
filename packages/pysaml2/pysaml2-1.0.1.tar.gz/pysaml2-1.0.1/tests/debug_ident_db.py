from saml2.assertion import Policy
from saml2.samlp import NameIDPolicy, NameIDMappingRequest, \
    name_id_policy_from_string
from saml2.ident import code, IdentDB
from saml2.ident import decode
from saml2.saml import NameID
from saml2.saml import NAMEID_FORMAT_PERSISTENT
from saml2.saml import NAMEID_FORMAT_TRANSIENT

local_id = "roland"

name_id1 = NameID(format = NAMEID_FORMAT_PERSISTENT, sp_name_qualifier="sp1")

name_id2 = NameID(format = NAMEID_FORMAT_TRANSIENT, name_qualifier="edu")

name_id3 = NameID(format=NAMEID_FORMAT_PERSISTENT, sp_name_qualifier="foobar",
                  name_qualifier="com", sp_provided_id="james")

for item in [name_id1, name_id2, name_id3]:
    s1 = code(item)
    n1 = decode(s1)
    assert s1 == code(n1)

NAME_ID_POLICY_1 = """<?xml version="1.0" encoding="utf-8"?>
<NameIDPolicy xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
  SPNameQualifier="http://vo.example.org/biomed"
/>
"""

NAME_ID_POLICY_2 = """<?xml version="1.0" encoding="utf-8"?>
<NameIDPolicy xmlns="urn:oasis:names:tc:SAML:2.0:protocol"
  SPNameQualifier="http://vo.example.org/design"
/>
"""

id = IdentDB("subject.db", "example.com", "example")

policy = Policy({
    "default": {
        "name_form": "urn:oasis:names:tc:SAML:2.0:attrname-format:uri",
        "nameid_format": NAMEID_FORMAT_PERSISTENT,
        "attribute_restrictions": {
            "surName": [".*berg"],
            }
    }
})

name_id_policy = name_id_policy_from_string(NAME_ID_POLICY_1)
print name_id_policy
nameid = id.construct_nameid("foobar", policy,
                                  'http://vo.example.org/biomed',
                                  name_id_policy)

print nameid
assert nameid.sp_name_qualifier == 'http://vo.example.org/biomed'
assert nameid.format == 'urn:oid:2.16.756.1.2.5.1.1.1-NameID'
assert nameid.text == "foobar"
