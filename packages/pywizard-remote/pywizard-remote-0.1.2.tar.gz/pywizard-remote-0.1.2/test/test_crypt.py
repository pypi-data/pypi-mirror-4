from Crypto import Random
from Crypto.PublicKey import RSA
from pywizard.remote.crypt import encrypt, decrypt, sign, verify, key_checksum, cipher_encrypt, cipher_decrypt


rng = Random.new().read
rsa_key = RSA.generate(1024, rng)


def test_cipher():
    key = rng(32)

    data = cipher_encrypt(key, "a")
    data = cipher_decrypt(key, data)
    assert "a" == data
    assert "b" == cipher_decrypt(key, cipher_encrypt(key, "b"))
    assert "c" == cipher_decrypt(key, cipher_encrypt(key, "c"))


def test_encrypt_decrypt():
    enc = encrypt(rsa_key, 'foo')

    assert enc != 'foo'

    assert decrypt(rsa_key, enc) == 'foo'


def test_sign_verify():
    signature = sign(rsa_key, 'foo')

    assert verify(rsa_key, 'foo', signature)
    assert not verify(rsa_key, 'foo1', signature)


def test_key_checksum():
    assert 0 <= key_checksum(rsa_key) <= 10000
