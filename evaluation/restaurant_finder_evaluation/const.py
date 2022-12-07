from pathlib import Path
import shutil

API_KEY = "PASTE YOUR YELP API KEY HERE"
FULL_DATASET_FILE_PREFIX = 'yelp_academic_dataset_'
RESTAURANT_DATASET_FILE_PREFIX = 'yelp_academic_restaurant_dataset_'
FILTERED_DATASET_DIR = 'dataset'
SEARCH_RESULT_COUNT = 50
CITIES = ['Philadelphia', 'Tampa', 'Indianapolis']
SEARCH_TERMS = ['tacos', 'italian', 'pasta', 'steak', 'thai']


class DataStore:
    def __init__(self, location=None):
        '''Setup path for processed Yelp dataset for given location.'''
        self.location = location
        self.ABS_DATASET_DIR_PATH = Path(
            __file__).parent.absolute().parent / FILTERED_DATASET_DIR
        if location is not None:
            self.parent = self.location.lower().replace(' ', '_')
            self.location_dir = self.ABS_DATASET_DIR_PATH / self.parent
        else:
            self.parent = None
            self.location_dir = self.ABS_DATASET_DIR_PATH

        # self.BIZ_DATASET_FILENAME = self.location_dir / 'business.json'
        # self.BIZ_ID_FILENAME = self.location_dir / 'business_id.txt'
        self.RESTAURANT_DATASET_FILENAME = self.location_dir / 'business.json'
        self.RESTAURANT_INDEX_FILENAME = self.location_dir / 'restaurant_idx.json'
        self.REVIEW_DATASET_FILENAME = self.location_dir / 'review.json'
        self.REVIEW_TXT_BIZ_ID_FILENAME = self.location_dir / 'review_txt_business_id.txt'
        self.REVIEW_CORPUS_FILENAME = self.location_dir / 'review' / 'review.dat'
        self.REVIEW_CORPUS_CFG_FILENAME = self.location_dir / 'review' / 'line.toml'

    def clean(self):
        '''Delete all the existing folders in dataset folder.'''
        print('Cleaning existing dataset...')
        if self.location_dir.exists():
            shutil.rmtree(self.location_dir.as_posix())

    def create_dir_struct(self, skip_clean=True):
        '''Create a folder called dataset and store each city's dataset 
        folder with its corresponding dataset inside dataset folder.
        '''
        if not skip_clean:
            self.clean()
        self.ABS_DATASET_DIR_PATH.mkdir(exist_ok=True)
        self.location_dir.mkdir(exist_ok=True)
        (self.location_dir / 'review').mkdir(exist_ok=True)
