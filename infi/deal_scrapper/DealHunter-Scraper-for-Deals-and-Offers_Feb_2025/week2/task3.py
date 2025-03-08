import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from io import BytesIO
from urllib.parse import urljoin
import time

#task 3

# Set page config
st.set_page_config(
    page_title="Web Scraper Pro",
    layout="wide",
    page_icon="🌐",
    menu_items={'About': "### Professional Web Scraping Suite"}
)

#  CSS STYLING

st.markdown("""
<style>
    .main { background: #f8f9fa; padding: 2rem; }
    [data-testid="stSidebar"] { background: linear-gradient(145deg, #2c3e50, #3498db); padding: 1.5rem; }
    h1 { color: #2c3e50; font-family: 'Poppins', sans-serif; border-bottom: 3px solid #4CAF50; }
    .stButton > button { background: linear-gradient(45deg, #4CAF50, #45a049); color: white; border-radius: 8px; padding: 0.75rem 2rem; }
    .stButton > button:hover { transform: translateY(-2px); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
</style>
""", unsafe_allow_html=True)

st.markdown("""<link href='https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap' rel='stylesheet'>""", unsafe_allow_html=True)


def scrape_libraries(state_url):
    try:
        response = requests.get(state_url)
        if response.status_code != 200:
            return pd.DataFrame()

        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table")
        if not table:
            return pd.DataFrame()

        rows = table.find_all("tr")
        data = [[col.get_text(strip=True) for col in row.find_all("td")] for row in rows if row.find_all("td")]
        columns = ["City", "Library", "Address", "Zip", "Phone"][:max(len(row) for row in data) if data else 5]
        return pd.DataFrame(data, columns=columns)
    except:
        return pd.DataFrame()


def public_libraries_app():
    st.title("📚 Public Libraries Data Explorer")
    states = {
        "Alabama": "https://publiclibraries.com/state/alabama/",
        "Alaska": "https://publiclibraries.com/state/alaska/",
        "California": "https://publiclibraries.com/state/california/",
    }
    selected_state = st.selectbox("Select a state", list(states.keys()))
    if st.button("🚀 Fetch Library Data"):
        with st.spinner("🔍 Scanning library databases..."):
            df = scrape_libraries(states[selected_state])
        if not df.empty:
            st.success(f"✅ Found {len(df)} libraries in {selected_state}!")
            st.dataframe(df)
            st.download_button("Download CSV", df.to_csv(index=False), file_name=f"{selected_state}_libraries.csv", mime="text/csv")
        else:
            st.error("No data found for this state.")

# DEALSHEAVEN SCRAPER

def get_stores():
    try:
        url = "https://dealsheaven.in/stores"
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        return [{"name": a.text.strip(), "url": urljoin(url, a.get("href", "").strip())} for a in soup.select("ul.store-listings li a") if a.text.strip()]
    except:
        return []

def scrape_deals(store_info, max_pages, search_query=None):
    products = []
    for page in range(1, max_pages + 1):
        try:
            time.sleep(1.5) if page > 1 else None
            response = requests.get(f"{store_info['url']}?page={page}&keyword={search_query}" if search_query else store_info['url'])
            soup = BeautifulSoup(response.content, 'html.parser')
            for card in soup.find_all('div', class_='product-item-detail'):
                products.append({
                    'Product Name': card.find('h3').text.strip() if card.find('h3') else 'N/A',
                    'Image URL': card.find('img', class_='lazy')['data-src'] if card.find('img', class_='lazy') else 'N/A',
                    'Discount': card.find('div', class_='discount').text.strip() if card.find('div', class_='discount') else 'N/A',
                    'Price': card.find('p', class_='spacail-price').text.strip() if card.find('p', class_='spacail-price') else 'N/A',
                    'Shop Now Link': urljoin(store_info['url'], card.find('a', class_='btn')['href']) if card.find('a', class_='btn') else 'N/A'
                })
        except:
            continue
    return products

def dealsheaven_app():
    st.title("🛍️ DealSphere Pro - Shopping Assistant")
    stores = get_stores()
    if not stores:
        st.error("Failed to load stores. Please try again later.")
        return
    selected_store = st.selectbox("Select Store", stores, format_func=lambda x: x['name'])
    search_query = st.text_input("🔍 Search products (optional)")
    if st.button("🚀 Start Scraping"):
        with st.spinner(f"🕵️ Scanning {selected_store['name']}..."):
            deals = scrape_deals(selected_store, 3, search_query)
        if deals:
            df = pd.DataFrame(deals)
            st.success(f"🎉 Found {len(deals)} deals!")
            st.dataframe(df)
            st.download_button("📥 CSV", df.to_csv(index=False), file_name=f"{selected_store['name']}_deals.csv", mime="text/csv")
        else:
            st.warning("⚠️ No deals found.")


# MAIN APPLICATION


def main():
    st.sidebar.title("Navigation")
    scraper_choice = st.sidebar.selectbox("Select Scraper", ["Public Libraries", "DealsHeaven Scraper"])
    public_libraries_app() if scraper_choice == "Public Libraries" else dealsheaven_app()

if __name__ == "__main__":
    main()
