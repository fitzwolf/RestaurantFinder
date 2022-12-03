from urllib.parse import unquote

import metapy
from flask import Flask, request, jsonify

from const import SEARCH_RESULT_COUNT
from finder import Finder

app = Flask(__name__)


@app.route('/find')
def find():
    search_query = request.args.get('q')

    if search_query is None:
        return jsonify([])

    search_query = unquote(search_query)
    response = jsonify(finder.find_restaurants(search_query))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


def init_finder():
    fndr = Finder('config.toml', SEARCH_RESULT_COUNT)
    fndr.cleaning_existing_index()
    fndr.make_inverted_index()
    fndr.print_index_stats()
    return fndr


if __name__ == '__main__':
    metapy.log_to_stderr()
    finder = init_finder()
    app.run(port=8080, threaded=False)
