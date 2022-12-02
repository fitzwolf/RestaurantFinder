import argparse
import shutil
import sys

import orjson

from const import *


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
    biz_ids = []
    with open(dataset_path / (FULL_DATASET_FILE_PREFIX + 'business.json'), 'r', encoding='utf8') as r:
        for line in r:
            biz = orjson.loads(line)
            if biz['categories'] is None:
                continue
            biz_cats = [x.strip() for x in biz['categories'].split(',')]
            for category in biz_cats:
                if category.lower() in restaurant_cat_list:
                    restaurants.append(biz)
                    biz_ids.append(biz['business_id'])
                    break
    return restaurants, biz_ids


def get_reviews(dataset_path, biz_ids, review_limit_per_biz, review_len_limit):
    # converting list to set to speed up performance
    biz_ids = set(biz_ids)
    biz_review_count = {}
    reviews = []
    review_txts = []

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
                review['text'] = review['text'][:review_len_limit]
                reviews.append(review)

                # each line of corpus should be one review
                review['text'] = review['text'].replace('\r', '')
                review['text'] = review['text'].replace('\n', '')
                review_txts.append(review['text'])
    return reviews, review_txts


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
    restaurants, biz_ids = get_restaurants(dataset_path)
    assert len(restaurants) == len(biz_ids)

    print('Writing restaurants to file...')
    write_file(BIZ_DATASET_FILENAME, orjson.dumps(restaurants), True)

    print('Writing restaurants ids to file...')
    write_file(BIZ_ID_FILENAME, '\n'.join(biz_ids))

    print('Getting reviews of the restaurants...this will take some time')
    reviews, review_txts = get_reviews(dataset_path, biz_ids, review_limit, review_len_limit)
    assert len(reviews) == len(review_txts)

    print('Writing reviews to file...this will take some time')
    write_file(REVIEW_DATASET_FILENAME, orjson.dumps(reviews), True)

    print('Writing review texts to file...this will take some time')
    write_file(REVIEW_CORPUS_FILENAME, '\n'.join(review_txts))

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

    create_dir_struct()
    filter_dataset(dataset_dirpath, args.review_limit, args.review_length_limit)

    sys.exit(0)
