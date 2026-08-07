from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

_hasher = PasswordHasher()


def hash_password(plain_password: str) -> str:
    return _hasher.hash(plain_password)


def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        return _hasher.verify(stored_hash, plain_password)
    except VerifyMismatchError:
        return False
