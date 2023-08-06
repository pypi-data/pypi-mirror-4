import pyDes
import base64


def handle_crypt(key, data, decrypt=True):
    k = pyDes.triple_des(key)
    if decrypt:
        return k.decrypt(data, '*')
    else:
        return k.encrypt(data, '*')


def encrypt_data(key, data):
    new_data = handle_crypt(key, data, decrypt=False)
    return base64.b64encode(new_data)

def decrypt_data(key, data):
    new_data = base64.b64decode(data)
    return handle_crypt(key, new_data)
