from Crypto.Cipher import DES3
from Crypto.Cipher import RSA
from Crypto.Cipher.DES3 import MODE_CBC

__author__ = 'rohe0002'

def empty_callback():
    return

txt = "identifier"

# Make a triple-des key
des3 = DES3.new(mode=MODE_CBC)

# encrypt the message
ctext = des3.encrypt(txt)

# encrypt the 3des key with a RSA key
rsa =
ckey =

# construct the XML
