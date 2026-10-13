# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(f":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
  """Choose the fruits you want in your custome smoothie.
  """
)

name_on_order = st.text_input("Name on Smoothie")
st.write("The name on ur smoothie will be", name_on_order)

cnx=st.connection("snowflake")
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
#st.dataframe(data=my_dataframe, use_container_width=True)

ingredients_list = st.multiselect('Choose upto 5 ingredients:',
                                 my_dataframe,
                                 max_selections=5)

if ingredients_list:
    ingredients_string = ''
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        st.subheader(fruit_chosen+'Nutritional_information')
        fruit_url = "https://my.smoothiefroot.com/api/fruit/" + fruit_chosen
        smoothiefroot_response = requests.get(f"[{fruit_url}]({fruit_url})")
        st.write("Status code:", smoothiefroot_response.status_code)
        if smoothiefroot_response.status_code == 200:
           sf_df = st.dataframe(data=smoothiefroot_response.json(),use_container_width=True)
        else:
           st.error("Unable to retrieve nutritional information.")
    st.write(ingredients_string)
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                    values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    #st.write(my_insert_stmt)
    #st.stop()
    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
