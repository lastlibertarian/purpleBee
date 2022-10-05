import os.path
from whoosh.index import create_in, open_dir
from whoosh.fields import *
from whoosh.qparser import QueryParser

INDEX_DIRECTORY = f'{os.path.abspath(os.path.join(__file__, "../../.."))}/index'

if not os.path.exists(INDEX_DIRECTORY):
    os.mkdir(INDEX_DIRECTORY)
    schema = Schema(message_id=TEXT(stored=True),
                    user_id=TEXT(stored=True),
                    content=TEXT)
    create_in(INDEX_DIRECTORY, schema)

ix = open_dir(INDEX_DIRECTORY)
writer = ix.writer()
searcher = ix.searcher()


