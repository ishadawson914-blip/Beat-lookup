import streamlit as st
import pandas as pd
import urllib.parse

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv('SortCart.csv')
    # Pre-calculate unique street names for the dropdown
    unique_streets = sorted(df['StreetName'].unique())
    return df, unique_streets

df, street_list = load_data()

# Function to create Google Maps link
def make_map_link(row, specific_no=None):
    num = specific_no if specific_no else row['StreetNoMin']
    address = f"{num} {row['StreetName']}, {row['Suburb']}, NSW {row['Postcode']}, Australia"
    query = urllib.parse.quote(address)
    return f"https://www.google.com/maps/search/?api=1&query={query}"

st.set_page_config(page_title="Leightonfield", layout="wide", initial_sidebar_state="expanded")

# Custom CSS for a cleaner mobile look
st.markdown("""
    <style>
    .stSelectbox div[data-baseweb="select"] { background-color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("📍 Sorting App")
st.sidebar.header("Search Settings")

# Search Type Selection
option = st.sidebar.selectbox("Search by:", ["Street Address", "ID Number", "Beat Number", "Suburb"])

results = pd.DataFrame()
searched_no = None

if option == "Street Address":
    col1, col2 = st.columns([3, 1])
    with col1:
        # Searchable dropdown: user types 2 letters and it filters
        st_name = st.selectbox(
            "Start typing Street Name...",
            options=street_list,
            index=None,
            placeholder="e.g. ASHBY"
        )
    with col2:
        st_no = st.number_input("Number", min_value=1, value=1)
        searched_no = st_no
   
    if st_name:
        parity = 2 if st_no % 2 == 0 else 1
        mask = (
            (df['StreetName'] == st_name) &
            (df['EvenOdd'] == parity) &
            (df['StreetNoMin'] <= st_no) &
            (df['StreetNoMax'] >= st_no)
        )
        results = df[mask].copy()

elif option == "ID Number":
    id_val = st.number_input("Enter ID", min_value=1)
    results = df[df['id'] == id_val].copy()

elif option == "Beat Number":
    beat_val = st.sidebar.number_input("Enter Beat Number", min_value=1)
    results = df[df['BeatNo'] == beat_val].copy()

elif option == "Suburb":
    suburb_list = sorted(df['Suburb'].unique())
    sub_val = st.selectbox("Select Suburb", suburb_list, index=None, placeholder="Choose a suburb")
    results = df[df['Suburb'] == sub_val].copy()

# Display Results
if not results.empty:
    # Add Map Link Column
    results['Map Link'] = results.apply(lambda row: make_map_link(row, searched_no), axis=1)
   
    st.success(f"Found {len(results)} record(s)")
   
    # Configure the table
    st.dataframe(
        results,
        column_config={
            "Map Link": st.column_config.LinkColumn("Maps", display_text="📍 View"),
            "id": "ID",
            "StreetNoMin": "Min No",
            "StreetNoMax": "Max No",
            "BeatNo": "Beat",
            "TeamNo": "Team"
        },
        use_container_width=True,
        hide_index=True
    )
   
    # Download Button
    csv = results.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export to CSV", data=csv, file_name='sortcart_results.csv', mime='text/csv')

elif (option == "Street Address" and st_name):
    st.warning(f"No entry found for {st_no} {st_name}. Check if the number is Even/Odd correctly.")
 

 


