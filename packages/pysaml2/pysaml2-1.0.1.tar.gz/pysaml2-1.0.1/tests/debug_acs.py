from saml2 import attribute_converter, saml

from attribute_statement_data import *

acs = attribute_converter.ac_factory("attributemaps")
ats = saml.attribute_statement_from_string(STATEMENT2)
#print ats
ava = None
for ac in acs:
    try:
        ava = ac.fro(ats)
        break
    except attribute_converter.UnknownNameFormat:
        pass
print ava.keys()
#assert _eq(ava.keys(),['uid', 'swissEduPersonUniqueID',
#                       'swissEduPersonHomeOrganizationType',
#                       'eduPersonEntitlement',
#                       'eduPersonAffiliation', 'sn', 'mail',
#                      'swissEduPersonHomeOrganization', 'givenName'])

attr = [saml.Attribute(
    name="urn:mace:dir:attribute-def:eduPersonPrimaryOrgUnitDN")]

lan = [attribute_converter.to_local_name(acs, a) for a in attr]
