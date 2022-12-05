import argparse
import shutil
import sys
import time

import orjson

from const import *
from switches import *


def get_biz_categories(dataset_path):
    categories = []
    with open(dataset_path / (FULL_DATASET_FILE_PREFIX + 'business.json'), 'r', encoding='utf8') as r:
        for line in r:
            biz = orjson.loads(line)
            if biz['categories'] is None:
                continue
            biz_cats = [x.strip() for x in biz['categories'].split(',')]
            for cat in biz_cats:
                if cat not in categories:
                    categories.append(cat)
    return sorted(categories)


def get_restaurants(dataset_path):
    restaurant_cat_list = ['restaurants', 'pop-up restaurants']
    restaurants = []
    restaurant_idx = {}
    with open(dataset_path / (FULL_DATASET_FILE_PREFIX + 'business.json'), 'r', encoding='utf8') as r:
        for line in r:
            biz = orjson.loads(line)
            if biz['categories'] is None:
                continue
            biz_cats = [x.strip() for x in biz['categories'].split(',')]
            for category in biz_cats:
                if category.lower() in restaurant_cat_list:
                    restaurants.append(biz)
                    biz_id = biz['business_id']
                    if biz_id in restaurant_idx:
                        raise KeyError(f'Business id, {biz_id}, already exists in the restaurant index dict. '
                                       f'Business id should be unique in the business dataset.')
                    restaurant_idx[biz_id] = len(restaurants) - 1
                    break
    return restaurants, restaurant_idx


def expand_review_with_categories(restaurant, review_txt):
    expanded_review = ''
    expanded_review += review_txt
    categories = restaurant['categories']
    if categories is None or categories.strip() == '':
        return expanded_review
    for c in restaurant['categories'].split(','):
        c = c.lower().strip()
        category_words = c.split(' ')
        for word in category_words:
            word = word.strip()
            if word == '&' or word == 'and' or 'restaurant' in word:
                continue
            # if category word already exists in review then not adding it again to the review
            # otherwise I think duplicate word can increase emphasis on that word
            if word not in review_txt:
                expanded_review = word + ' ' + expanded_review
    return expanded_review


def get_reviews(dataset_path, restaurants, restaurant_idx, review_limit_per_biz, review_len_limit):
    # converting list to set to speed up performance
    biz_ids = set(restaurant_idx.keys())
    biz_review_count = {}
    reviews = []
    review_txts = []
    review_txt_biz_ids = []

    for i in biz_ids:
        biz_review_count[i] = 0

    with open(dataset_path / (FULL_DATASET_FILE_PREFIX + 'review.json'), 'r', encoding='utf8') as r:
        for line in r:
            review = orjson.loads(line)
            biz_id = review['business_id']
            if biz_id in biz_ids:
                biz_review_count[biz_id] += 1
                if biz_review_count[biz_id] > review_limit_per_biz:
                    continue
                review = {
                    'business_id': review['business_id'],
                    'stars': review['stars'],
                    'text': review['text']
                }
                reviews.append(review)
                review_txt = review['text'][:review_len_limit].lower()

                # each line of corpus should be one review
                review_txt = review_txt.replace('\r', '')
                review_txt = review_txt.replace('\n', '')

                if review_expansion_enabled:
                    review_txt = expand_review_with_categories(restaurants[restaurant_idx[biz_id]], review_txt)

                # remove the term 'restaurant' from review text and add it to the end of each restaurant
                # this is to avoid 'restaurant' term in the query from affecting ranking
                review_txt = review_txt.replace('restaurants', '')
                review_txt = review_txt.replace('restaurant', '')
                review_txt = review_txt + 'restaurant'

                review_txts.append(review_txt)
                review_txt_biz_ids.append(review['business_id'])
    return reviews, review_txts, review_txt_biz_ids


