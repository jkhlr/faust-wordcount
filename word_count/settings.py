import os

FAUST_BROKER = os.getenv('FAUST_WORDCOUNT_BROKER', 'kafka://localhost:9094')
REDIS_HOST = os.getenv('FAUST_WORDCOUNT_REDIS_HOST', 'localhost')
REDIS_PORT = os.getenv('FAUST_WORDCOUNT_REDIS_PORT', '6379')
DATA_DIR = os.getenv('FAUST_WORDCOUNT_DATA_DIR', 'vep_data')
