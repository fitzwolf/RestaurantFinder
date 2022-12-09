<h1 align="center">Restaurant Finder</h1>
<div align="center">A Chrome extension to search restaurants based on user's search query</div>
<br /><br />
<div align="center">
<span><img src="screenshot/default-ui.jpg" width="250" align="top"></span>
<span><img src="screenshot/ui-20-results-location-enabled.jpg" width="250" align="top"></span>
<span><img src="screenshot/ui-40-results-location-disabled.jpg" width="250" align="top"></span>
</div>
<br /><br />

## Table of Contents

- [Overview](#overview)
- [Components](#components)
- [Flow](#flow)
- [Search Dataset](#search-dataset)
- [Video on Usage and Setup](#video-on-usage-and-setup)
- [Requirements](#requirements)
- [Setup](#setup)
    * [Setup Restaurant Finder Search App](#setup-restaurant-finder-search-app)
        * [Download dataset](#download-dataset)
        * [Create and activate virtual environment](#create-and-activate-virtual-environment)
        * [Install required packages](#install-required-packages)
        * [Filter and prepare restaurant dataset for indexing](#filter-and-prepare-restaurant-dataset-for-indexing)
    * [Setup Restaurant Finder Chrome Extension](#setup-restaurant-finder-chrome-extension)
- [Usage](#usage)
    * [Running search app](#running-search-app)
    * [Searching for restaurants](#searching-for-restaurants)
- [Misc](#misc)
    * [Get list of restaurants based on query](#get-list-of-restaurants-based-on-query)
    * [Query Parameters of find API](#query-parameters-of-em-find-em-api)
    * [Usage of dataset.py](#usage-of-datasetpy)
- [Notes to the reviewer](#notes-to-the-reviewer)

## Overview

Restaurant Finder is a Chrome extension powered by a search app that returns relevant restaurant results near the
user’s current location based on user's search query.

## Components

Restaurant finder is composed of a <strong>search</strong> app that runs in the background and a <strong>Chrome
extension</strong> that handles the UI interactions. To run this project, you will need to setup both components.

## Flow

User enters search query in the input field of the extension and clicks on 'Go'. The extension then invokes
"/find" API of the search app providing info about the search in the query parameters. The app responds with a ranked
list in JSON format containing restaurant info JSON objects that have info like restaurant name, address, stars,
location etc. This response is then used by the extension to return the search results back to the user.

## Search Dataset

For the dataset, we are using Yelp's open dataset to build inverted index for search and to return restaurant info
based on the ranked results. This dataset is a collection of datasets - business, checkin, review, tip, user. For our
purpose,
we only use business and review datasets which are linked to each other by business id.

## Video on Usage and Setup

You can look at the video Howto-Install-and-Use-720.mp4 that will guide you
through installation, setup and usage.

## Requirements

- Python version 3.7
- Google Chrome

## Setup

### Setup Restaurant Finder Search App

#### Download dataset

Download Yelp's open dataset from [Yelp Dataset](https://www.yelp.com/dataset) and extract it.

#### Create and activate virtual environment

To create virtual environment using Anaconda, you will first need to download it which you can get
from [Anaconda Distribution](https://www.anaconda.com/products/distribution). After you have installed Anaconda,
you can use below-mentioned commands to create and activate Python virtual environment. This step is optional but
recommended.

```commandline
$ conda create -n <virtual-env-name> python=3.7
$ conda activate <virtual-env-name>
```

#### Install required packages

```commandline
pip install -r requirements.txt
```

#### Filter and prepare restaurant dataset for indexing

This has to be done one time only.

```commandline
cd restaurant_finder
python dataset.py -p <path-of-dataset>
```

Check [Usage of dataset.py](#usage-of-datasetpy) for custom configuration

### Setup Restaurant Finder Chrome Extension

- Open Google Chrome.
- Browse "chrome://extensions/" or go to Settings > More Tools > Extensions.
- Enable "Developer mode" switch in the top right corner of the window.
- You should see a new button 'Load unpacked'.
- Click on 'Load unpacked' and select 'Chrome-Extension' folder located in your local copy of this repo.
- You should see 'Restaurant Finder' extension show up in the list of extensions.
- You can choose to pin this extension while you are testing by clicking on the 'Extensions' icon on the right side
  of the search bar and clicking on the pin icon.

## Usage

There are two steps to using Restaurant Finder. Details of each step is given in their respective sections.

- Run search app in the background
- Search restaurants using Chrome extension

### Running search app

Run the 'app.py' script. The app runs on localhost at port 8080. Let this app run while testing.

```commandline
python app.py
```

### Searching for restaurants

Note - The Restaurant finder Chrome Extension has access to your current location.

- Open Google Chrome.
- Click on the 'Restaurant Finder' extension.
- Provide your search query.
- Click 'Go' to see the search results.

You can click on 'Clear' to clear the search results. You can also adjust search configuration such as number of results
that will get returned, enable/disable location based search.

## Misc

### Get list of restaurants based on query

Invoke a GET request or just browse at path '/find' with query parameters. Response to the find API will be returned in
JSON format.

```commandline
http://localhost:8080/find?q=<search-query>&count=<count>&latitude=<latitude>&longitude=<longitude>
```

### Query Parameters of <em>find</em> API

Following are the parameters that the find API supports:

- q - Search query
- count - Number of results to be returned
- latitude - User's current location's latitude co-ordinate
- longitude - User's current location's longitude co-ordinate

### Usage of dataset.py

```commandline
$ python dataset.py --help

usage: dataset.py [-h] -p DATASET_DIRPATH [--review-limit REVIEW_LIMIT]
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

## Notes to the reviewer

- Python version - This project requires Python 3.7 and has been tested with only this version of Python.
- Setup - We recommend that you test on a clean setup by creating a virtual environment specifically for reviewing the
  project.
- Location access - Restaurant finder Chrome extension has access to the user's current location by default, and it
  cannot be turned off. There is no prompt where it will be requested.
- Location switch - "Enable location" switch that you see in Chrome extension is to send/not send the user's current
  location
  info to the search app. It does not affect the access of Chrome extension to the user's location.
- Location based result limitation - Even though the app supports location based results, you might not get the expected
  restaurants near your location.
  This limitation is due to the static, small and sparse dataset.
