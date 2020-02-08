import io
import os
from pathlib import Path
import warnings

import pandas as pd
from PIL import Image
import requests
import streamlit as st

BASE_PATH = Path(__file__).parents[2]
DATA_DIR = BASE_PATH.joinpath('data', 'raw', 'picts')


@st.cache
def get_image(url):

    response = requests.get(url)
    if response.status_code != 200:
        warnings.warn('Error %i ' % response.status_code)
    else:
        try:
            img = Image.open(io.BytesIO(response.content))
            return img
        except OSError as e:
            warnings.warn(e)


def get_urls(data_path=BASE_PATH.joinpath('data', 'interim',
                                          'products_interim.pickle')):
    data = pd.read_pickle(data_path)
    urls = data[['image_url', 'code']]
    return urls
