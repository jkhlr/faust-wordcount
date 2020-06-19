from unittest.mock import patch, PropertyMock

import aioredis
import mockaioredis
import pytest

from redis_backed_document import RedisBackedDocument


@pytest.fixture
def redis(mocker):
    """ Patches aioredis with a mock interface during tests """
    mocker.patch.object(
        aioredis,
        'create_redis_pool',
        new=mockaioredis.create_redis_pool
    )


@pytest.mark.asyncio()
async def test_redis_backed_document_small_content():
    """
    Tests RedisBackedDocument's handling of small documents.

    Small documents should not be stored in redis, so redis does not need to be
    mocked for this test case
    """
    test_content = 'testWord1 testWord2'

    document = await RedisBackedDocument.from_string(test_content)
    stored_content = await document.get_content()

    assert stored_content == test_content
    assert not document.is_stored_in_redis


@pytest.mark.asyncio()
@patch(
    'redis_backed_document.RedisBackedDocument.MAX_REQUEST_SIZE',
    new_callable=PropertyMock,
    return_value=100
)
async def test_redis_backed_document_large_content(mock, redis):
    """
    Tests RedisBackedDocument's handling of large documents.

    The number of bytes from which on a document is stored in redis is set to a
    lower value here (100 instead of 100_000_000) in order to improve test
    performance.
    """
    test_content = ' '.join(['testWord1 testWord2'] * 100)

    document = await RedisBackedDocument.from_string(test_content)
    stored_content = await document.get_content()

    assert stored_content.decode() == test_content
    assert document.is_stored_in_redis
