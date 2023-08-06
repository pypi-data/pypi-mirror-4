import base64
import hashlib
import os
import binascii

import struct
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Hash import MD5
from Crypto.PublicKey import RSA, DSA
from Crypto.Cipher import DES

from paramiko import RSAKey, DSSKey, SSHException


def key_checksum(key):
    st = key.publickey().exportKey('DER')
    return reduce(lambda x, y: x + y, map(ord, st)) % 10000


def cipher_decrypt(key, data):
    data = AES.new(key, AES.MODE_ECB).decrypt(data)
    block_size_diff = struct.unpack('>B', data[0])[0]
    return data[block_size_diff + 1:]


def cipher_encrypt(key, data):
    aes_block_size = AES.block_size
    data_len_with_padding_cnt = len(data) + 1
    block_size_diff = aes_block_size - data_len_with_padding_cnt % aes_block_size
    # add padding
    packed_len = struct.pack('>B', block_size_diff)

    data = packed_len + Random.new().read(block_size_diff) + data
    return AES.new(key, AES.MODE_ECB).encrypt(data)


def sign(key, data):
    rng = Random.new().read
    data_hash = MD5.new(data).digest()
    return base64.b64encode(str(key.sign(data_hash, rng)[0]))


def verify(key, data, signature):
    signature = (long(base64.b64decode(signature)), )
    data_hash = MD5.new(data).digest()
    return key.verify(data_hash, signature)


def encrypt(key, data):
    cipher_key = Random.new().read(AES.block_size * 2)
    enc = cipher_encrypt(cipher_key, data)
    cipher_key_enc = key.encrypt(cipher_key, None)[0]

    return struct.pack('>II', len(cipher_key_enc), len(enc)) + cipher_key_enc + enc


def decrypt(key, data):
    (cipher_key_len, enc_len) = struct.unpack('>II', data[0:8])
    data = data[8:]

    (cipher_key_enc, data) = (data[0:cipher_key_len], data[cipher_key_len:cipher_key_len + enc_len])
    cipher_key = key.decrypt(cipher_key_enc)

    return cipher_decrypt(cipher_key, data)


def load_auth_key(key_filenames=None, password=None):
    """

    :param key_filenames:
    :param password:
    :return: RSAKey
    """
    key = None

    if key_filenames:
        for key_filename in key_filenames:
            for pkey_class in (RSAKey, DSSKey):
                try:
                    key = pkey_class.from_private_key_file(key_filename, password)
                except SSHException, e:
                    pass

    else:
        keyfiles = []
        rsa_key = os.path.expanduser('~/.ssh/id_rsa')
        dsa_key = os.path.expanduser('~/.ssh/id_dsa')
        if os.path.isfile(rsa_key):
            keyfiles.append((RSA, rsa_key))
        if os.path.isfile(dsa_key):
            keyfiles.append((DSA, dsa_key))
            # look in ~/ssh/ for windows users:
        rsa_key = os.path.expanduser('~/ssh/id_rsa')
        dsa_key = os.path.expanduser('~/ssh/id_dsa')
        if os.path.isfile(rsa_key):
            keyfiles.append((RSAKey, rsa_key))
        if os.path.isfile(dsa_key):
            keyfiles.append((DSSKey, dsa_key))

        for pkey_class, filename in keyfiles:
            try:
                key = pkey_class.importKey(filename, password)
            except IOError, e:
                pass

    return key


def load_acceptable_keys():
    keys = []
    auth_keys_file = os.path.expanduser('~/.ssh/authorized_keys')
    if os.path.isfile(auth_keys_file):

        with open(auth_keys_file) as f:
            for line in f:
                fields = line.split(' ')

                if len(fields) < 3:
                    # Bad number of fields
                    continue

                fields = fields[:3]
                keytype, key, name = fields

                # Decide what kind of key we're looking at and create an object
                # to hold it accordingly.
                try:
                    if keytype == 'ssh-rsa':
                        keys.append(RSA.importKey(line))
                    elif keytype == 'ssh-dss':
                        keys.append(DSA.importKey(line))
                except binascii.Error, e:
                    pass

    return keys


def gen_key_index(keys_to_index):
    keys = {}

    for key in keys_to_index:
        chk = key_checksum(key)
        if not chk in keys:
            keys[chk] = []
        keys[chk].append(key)
    return keys