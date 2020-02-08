from pathlib import Path

import streamlit as st
import pandas as pd

from src.demo_app import get_product_image

BASE_PATH = Path(__file__).parents[2]

products = ['3017620402678',
            '8714100380383',
            '3350031913563',
            '3215200000775',
            '00189095',
            ]


@st.cache
def load_data(path):
    data = pd.read_pickle(path)
    return data

def display_product(product_infos):
    st.header(product_infos.get('product_name'))
    st.image(get_product_image.get_image(product_infos.get('image_url')))
    st.markdown(f'**Nutriscore** {product_infos.get("nutriscore_grade").upper()}')
    display_infos(product_infos)

def display_energy(energy):
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

    st.write(pd.DataFrame({'Pour 100g' : [fat, saturated_fat,
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


st.title("Demo app V 0.1")
st.text('Project path:')
st.write(BASE_PATH)


data = load_data(BASE_PATH.joinpath('data', 'processed',
                                    'products.pickle'))

data = data[data['image_url'].notnull()]

product = st.sidebar.selectbox(options=products, label='select a product')
product_infos = data[data['code'] == product].iloc[0, :]

st.sidebar.markdown("**Produit :** " + product_infos['product_name'])
n_prod = st.sidebar.number_input('Nombre maximum de produits à afficher.',
                                 value=10)

display_product(product_infos.to_dict())


st.title('Résultats de la recherche')
related_products = data[data['pnns_groups_2'] == product_infos['pnns_groups_2']]
related_products = related_products[related_products['main_category_en'] == product_infos.main_category_en]

related_products.sort_values('nutriscore_grade', ascending=True, inplace=True)

st.info(f"Nombre de produits trouvés {related_products.shape[0]}")

for i in range(n_prod):
    product = related_products.iloc[i, :]
    display_product(product.to_dict())
