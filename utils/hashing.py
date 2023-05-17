from passlib.context import CryptContext


class Hasher:
    """
    The object of the hash operation.
    """
    __pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

    @classmethod
    def verify_password(cls, plain_password: str, hashed_password: str) -> bool:
        """
        Checks that the password entered matches the hashed password.
        :param plain_password: The password entered.
        :param hashed_password: Password from the base.
        :return: Matches or not.
        """
        return cls.__pwd_context.verify(plain_password, hashed_password)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """
        Hashing the password.
        :param password:
        :return: hashed password.
        """
        return cls.__pwd_context.hash(password)
