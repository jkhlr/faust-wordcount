import aiofiles
import faust

from redis_backed_document import RedisBackedDocument
from settings import FAUST_BROKER
from word_count_logger import WordCountLogger

app = faust.App(
    id='word-count',
    broker=FAUST_BROKER
)

# Topic which holds file paths that should be read from
files_topic = app.topic(
    'files',
    value_type=str,
    internal=True
)
# Topic which holds documents that should be split
documents_topic = app.topic(
    'documents',
    value_type=RedisBackedDocument,
    internal=True
)

# Topic which holds words that should be counted, partitioned by word
words_topic = app.topic(
    'words',
    key_type=str,
    value_type=str,
    internal=True
)

# Distributed table which holds the current word counts
word_counts_table = app.Table(
    name='word_counts',
    default=int
)


@app.agent(files_topic)
async def read_files(file_paths):
    """
    Reads content from a received file path and sends a RedisBackedDocument
    constructed from the content to split_documents.
    """
    async for file_path in file_paths:
        async with aiofiles.open(file_path) as f:
            content = await f.read()
            document = await RedisBackedDocument.from_string(content)
            await split_documents.send(value=document)
            yield document


@app.agent(documents_topic)
async def split_documents(documents):
    """
    Loads content from a received RedisBackedDocument, splits it into words and
    sends each word to count_words.

    The stream of words is partitioned by the content of the words
    """
    async for document in documents:
        content = await document.get_content()
        for word in content.split():
            await count_words.send(key=word, value=1)
            yield word


@app.agent(words_topic)
async def count_words(words):
    """
    Records each received word and counts occurrences in a distributed table.

    The table is backed by changelog stream word_count-count_words-changelog
    """
    async for word, count in words.items():
        word_counts_table[word] += count
        yield word


@app.timer(interval=5, on_leader=True)
async def print_word_counts():
    """
    Prints top 10 words every 5 seconds (if they have changed).
    """
    WordCountLogger.print(word_counts_table, head=10)
