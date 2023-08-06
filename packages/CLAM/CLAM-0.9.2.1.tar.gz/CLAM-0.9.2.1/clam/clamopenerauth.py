#Code adapted from  http://stackoverflow.com/a/8232171

import clam.external.rijndael as rijndael
from os import environ
from sys import argv, argc
import base64

KEY_SIZE = 16
BLOCK_SIZE = 32

def encrypt(plaintext):
    key = environ['CLAMOPENER_KEY']
    padded_key = key.ljust(KEY_SIZE, '\0')
    padded_text = plaintext + (BLOCK_SIZE - len(plaintext) % BLOCK_SIZE) * '\0'

    # could also be one of
    #if len(plaintext) % BLOCK_SIZE != 0:
    #    padded_text = plaintext.ljust((len(plaintext) / BLOCK_SIZE) + 1 * BLOCKSIZE), '\0')
    # -OR-
    #padded_text = plaintext.ljust((len(plaintext) + (BLOCK_SIZE - len(plaintext) % BLOCK_SIZE)), '\0')

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    ciphertext = ''
    for start in range(0, len(padded_text), BLOCK_SIZE):
        ciphertext += r.encrypt(padded_text[start:start+BLOCK_SIZE])

    encoded = base64.b64encode(ciphertext)

    return encoded


def decrypt(encoded):
    key = environ['CLAMOPENER_KEY']    
    padded_key = key.ljust(KEY_SIZE, '\0')

    ciphertext = base64.b64decode(encoded)

    r = rijndael.rijndael(padded_key, BLOCK_SIZE)

    padded_text = ''
    for start in range(0, len(ciphertext), BLOCK_SIZE):
        padded_text += r.decrypt(ciphertext[start:start+BLOCK_SIZE])

    plaintext = padded_text.split('\x00', 1)[0]

    return plaintext


if __name__ == "__main__":
    if argc != 2:
        print "Syntax to encrypt a password: clamopenerauth.py private-key plaintext-pw"
    else:    
        environ['CLAMOPENER_KEY'] =  argv[1]
        print encrypt(argv[2])
   
