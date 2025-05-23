# Import python packages
import requests
import pandas
import streamlit as st
# from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

helpful_links = [
    "https://docs.streamlit.io",
    "https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit",
    "https://github.com/Snowflake-Labs/snowflake-demo-streamlit",
    "https://docs.snowflake.com/en/release-notes/streamlit-in-snowflake"
]

cnx = st.connection('snowflake')
session = cnx.session()

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

# option = st.selectbox(
#     "What is your favorite fruit?",
#     ("Banana", "Strawberries", "Peaches"),
#     index=None,
#     placeholder="Select favorite fruit...",
# )

# st.write("Your favorite fruit is:", option)

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'));
# st.dataframe(data=my_dataframe, use_container_width=True)
pd_df = my_dataframe.to_pandas()

name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

ingredients_list = st.multiselect(
    'Choose upto 5 ingredients',
    my_dataframe,
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        # st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.header(fruit_chosen + 'Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        # st.text(smoothiefroot_response)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
    # st.write(ingredients_string)

    time_to_insert = st.button('Submit order')
    
    if time_to_insert:
        my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

        # st.write(my_insert_stmt)

        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")

