import logging
from hashlib import sha256
from operator import itemgetter

from faust.utils.terminal import table as terminal_table


class WordCountLogger:
    """
    Logs the current state of a table containing the word counts.

    The table is printed only if its representation has changed since the last
    invocation of print(). The table is sorted by the ocurrences of a word in
    descending order. The head=n parameter can be used to only print the top n
    words
    """
    _last_table_hash = None

    @classmethod
    def print(cls, table, head=None):
        data = list(reversed(sorted(table.items(), key=itemgetter(1))))
        if head is not None:
            data = data[:head]
        table_string = terminal_table(
            title='wordcount',
            data=[['word', 'count']] + data
        ).table
        table_hash = sha256(table_string.encode()).hexdigest()
        if table_hash != cls._last_table_hash:
            cls._last_table_hash = table_hash
            logging.warning(f'\n{table_string}')
