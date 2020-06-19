#!/usr/bin/env python3
import glob
import subprocess
from pathlib import Path

from pipeline import app, read_files
from settings import DATA_DIR

@app.command()
async def load_document_small() -> None:
    """
    Loads a small document (30KB, will be stored in Kafka) into the pipeline.
    """
    await read_files.send(value=f'{DATA_DIR}/A01586.headed.txt')


@app.command()
async def load_document_large() -> None:
    """
    Loads a large document (1.1MB, will be stored in Redis) into the pipeline.
    """
    await read_files.send(value=f'{DATA_DIR}/A01658.headed.txt')


@app.command()
async def load_all_documents() -> None:
    """
    Loads all documents (103MB) into the pipeline.
    """
    for file_path in glob.iglob(f'{DATA_DIR}/*'):
        await read_files.send(value=file_path)


@app.command()
async def test() -> None:
    """
    Runs the test suite using pytest.
    """
    subprocess.call(['pytest'])


if __name__ == '__main__':
    app.main()
