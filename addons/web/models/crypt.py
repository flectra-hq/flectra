import Crypto.Random
from Crypto.Cipher import AES
import hashlib

# salt size in bytes
SALT_SIZE = 16

# number of iterations in the key generation
NUMBER_OF_ITERATIONS = 20

# the size multiple required for AES
AES_MULTIPLE = 16


def generate_key(password, salt, iterations):
    assert iterations > 0
    key = str.encode(password) + salt
    for i in range(iterations):
        key = hashlib.sha256(key).digest()
    return key


def pad_text(text, multiple):
    return (text) + (chr((multiple - (len(text) % multiple))) * ((multiple - (len(text) % multiple))))


def unpad_text(padded_text):
    return padded_text.decode('utf-8')[:-ord(padded_text.decode('utf-8')[-1])]


def encrypt(plaintext, contract_id):
    salt = Crypto.Random.get_random_bytes(SALT_SIZE)
    return salt + (AES.new((generate_key(contract_id, salt, NUMBER_OF_ITERATIONS)), AES.MODE_ECB).encrypt(
        (pad_text(plaintext, AES_MULTIPLE))))


def decrypt(ciphertext, contract_id):
    salt = ciphertext[0:SALT_SIZE]
    return unpad_text(
        AES.new((generate_key(contract_id, salt, NUMBER_OF_ITERATIONS)), AES.MODE_ECB).decrypt(ciphertext[SALT_SIZE:]))
