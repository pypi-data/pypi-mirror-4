__author__ = 'rohe0002'

from saml2.encdec import decrypt_message

enctext = open("signed_id.xml").read()
xmlsec_binary = "/opt/local/bin/xmlsec1"
node_name = "_732eca018e4c1e0e3c9dc7de48c45dcc"

#decrypt_message(enctext, xmlsec_binary, node_name, cert_file=None,
#                cert_type="pem", debug=False, node_id=None,
#                log=None, id_attr="")

decrypt_message(enctext, xmlsec_binary, node_name, cert_file="")
