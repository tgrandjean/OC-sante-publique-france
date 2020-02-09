import io
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
    """Download image from openfoodfacts's website.

    :args:
        url (str) : media's URL
    :return:
        image (PIL.Image) : downloaded picture.
    """

    response = requests.get(url)
    if response.status_code != 200:
        warnings.warn('Error %i ' % response.status_code)
    else:
        try:
            img = Image.open(io.BytesIO(response.content))
            return img
        except OSError as e:
            warnings.warn(e)


@st.cache
def load_data(path):
    """Load data for the app.

    :args:
        path (str, path-like obj) : path of the dataset (pickle format)
    :return:
        data (pandas.DataFrame) : data as dataframe
    """
    data = pd.read_pickle(path)
    return data


def display_product(product_infos):
    """Display informations about a product.

    :args:
        product_infos (dict): dict contening all informations about a product
    """
    st.header(product_infos.get('product_name'))
    st.image(get_image(product_infos.get('image_url')))
    st.markdown(f'**Nutriscore** \
                {product_infos.get("nutriscore_grade").upper()}')
    display_infos(product_infos)


def display_energy(energy):
    """Create a fancy colored box contening the value.

    :args:
        energy (float, int) : value of energy.
    """
    s = "Valeur énergétique au 100g : "
    if energy < 500:
        st.success(f"{s} {energy} KJ")
    elif energy >= 500 and energy < 1200:
        st.info(f"{s} {energy} KJ")
    elif energy >= 1200 and energy < 2000:
        st.warning(f"{s} {energy} KJ")
    else:
        st.error(s + str(energy))


def display_infos(product_infos):
    """Display nutritional informations about a product

    :args:
        product_infos (dict): dict contening all informations about a product
    """
    energy = product_infos.get('energy_100g')
    display_energy(energy)
    fat = product_infos.get('fat_100g')
    saturated_fat = product_infos.get('saturated-fat_100g')

    carbohydrates = product_infos.get('carbohydrates_100g')
    sugars = product_infos.get('sugars_100g')

    proteins = product_infos.get('proteins_100g')

    fibers = product_infos.get('fiber_100g')

    salt = product_infos.get('salt_100g')
    sodium = product_infos.get('sodium_100g')

    st.write(pd.DataFrame({'Pour 100g': [fat, saturated_fat,
                                         proteins,
                                         carbohydrates, sugars,
                                         fibers,
                                         salt, sodium]},
                          index=['Matière grasse',
                                 'dont saturée',
                                 'protéines',
                                 'glucides',
                                 'dont sucre',
                                 'fibres',
                                 'sels',
                                 'dont sodium']))
