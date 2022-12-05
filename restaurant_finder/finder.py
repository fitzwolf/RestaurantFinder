import json
import shutil

import metapy
import toml

from const import *


def get_file_contents(filename):
    with open(filename, 'r', encoding='utf8') as file:
        return json.loads(file.read())


def remove_keys(restaurant):
    removals = [
        'attributes',
        'categories',
        'hours',
        'is_open',
        'review_count'
    ]
    for key in removals:
        restaurant.pop(key, None)
    return restaurant


class Finder:

    def __init__(self, cfg_filename, num_results):
        self.cfg_filename = cfg_filename
        self.cfg = toml.load(cfg_filename)
        self.num_results = num_results
        self.idx = None

    def cleaning_existing_index(self):
        index_name = self.cfg.get('index')
        index_dirpath = Path(__file__).parent.absolute() / index_name
        if index_dirpath.exists():
            print('Cleaning existing index...')
            shutil.rmtree(index_dirpath)

    def make_inverted_index(self):
        print('Building index...this will take some time')
        self.idx = metapy.index.make_inverted_index(self.cfg_filename)
        return self.idx

    def print_index_stats(self):
        print('Index stats:')
        print(f'Number of reviews - {self.idx.num_docs()}')
        print(f'Number of terms - {self.idx.total_corpus_terms()}')
        print(f'Number of unique terms - {self.idx.unique_terms()}')
        print(f'Average review length - {self.idx.avg_doc_length()}')

    def find_restaurants(self, query_str):
        search_results = []
        query = metapy.index.Document()
        query.content(query_str)
        ranker = metapy.index.OkapiBM25()
        ranked_results = ranker.score(self.idx, query, num_results=self.num_results)

        reviews = get_file_contents(REVIEW_DATASET_FILENAME)
        restaurants = get_file_contents(RESTAURANT_DATASET_FILENAME)
        restaurant_idx = get_file_contents(RESTAURANT_INDEX_FILENAME)

        for review_idx, _ in ranked_results:
            idx = restaurant_idx[reviews[review_idx]['business_id']]
            restaurant = restaurants[idx]
            search_results.append(remove_keys(restaurant))

        return search_results
