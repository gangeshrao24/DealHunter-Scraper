import streamlit as st
import pandas as pd
import requests


from bs4 import BeautifulSoup
from io import BytesIO

def get_states():
    url = "https://publiclibraries.com/state/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        st.error("Failed to fetch states. Please try again later.")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")

    states = {}
    for link in soup.select("div.entry-content a"):
        state_name = link.text.strip()
        state_url = link["href"]
        if "state" in state_url:
            states[state_name] = state_url

    return states

def get_libraries(state_url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(state_url, headers=headers)

    if response.status_code != 200:
        st.error("Failed to fetch library data. Please try again later.")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")

    print(response.text[:1000])

    table = soup.find("table") 
    if not table:
        st.error("No library data found on the page.")
        return pd.DataFrame()

    data = []
    rows = table.find_all("tr")
    for row in rows[1:]:  
        cols = row.find_all("td")
        if len(cols) == 5:
            city = cols[0].text.strip()
            library = cols[1].text.strip()
            address = cols[2].text.strip()
            zip_code = cols[3].text.strip()
            phone = cols[4].text.strip()
            data.append([city, library, address, zip_code, phone])

    df = pd.DataFrame(data, columns=["City", "Library", "Address", "Zip", "Phone"])
    return df

st.set_page_config(page_title="Public Libraries Data", layout="wide")
st.title("📚 Public Libraries Data")

st.write("Select a state from the dropdown to view its public libraries information.")

states_dict = get_states()
state_names = list(states_dict.keys())

selected_state = st.selectbox("Select a state", state_names)

if selected_state:
    state_url = states_dict[selected_state]
    print(f"Selected State URL: {state_url}")  
    df = get_libraries(state_url)

    if not df.empty:
        st.dataframe(df, height=500)

        csv = df.to_csv(index=False).encode("utf-8")
        json = df.to_json(orient="records")
        excel_buffer = BytesIO()
        df.to_excel(excel_buffer, index=False, engine="openpyxl")
        excel_buffer.seek(0)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button("Download as CSV", data=csv, file_name=f"{selected_state}_libraries.csv", mime="text/csv")
        with col2:
            st.download_button("Download as JSON", data=json, file_name=f"{selected_state}_libraries.json", mime="application/json")
        with col3:
            st.download_button("Download as Excel", data=excel_buffer, file_name=f"{selected_state}_libraries.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        st.warning("No library data found for the selected state.")
