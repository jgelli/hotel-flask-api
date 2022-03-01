import hashlib

def password_hash(password, salt):
    """Return the hash of password in hexadecimal"""
    hashed_passwor = hashlib.pbkdf2_hmac(hash_name='sha256',password=password.encode(), iterations=200000, salt=salt.encode())
    return hashed_passwor.hex()

def return_salt(stored_password):
    """Return the stored salt hash"""
    salt = stored_password.split(':')[0]
    return salt

def return_password_hash(stored_password):
    """Return the stored password hash"""
    password = stored_password.split(':')[1]
    return password