def print_top_review_counts_per_biz(biz_ids, reviews):
    biz_review_count = {}
    biz_ids = set(biz_ids)
    for i in biz_ids:
        biz_review_count[i] = 0
    for review in reviews:
        if review['business_id'] in biz_ids:
            biz_review_count[review['business_id']] += 1
    print(
        f'Top 3 counts of reviews per business - {sorted(set(biz_review_count.values()), reverse=True)[0:3]}')


def print_top_review_length(reviews):
    review_length = []
    for review in reviews:
        review_length.append(len(review['text']))
    print(
        f'Top 3 review lengths - {sorted(set(review_length), reverse=True)[0:3]}')


def clean_existing_dataset():
    if Path(ABS_DATASET_DIR_PATH).exists():
        shutil.rmtree(ABS_DATASET_DIR_PATH)


def create_dir_struct():
    Path(ABS_DATASET_DIR_PATH).mkdir(exist_ok=True)
    Path(ABS_DATASET_DIR_PATH / 'review').mkdir(exist_ok=True)


def write_file(filename, data, is_binary_mode=False):
    if is_binary_mode:
        with open(filename, 'wb') as file:
            file.write(data)
    else:
        with open(filename, 'w', newline='\n', encoding='utf8') as file:
            file.write(data)


def filter_dataset(dataset_path, review_limit, review_len_limit):
    print('Getting restaurants...')
    restaurants, restaurant_idx = get_restaurants(dataset_path)
    assert len(restaurants) == len(restaurant_idx.keys())

    print('Writing restaurants to a file...')
    write_file(RESTAURANT_DATASET_FILENAME, orjson.dumps(restaurants), True)

    print('Writing restaurant index to a file...')
    write_file(RESTAURANT_INDEX_FILENAME, orjson.dumps(restaurant_idx), True)

    print('Getting reviews of the restaurants...this will take some time')
    reviews, review_txts, review_txt_biz_ids = get_reviews(dataset_path, restaurants, restaurant_idx, review_limit,
                                                           review_len_limit)
    if not combine_reviews_enabled:
        assert len(reviews) == len(review_txts)
    assert len(review_txts) == len(review_txt_biz_ids)

    print('Writing reviews to a file...this will take some time')
    write_file(REVIEW_DATASET_FILENAME, orjson.dumps(reviews), True)

    print('Writing review texts to a file...this will take some time')
    write_file(REVIEW_CORPUS_FILENAME, '\n'.join(review_txts))

    print('Writing business id associated to the review texts to a file...')
    write_file(REVIEW_TXT_BIZ_ID_FILENAME, '\n'.join(review_txt_biz_ids))

    if not combine_reviews_enabled:
        with open(REVIEW_CORPUS_FILENAME, 'r', encoding='utf8') as review_corpus:
            print('Checking review corpus length is same as number of reviews in dataset...')
            assert len(review_corpus.readlines()) == len(reviews)

    print('Writing review corpus configuration file...')
    write_file(REVIEW_CORPUS_CFG_FILENAME, "type = \"line-corpus\"")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Filter dataset')
    parser.add_argument('-p', '--dataset-dirpath', required=True, help='Full dataset path')
    parser.add_argument('--review-limit', type=int, default=100, help='Review limit per restaurant, default=100')
    parser.add_argument('--review-length-limit', type=int, default=5000, help='Review char length limit, default=5000')
    parser.add_argument('--skip-clean', action='store_true', help='Skip cleaning of existing filtered dataset')
    args = parser.parse_args()

    dataset_dirpath = Path(args.dataset_dirpath)
    if not Path(args.dataset_dirpath).exists():
        print('Dataset path provided does not exist. Exiting.')
        sys.exit(1)

    if not args.skip_clean:
        print('Cleaning existing dataset...')
        clean_existing_dataset()

    start_time = time.time()

    create_dir_struct()
    filter_dataset(dataset_dirpath, args.review_limit, args.review_length_limit)

    print(f'Time taken: {round(time.time() - start_time, 2)} seconds')
    sys.exit(0)
