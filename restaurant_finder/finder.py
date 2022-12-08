import shutil

import metapy
import orjson
import toml
from geopy import distance

from const import *
from switches import *


def get_file_contents(filename, file_type):
    if file_type == 'json':
        with open(filename, 'r', encoding='utf8') as file:
            return orjson.loads(file.read())
    else:
        with open(filename, 'r', encoding='utf8') as file:
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

    def __init__(self, cfg_filename, num_results):
        self.cfg_filename = cfg_filename
        self.cfg = toml.load(cfg_filename)
        self.num_results = num_results
        self.idx = None
        self.loc_sorted_results = []
        self.final_search_results = []

        self.review_txt_biz_id = get_file_contents(REVIEW_TXT_BIZ_ID_FILENAME, file_type='text').split('\n')
        self.restaurants = get_file_contents(RESTAURANT_DATASET_FILENAME, file_type='json')
        self.restaurant_idx = get_file_contents(RESTAURANT_INDEX_FILENAME, file_type='json')

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

    def add_nearest_key(self):
        if 'distance' not in self.final_search_results[0]:
            return

        nearest_restaurant_id = sorted(self.final_search_results, key=lambda x: x['distance'])[0]['business_id']
        for result in self.final_search_results:
            if result['business_id'] == nearest_restaurant_id:
                result['nearest'] = True
            else:
                result['nearest'] = False

    def combine_location_sorted_and_orig_results(self, search_results):
        if len(self.loc_sorted_results) == 0:
            return

        restaurant_id = self.loc_sorted_results[0]['business_id']
        search_idx = None

        for idx, s_result in enumerate(search_results):
            if s_result['business_id'] == restaurant_id:
                search_idx = idx
                break

        if search_idx is None:
            self.final_search_results.append(self.loc_sorted_results[0])
        else:
            rank_diff = search_idx
            distance_diff = abs(search_results[0]['distance'] - search_results[search_idx]['distance'])
            if rank_diff < ACCEPTABLE_RANKING_DIFFERENCE and distance_diff > ACCEPTABLE_DISTANCE_DIFFERENCE:
                self.final_search_results.append(self.loc_sorted_results[0])
            else:
                self.final_search_results.append(search_results[search_idx])

        self.loc_sorted_results.pop(0)
        if search_idx is not None:
            search_results.pop(search_idx)
        self.combine_location_sorted_and_orig_results(search_results)

    def sort_by_rank_and_location(self, search_results, user_location):
        if not location_based_sorting or user_location[0] is None or user_location[1] is None:
            self.final_search_results = search_results

        for result in search_results:
            restaurant_location = (result['latitude'], result['longitude'])
            result['distance'] = round(distance.distance(user_location, restaurant_location).miles, 2)
        self.loc_sorted_results = sorted(search_results, key=lambda x: x['distance'])
        self.combine_location_sorted_and_orig_results(search_results)

    def find_restaurants(self, query_str, num_results, user_location):
        self.final_search_results = []
        self.num_results = num_results
        search_results = []
        query = metapy.index.Document()
        query.content(query_str)
        ranker = metapy.index.OkapiBM25()

        if self.num_results > INTERNAL_SEARCH_RESULT_COUNT:
            ranked_results = ranker.score(self.idx, query, num_results=self.num_results)
        else:
            ranked_results = ranker.score(self.idx, query, num_results=INTERNAL_SEARCH_RESULT_COUNT)

        for review_idx, _ in ranked_results:
            idx = self.restaurant_idx[self.review_txt_biz_id[review_idx]]
            restaurant = self.restaurants[idx]
            search_results.append(remove_keys(restaurant))

        if location_based_sorting:
            self.sort_by_rank_and_location(search_results, user_location)
        else:
            self.final_search_results = search_results

        if len(self.final_search_results) >= self.num_results:
            self.final_search_results = self.final_search_results[:self.num_results]
            self.add_nearest_key()
            return self.final_search_results
        else:
            self.add_nearest_key()
            return self.final_search_results
