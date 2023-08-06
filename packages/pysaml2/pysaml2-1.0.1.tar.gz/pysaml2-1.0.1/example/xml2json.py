__author__ = 'rohe0002'

#[{"entityID":"urn:mace:incommon:osu.edu",
# "IDPSSODescriptor":{"DisplayName":"Ohio State University"},
# "Organization":{"OrganizationName":"The Ohio State University",
# "OrganizationDisplayName":"Ohio State University",
# "OrganizationURL":"http://www.osu.edu/"}}

from saml2.md import EntitiesDescriptor
from saml2 import create_class_from_xml_string

def compress(dct):
    if not isinstance(dct, dict):
        return dct

    for attr, val in dct.items():
        if isinstance(val, basestring):
            pass
        elif isinstance(val, dict):
            dct[attr] = compress(val)
        elif isinstance(val, list):
            val = [compress(v) for v in val]
            if len(val) == 1:
                dct[attr] = val[0]
            else:
                dct[attr] = val

    return dct

def add_val(dct, param, val, add_none=False):
    if not val and not add_none:
        return

    try:
        dct[param].append(val)
    except KeyError:
        dct[param] = [val]

def organization_info(org, lang="en"):
    res = {}
    for attr in ['organization_name', 'organization_display_name',
                 'organization_url']:
        for v in getattr(org, attr):
            if v.lang == lang:
                add_val(res, attr, v.text)

    return res

def do_descriptor(desc):
    res = {}

    if desc.organization:
        add_val(res, "Organization", organization_info(desc.organization))

    return res

def xml2json(inst):
    res = []
    for ed in inst.entity_descriptor:
        ent = {"entityID": ed.entity_id}
        for desc in ["idpsso_descriptor", "spsso_descriptor"]:
            for d in getattr(ed, desc):
                add_val(ent, d.__class__.__name__, do_descriptor(d), True)

        if ed.organization:
            add_val(ent, "Organization", organization_info(ed.organization))

        res.append(ent)
    return res

if __name__ == "__main__":
    import sys
    res = xml2json(create_class_from_xml_string(EntitiesDescriptor,
                                                open(sys.argv[1]).read()))

    res = [compress(r) for r in res]
    for item in res:
        print item
