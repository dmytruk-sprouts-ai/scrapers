"""Client-side crypto the Angular app uses to talk to the announcement API.

Everything here was recovered from the site's JS bundle (``egp-agpc01-web``) and confirmed
byte-for-byte against a captured session (see ``outputs/.../har_file.har``):

* ``encrypt_data`` / ``encrypt_key`` reproduce the app's ``CryptoService`` — CryptoJS
  ``AES.encrypt(text, "RDCrypto")`` with the OpenSSL "Salted__" KDF (EVP_BytesToKey, MD5),
  the ciphertext base64'd and then ``encodeURIComponent``'d.
* ``generate_token_key`` builds the body for ``announcement/generateToken``: the project id is
  wrapped by ``encrypt_data`` *twice* (the page re-encrypts the route param it was navigated with).
* ``xsrf_token`` reproduces the ``HiddenInfoService.hideInfo`` interceptor that signs every XHR:
  ``AES.encrypt(f"{xsrf_cookie}:{now_ms}", iv=key="uPfVxw5nykjNf9hF")`` — fixed key *and* IV,
  raw ciphertext base64 (no salt header).

CryptoJS with a *string* passphrase => salted/MD5 KDF; with a 16-byte WordArray key => raw AES.
The two helpers below cover exactly those two shapes.
"""

import base64
import hashlib
import json
import os
import time
import urllib.parse

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

# Passphrase baked into CryptoService (``this.itHarder = "RDCrypto"``).
_RD_PASSPHRASE = b"RDCrypto"
# Fixed key (== IV) baked into HiddenInfoService for the X-Xsrf-Token signature.
_XSRF_KEY = b"uPfVxw5nykjNf9hF"


def _pkcs7_pad(data: bytes) -> bytes:
    pad = 16 - (len(data) % 16)
    return data + bytes([pad]) * pad


def _pkcs7_unpad(data: bytes) -> bytes:
    return data[: -data[-1]]


def _evp_bytes_to_key(passphrase: bytes, salt: bytes, key_len: int = 32, iv_len: int = 16):
    """OpenSSL EVP_BytesToKey (MD5, 1 iteration) — the KDF CryptoJS uses for string passphrases."""
    derived = b""
    block = b""
    while len(derived) < key_len + iv_len:
        block = hashlib.md5(block + passphrase + salt).digest()
        derived += block
    return derived[:key_len], derived[key_len : key_len + iv_len]


def _cryptojs_encrypt(plaintext: str, passphrase: bytes) -> str:
    """CryptoJS ``AES.encrypt(plaintext, passphrase)`` -> "U2FsdGVkX1..." base64 string."""
    salt = os.urandom(8)
    key, iv = _evp_bytes_to_key(passphrase, salt)
    enc = Cipher(algorithms.AES(key), modes.CBC(iv)).encryptor()
    ct = enc.update(_pkcs7_pad(plaintext.encode())) + enc.finalize()
    return base64.b64encode(b"Salted__" + salt + ct).decode()


def _cryptojs_decrypt(b64: str, passphrase: bytes) -> bytes:
    """Inverse of :func:`_cryptojs_encrypt`; kept for verification/debugging."""
    raw = base64.b64decode(b64)
    if raw[:8] != b"Salted__":
        raise ValueError("not a CryptoJS salted payload")
    salt = raw[8:16]
    key, iv = _evp_bytes_to_key(passphrase, salt)
    dec = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    return _pkcs7_unpad(dec.update(raw[16:]) + dec.finalize())


def encrypt_data(value) -> str:
    """``CryptoService.encryptData`` — JSON-encode, AES-encrypt with "RDCrypto", URL-encode."""
    text = json.dumps(value, separators=(",", ":"))
    return urllib.parse.quote(_cryptojs_encrypt(text, _RD_PASSPHRASE), safe="")


def generate_token_key(project_id: str) -> str:
    """Body ``key`` for ``announcement/generateToken``: ``encryptData(encryptData({projectId}))``."""
    return encrypt_data(encrypt_data({"projectId": str(project_id)}))


def route_param(project_id: str) -> str:
    """The ``/announcement/procurement/<param>`` route token the SPA navigates with."""
    return encrypt_data({"projectId": str(project_id)})


def xsrf_token(xsrf_cookie: str) -> str:
    """``HiddenInfoService.hideInfo`` — sign ``"{cookie}:{now_ms}"`` for the X-Xsrf-Token header."""
    plaintext = f"{xsrf_cookie}:{int(time.time() * 1000)}".encode()
    enc = Cipher(algorithms.AES(_XSRF_KEY), modes.CBC(_XSRF_KEY)).encryptor()
    return base64.b64encode(enc.update(_pkcs7_pad(plaintext)) + enc.finalize()).decode()
