from saml2.ident import IdentDB

__author__ = 'rolandh'

id = IdentDB("foo")
sp_id = "urn:mace:umu.se:sp"
nameid = id.persistent_nameid("abcd0001", sp_id)
remote_id = nameid.text.strip()
print remote_id
local = id.find_local_id(nameid)
assert local == "abcd0001"

# Always get the same
nameid2 = id.persistent_nameid("abcd0001", sp_id)
assert nameid.text.strip() == nameid2.text.strip()
