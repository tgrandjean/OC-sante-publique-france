"""Script to run to lauch the demo app.

:usage:
    $ streamlit run ./src/demo_app/demo.py
"""
from pathlib import Path

import streamlit as st

from src.demo_app.app_assets import load_data, display_product

BASE_PATH = Path(__file__).parents[2]

products = ['3017620402678',
            '8714100380383',
            '3350031913563',
            '3215200000775',
            '00189095',
            ]

st.title("Demo app V 0.1")
st.text('Project path:')
st.write(BASE_PATH)


data = load_data(BASE_PATH.joinpath('data', 'processed',
                                    'products.pickle'))

data = data[data['image_url'].notnull()]

st.sidebar.markdown("Select a product or enter a code product.")
custom = st.sidebar.checkbox('Custom code', value=False, key=None)
if custom:
    product = st.sidebar.text_input('code produit :', value=products[0])
else:
    product = st.sidebar.selectbox(options=products, label='select a product')

if product:
    product_infos = data[data['code'] == product].iloc[0, :]

    st.sidebar.markdown("**Produit :** " + product_infos['product_name'])
    n_prod = st.sidebar.number_input('Nombre maximum de produits à afficher.',
                                     value=10)

    display_product(product_infos.to_dict())


    st.title('Résultats de la recherche')
    related_products = data[data['pnns_groups_2'] ==
                            product_infos['pnns_groups_2']]
    related_products = related_products[related_products['main_category_en'] ==
                                        product_infos.main_category_en]

    related_products.sort_values('nutriscore_grade', ascending=True,
                                 inplace=True)

    st.info(f"Nombre de produits trouvés {related_products.shape[0]}")

    for i in range(n_prod):
        product = related_products.iloc[i, :]
        display_product(product.to_dict())
