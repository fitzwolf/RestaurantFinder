# Restaurant Finder Evaluation

## Setup

Download yelp dataset from https://www.yelp.com/dataset and extract it.

Apply your yelp API KEY from https://docs.developer.yelp.com/docs/fusion-authentication and paste you API KEY on the fourth line in const.py

### Install required packages

```commandline
cd restaurant_finder_evaluation
pip install -r requirements.txt
```

### Filter and prepare restaurant dataset for indexing

This has to be done one time only.

```commandline
python dataset_eval.py -p <path-of-dataset>
```

## Running Restaurant Finder Evaluation

```commandline
python evaluation.py
```

## Usage of dataset_eval.py

```commandline
$ python dataset_eval.py --help

usage: dataset_eval.py [-h] -p DATASET_DIRPATH [--review-limit REVIEW_LIMIT]
                  [--review-length-limit REVIEW_LENGTH_LIMIT] [--skip-clean]

Filter dataset

optional arguments:
  -h, --help            show this help message and exit
  -p DATASET_DIRPATH, --dataset-dirpath DATASET_DIRPATH
                        Full dataset path
  --review-limit REVIEW_LIMIT
                        Review limit per restaurant, default=100
  --review-length-limit REVIEW_LENGTH_LIMIT
                        Review char length limit, default=5000
  --skip-clean          Skip cleaning of existing filtered dataset
```
