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
    # Use specific number if provided, otherwise default to the range start
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
option = st.sidebar.selectbox("Search by:", ["Street Address", "Beat Number", "Suburb"])

results = pd.DataFrame()
searched_no = None

if option == "Street Address":
    col1, col2 = st.columns([3, 1])
    with col1:
        st_name = st.selectbox(
            "Start typing Street Name...",
            options=street_list,
            index=None,
            placeholder="e.g. ASHBY"
        )
    with col2:
        # Use a text input or allow 0/None to represent "no number"
        st_no_str = st.text_input("Number (optional)", value="")
        if st_no_str.isdigit():
            searched_no = int(st_no_str)
        else:
            searched_no = None
   
    if st_name:
        if searched_no is not None:
            # Filter by specific number and parity
            parity = 2 if searched_no % 2 == 0 else 1
            mask = (
                (df['StreetName'] == st_name) &
                (df['EvenOdd'] == parity) &
                (df['StreetNoMin'] <= searched_no) &
                (df['StreetNoMax'] >= searched_no)
            )
            results = df[mask].copy()
        else:
            # Show all records for that street name if no number is provided
            results = df[df['StreetName'] == st_name].copy()

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
    
    # Select only the columns requested: StreetName, Beat, Team, Postcode, Suburb, Maps, MaxNo, MinNo
    display_cols = ['StreetName', 'StreetNoMin', 'StreetNoMax', 'BeatNo', 'TeamNo', 'Postcode', 'Suburb', 'Map Link']
    display_results = results[display_cols]
   
    # Configure the table
    st.dataframe(
        display_results,
        column_config={
            "Map Link": st.column_config.LinkColumn("Maps", display_text="📍 View"),
            "BeatNo": "Round",
            "TeamNo": "Team",
            "StreetNoMin": "From",
            "StreetNoMax": "To"
        },
        use_container_width=True,
        hide_index=True
    )
   
    # Download Button
    csv = display_results.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Export to CSV", data=csv, file_name='search_results.csv', mime='text/csv')

elif (option == "Street Address" and st_name):
    msg = f"No entry found for {searched_no} {st_name}" if searched_no else f"No records found for {st_name}"
    st.warning(msg)
 

 








