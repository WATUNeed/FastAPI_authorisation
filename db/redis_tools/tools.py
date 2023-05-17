import redis

from config import settings


class RedisTools:
    """
    An object to communicate with Redis.
    """
    __redis_connect = redis.Redis(host=settings.redis_host, port=settings.redis_port)

    @classmethod
    def set_key(cls, key: str, value: str, is_expire: bool = True):
        """
        Writes the key-value into the database.
        :param is_expire:
        :param key:
        :param value:
        :return:
        """
        cls.__redis_connect.set(key, value)

        if is_expire:
            cls.__redis_connect.expire(key, settings.access_token_expire_min)

    @classmethod
    def get_value(cls, key: str) -> str:
        """
        :param key:
        :return: Returns the value according to the key.
        """
        return cls.__redis_connect.get(key)

    @classmethod
    def delete_value(cls, key: str):
        """
        Deletes the value and key from the database.
        :param key:
        :return:
        """
        try:
            cls.__redis_connect.delete(key)
            return True
        except redis.DataError:
            return False

    @classmethod
    def get_keys(cls) -> list[str]:
        """
        :return: Outputs all the keys of the database.
        """
        return [value.decode('UTF-8') for value in cls.__redis_connect.keys(pattern='*')]
