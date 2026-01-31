import streamlit as st
import pandas as pd

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('SortCart.csv')
    return df

df = load_data()

st.title("📍 Address & Beat Lookup App")
st.write("Enter the details below to find associating information from the SortCart database.")

# Sidebar for different search modes
search_mode = st.sidebar.radio("Search by:", ["Street Address", "ID Number", "Beat Number"])

if search_mode == "Street Address":
    col1, col2 = st.columns(2)
    with col1:
        street_input = st.text_input("Enter Street Name (e.g., Ashby Avenue)").upper()
    with col2:
        number_input = st.number_input("Enter Street Number", min_value=1, step=1)

    if street_input:
        # Filter for street and parity (Even/Odd)
        parity = 2 if number_input % 2 == 0 else 1
        results = df[
            ((df['StreetName'].str.upper() == street_input) | (df['StreetNameShort'].str.upper() == street_input)) &
            (df['EvenOdd'] == parity) &
            (df['StreetNoMin'] <= number_input) &
            (df['StreetNoMax'] >= number_input)
        ]
       
        if not results.empty:
            st.success(f"Found {len(results)} match(es)!")
            st.dataframe(results)
        else:
            st.warning("No matches found for that address.")

elif search_mode == "ID Number":
    id_input = st.text_input("Enter ID Number(s) - separate by comma for multiple")
    if id_input:
        ids = [int(i.strip()) for i in id_input.split(',')]
        results = df[df['id'].isin(ids)]
        st.dataframe(results)

elif search_mode == "Beat Number":
    beat_input = st.number_input("Enter Beat Number", min_value=0, step=1)
    if beat_input:
        results = df[df['BeatNo'] == beat_input]
        st.dataframe(results)

st.divider()
st.caption("Data source: SortCart.csv")
 