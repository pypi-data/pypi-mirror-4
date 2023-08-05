import string
import random
import hashlib

SALT_CHARACTERS = string.letters + string.digits

class InvalidPasswordError(Exception):
    """ Invalid Password was provided to the validate method """

class HashishMixin(object):
    """ HashishMixin adds pasword hashing to an object.

    Example Usage with SqlAlchemy:

        class Account(Base,HashishMixin):
            __PASSWORD_FIELD__ = "password_hash"  # Defaults to "hash"
            __SALT_COUNT__ = 4  # Defaults to 2

            password_hash = Column(String)


        test_account = Account()
        test_account.password = "SuperSecretPasswordYo!"
        test_account.validate("SuperSecretPasswordYo!")  # True if the hashes match using the same salt.

    This updates the password_hash field with a hashed password
    """

    __PASSWORD_FIELD__ = "hash"
    __SALT_COUNT__ = 2

    @property
    def password(self):
        raise AttributeError("Password is not readable")

    @password.setter
    def password(self, value):
        salt = self.salt
        data = "{salt};{value}".format(salt=salt,
                                       value=self._generate_hash(salt, value))
        setattr(self, self.__PASSWORD_FIELD__, data)

    @property
    def salt(self):
        if not hasattr(self, "_salt") or self._salt is None:
            self._salt = self._generate_salt()

        return self._salt

    @salt.setter
    def salt(self, value):
        if value is None:
            self._salt = None
            return

        if len(value) != self.__SALT_COUNT__:
            raise ValueError(
                "Salt must be {0} characters".format(self.__SALT_COUNT__))

        self._salt = str(value)

    def validate(self, value, throw=False):
        hash_value = getattr(self, self.__PASSWORD_FIELD__)
        salt = hash_value[:self.__SALT_COUNT__]
        expected = hash_value[(self.__SALT_COUNT__+1):]

        actual = self._generate_hash(salt, value)

        if throw and actual != expected:
            raise InvalidPasswordError()

        return actual == expected

    def _generate_hash(self, salt, value):
        hash_string = "{salt};{value}".format(salt=salt, value=value)
        return hashlib.sha512(hash_string).hexdigest()

    def _generate_salt(self):
        return "".join((random.choice(SALT_CHARACTERS) for x in range(self.__SALT_COUNT__)))
