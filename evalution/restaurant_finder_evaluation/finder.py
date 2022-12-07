import json
import shutil

import metapy
import toml

from const import *


def get_file_contents(filepath, file_type):
    with open(str(filepath), 'r', encoding='utf8') as file:
        if file_type == 'json':
            return json.loads(file.read())
        else:
            return file.read()


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
    def __init__(self, cfg_filename, num_results, location):
        self.cfg_filename = cfg_filename
        self.cfg = toml.load(cfg_filename)
        self.num_results = num_results
        self.idx = None
        self.ds = DataStore(location)

        self.review_txt_biz_id = get_file_contents(
            self.ds.REVIEW_TXT_BIZ_ID_FILENAME, file_type='text').split('\n')
        self.restaurants = get_file_contents(
            self.ds.RESTAURANT_DATASET_FILENAME, file_type='json')
        self.restaurant_idx = get_file_contents(
            self.ds.RESTAURANT_INDEX_FILENAME, file_type='json')

        print(len(self.review_txt_biz_id))

    def cleaning_existing_index(self):
        index_name = self.cfg.get('index')
        index_dirpath = Path(__file__).parent.absolute() / index_name
        if index_dirpath.exists():
            print('Cleaning existing index...')
            shutil.rmtree(str(index_dirpath))

    def make_inverted_index(self):
        print("Inverting index...")
        prefix = self.cfg.get('prefix')
        self.cfg['prefix'] = prefix + '/' + self.ds.parent
        with open('temp.toml', 'w') as f:
            toml.dump(self.cfg, f)
        self.idx = metapy.index.make_inverted_index('temp.toml')
        return self.idx

    def print_index_stats(self):
        print('Index stats:')
        print(f'Number of reviews - {self.idx.num_docs()}')
        print(f'Number of terms - {self.idx.total_corpus_terms()}')
        print(f'Number of unique terms - {self.idx.unique_terms()}')
        print(f'Average review length - {self.idx.avg_doc_length()}')

    def find_restaurants(self, query_str):
        print('Started to search for "{}" in app.'.format(
            query_str))
        search_results = []
        query = metapy.index.Document()
        query.content(query_str)
        ranker = metapy.index.OkapiBM25()
        print('Ranking results...')
        ranked_results = ranker.score(
            self.idx, query, num_results=self.num_results)

        # print(ranked_results)
        for review_idx, _ in ranked_results:
            idx = self.restaurant_idx[self.review_txt_biz_id[review_idx]]
            restaurant = self.restaurants[idx]

            # restaurant = restaurants[biz_ids.index(
            # reviews[review_idx]['business_id'])]
            search_results.append(remove_keys(restaurant))

        return search_results
