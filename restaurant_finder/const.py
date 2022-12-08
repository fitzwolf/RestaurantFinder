from pathlib import Path

# file structure consts
FULL_DATASET_FILE_PREFIX = 'yelp_academic_dataset_'
RESTAURANT_DATASET_FILE_PREFIX = 'yelp_academic_restaurant_dataset_'
FILTERED_DATASET_DIR = 'dataset'
ABS_DATASET_DIR_PATH = Path(__file__).parent.absolute().parent / FILTERED_DATASET_DIR
RESTAURANT_DATASET_FILENAME = ABS_DATASET_DIR_PATH / (RESTAURANT_DATASET_FILE_PREFIX + 'business.json')
RESTAURANT_INDEX_FILENAME = ABS_DATASET_DIR_PATH / 'restaurant_idx.json'
REVIEW_DATASET_FILENAME = ABS_DATASET_DIR_PATH / (RESTAURANT_DATASET_FILE_PREFIX + 'review.json')
REVIEW_TXT_BIZ_ID_FILENAME = ABS_DATASET_DIR_PATH / 'review_txt_business_id.txt'
REVIEW_CORPUS_FILENAME = ABS_DATASET_DIR_PATH / 'review' / 'review.dat'
REVIEW_CORPUS_CFG_FILENAME = ABS_DATASET_DIR_PATH / 'review' / 'line.toml'

# search
INTERNAL_SEARCH_RESULT_COUNT = 100
SEARCH_RESULT_COUNT = 10

# location based sorting
MAX_RANK_DIFFERENCE = 40
MIN_DISTANCE_DIFFERENCE = 200  # in miles
