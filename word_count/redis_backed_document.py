from hashlib import sha256

import faust

from redis import RedisConnection


# noinspection PyAbstractClass
# see https://github.com/robinhood/faust/issues/374
class RedisBackedDocument(faust.Record, serializer='json'):
    """
    Provides an abstraction for documents that will be stored in an external
    Redis database if they exceed the maximum request size for a Kafka message.

    RedisBackedDocuments should be constructed from a string using the static
    builder function from_string(). The content of the document will either be
    stored inside of the record, or in an external Redis database (if the
    representation of the record would exceeds MAX_REQUEST_SIZE bytes).

    The content of the document should be accessed using the get_content()
    method, which returns the content, either from the record itself or from the
    Redis backend.
    """

    _content: str
    is_stored_in_redis: bool = False

    # adopted from faust.types.settings.PRODUCER_MAX_REQUEST_SIZE
    MAX_REQUEST_SIZE = 1_000_000

    @classmethod
    async def from_string(cls, content):
        instance = cls(_content=content)
        if len(instance.dumps()) > cls.MAX_REQUEST_SIZE:
            # The content is stored by its SHA-256 hash, so that multiple
            # instances of the same document share storage in Redis
            key = sha256(content.encode()).hexdigest()
            redis = await RedisConnection.get()
            await redis.set(key=key, value=content)
            instance.is_stored_in_redis = True
            instance._content = key
        return instance

    async def get_content(self):
        if self.is_stored_in_redis:
            redis = await RedisConnection.get()
            return await redis.get(key=self._content)
        return self._content
