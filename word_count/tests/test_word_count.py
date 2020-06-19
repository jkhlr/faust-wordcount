from asyncio import Future
from unittest.mock import patch, MagicMock, call

import aiofiles
import pytest

from pipeline import \
    RedisBackedDocument, \
    read_files, \
    split_documents, \
    count_words, \
    word_counts_table


def coroutine_mock():
    """ Returns a function that can be awaited to a return value of None """
    mock = MagicMock(return_value=Future())
    mock.return_value.set_result(None)
    return mock


@pytest.mark.asyncio()
@patch(
    'pipeline.split_documents.send',
    new_callable=coroutine_mock
)
async def test_read_files(mock, afs):
    """
    Tests if the read_files agent correctly reads a file with a given name and
    returns its content.

    The afs fixture provides a mocked file system.
    The .send() method of the split_documents agent is patched to check if the
    content of the file is forwarded correctly
    """
    test_file_name = 'test.txt'
    test_content = 'testWord1 testWord2'
    async with aiofiles.open(test_file_name, 'w') as f:
        await f.write(test_content)

    async with read_files.test_context() as agent:
        await agent.put(value=test_file_name)
        result = agent.results[0]

    assert await result.get_content() == test_content
    mock.assert_called_with(value=result)


@pytest.mark.asyncio()
@patch(
    'pipeline.count_words.send',
    new_callable=coroutine_mock
)
async def test_split_documents(mock):
    """
    Tests if the split_documents agent correctly splits a given document and
    returns all of its words.
.
    The .send() method of the count_words agent is patched to check if all words
    in the document are forwarded correctly
    """
    test_content = 'testWord1 testWord2'

    async with split_documents.test_context() as agent:
        await agent.put(RedisBackedDocument.from_string(test_content))
        results = [agent.results[0], agent.results[1]]

    assert results == test_content.split()
    mock.assert_has_calls([
        call(key=results[0], value=1),
        call(key=results[1], value=1)
    ])


@pytest.mark.asyncio()
async def test_count_words():
    """
    Tests if the count_words agent correctly counts given words using a table.
    """
    test_word = 'testWord'
    assert word_counts_table[test_word] == 0

    async with count_words.test_context() as agent:
        await agent.put(key='testWord', value=1)
        result = agent.results[0]

    assert result == test_word
    assert word_counts_table[test_word] == 1
