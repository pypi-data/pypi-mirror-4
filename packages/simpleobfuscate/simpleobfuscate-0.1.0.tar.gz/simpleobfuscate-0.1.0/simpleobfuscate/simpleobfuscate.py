#encoding=utf-8
"""
Quick-and-dirty obfuscation for strings, designed to
hide URL parameters from the casual experimenter without
adding too much length. A little randomness is baked
in to make it look like the parameters are constantly
changing, even if they're not.

Obviously this is NOT SECURE; don't rely on it for strong secrecy.
A chosen-plaintext attack will recover the key, just like xor.

Only works for ASCII strings.  Not Unicode-safe.
"""
__author__ = "Christian Ternus <ternus@cternus.net>"

from base64 import b64encode, b64decode
from random import randint

def obfuscate(string, key):
    """
    Obfuscates a string, hiding it from the casual eye.

    1. Generates a single random 8-bit value.
    2. XORs the string with the (repeated) key and the random value.
    3. Prepends the random value to the result and b64encodes it.

    Example run:

    >>> print obfuscate('test', 'foo')
    'JjQsOjQ='
    >>> print deobfuscate('JjQsOjQ=', 'foo')
    'test'
    >>> print deobfuscate(obfuscate('foo', 'bar'), 'bar')
    'foo'
    """
    randkey = randint(1,255)
    plaintext = map(ord, string)
    key2 = map(ord, key) * ((len(plaintext) / len(key)) + 1)
    return b64encode(chr(randkey) + "".join([chr(plaintext[x] ^ key2[x] ^ randkey) for x in range(len(plaintext))]))

def deobfuscate(string, key):
    """
    The reverse of the obfuscate() function.

    1. b64decodes the string.
    2. Grabs the random value off the front.
    3. XORs the ciphertext with the random value and the key.
    """
    rawtext = b64decode(string)
    randkey = ord(rawtext[0])
    ciphertext = map(ord, rawtext[1:])
    key2 = map(ord, key) * ((len(ciphertext) / len(key)) + 1)
    return "".join([chr(ciphertext[x] ^ key2[x] ^ randkey) for x in range(len(ciphertext))])

