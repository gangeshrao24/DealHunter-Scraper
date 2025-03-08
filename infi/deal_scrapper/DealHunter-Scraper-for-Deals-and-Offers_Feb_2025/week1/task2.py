import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from io import BytesIO
from urllib.parse import urljoin
import time

#task 2
st.set_page_config(page_title="DealsSphere Pro", layout="wide", page_icon="🛍️")

@st.cache_data(ttl=3600)
def get_all_stores():
    url = "https://dealsheaven.in/stores"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        stores = [{"name": a.text.strip(), "url": urljoin(url, a.get("href", "").strip())} for a in soup.select("ul.store-listings li a") if a.text.strip()]
        return stores
    except Exception as e:
        st.error(f"Error fetching stores: {e}")
        return []

def get_page_count(store_url, search_query=None):
    try:
        url = f"{store_url}?keyword={search_query}" if search_query else store_url
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        pages = [int(a.text) for a in soup.select('ul.pagination a') if a.text.isdigit()]
        return max(pages) if pages else 1
    except Exception:
        return 1

def scrape_deals(store_info, max_pages, search_query=None):
    products = []
    store_url = store_info['url']
    store_name = store_info['name']
    
    for page in range(1, max_pages + 1):
        try:
            if page > 1:
                time.sleep(1.2)
            
            url = f"{store_url}?page={page}" + (f"&keyword={search_query}" if search_query else "")
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            for card in soup.select('div.product-item-detail'):
                if card.find('div', class_='ad-div'):
                    continue
                
                products.append({
                    'Product Name': card.find('h3').text.strip() if card.find('h3') else 'N/A',
                    'Image URL': urljoin(store_url, card.find('img', class_='lazy')['data-src']) if card.find('img', class_='lazy') else 'N/A',
                    'Discount': card.find('div', class_='discount').text.strip() if card.find('div', class_='discount') else 'N/A',
                    'Original Price': card.find('p', class_='price').text.strip() if card.find('p', class_='price') else 'N/A',
                    'Current Price': card.find('p', class_='spacail-price').text.strip() if card.find('p', class_='spacail-price') else 'N/A',
                    'Store Name': store_name,
                    'Shop Now Link': urljoin(store_url, card.find('a', class_='btn')['href']) if card.find('a', class_='btn') else 'N/A'
                })
        except Exception as e:
            st.error(f"Error scraping page {page}: {str(e)}")
            continue
    
    return products

def main():
    st.title("🛍️ DealSphere Pro - Unified Shopping Platform")
    
    stores = get_all_stores()
    if not stores:
        st.error("Failed to load stores. Please try again later.")
        return
    
    selected_store = st.selectbox("Select Store", options=stores, format_func=lambda x: x['name'])
    search_query = st.text_input("🔍 Search products (optional)")
    
    page_count = get_page_count(selected_store['url'], search_query)
    max_pages = st.selectbox("Pages to scrape", options=list(range(1, page_count + 1)), index=0)
    
    if st.button("🚀 Start Scraping"):
        with st.spinner(f"Scraping {selected_store['name']}..."):
            deals = scrape_deals(selected_store, max_pages, search_query)
        
        if deals:
            st.success(f"Found {len(deals)} deals!")
            df = pd.DataFrame(deals)
            st.dataframe(df, use_container_width=True)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.download_button("📥 CSV", data=df.to_csv(index=False).encode('utf-8'), file_name=f"{selected_store['name']}_deals.csv", mime="text/csv")
            with col2:
                excel_data = BytesIO()
                df.to_excel(excel_data, index=False)
                st.download_button("📊 Excel", data=excel_data, file_name=f"{selected_store['name']}_deals.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            with col3:
                st.download_button("📄 JSON", data=json.dumps(deals, indent=2), file_name=f"{selected_store['name']}_deals.json", mime="application/json")
        else:
            st.warning("No deals found in scanned pages. Try different parameters!")

if __name__ == "__main__":
    main()
