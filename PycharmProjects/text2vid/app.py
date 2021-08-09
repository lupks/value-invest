import os
import sys
from flask import Flask, request

from src.keyword_extraction import get_kw
from src.vid_dl import download_vid
from src.vid_editor import concat_vid

base_dir = os.getcwd()

"""
Flask App
"""
app = Flask(__name__)

app.route('/search', methods=['POST'])
def search():
    query = request.get_json(force=True)
    print(query)
    kw = get_kw(query['text'])

    output_dir = os.path.join(base_dir, 'data')
    download_vid(kw, output_dir)
    concat_vid(query['text'], kw, output_dir)

    return 'Video Creation Complete!'


if __name__ == "__main__":
    app.run()

output_dir = os.path.join(base_dir, 'data')
query_text = """

PLACE TEXT HERE

"""


kw = get_kw(query_text.replace('\n', ' '))
download_vid(kw, output_dir)
concat_vid(query_text, kw, output_dir)