# import streamlit as st
# import requests
# from bs4 import BeautifulSoup
# import pandas as pd
# from streamlit_tags import st_tags  # Import for tag-based input

# # Streamlit UI Setup
# st.set_page_config(page_title="Universal Web Scraper", layout="wide")

# # Sidebar: Web Scraper Settings
# st.sidebar.title("🕷️ Web Scraper Settings")
# model = st.sidebar.selectbox("Select Model", ["gemini-2.0-flash", "gemini-pro"])
# url = st.sidebar.text_input("Enter URL", placeholder="https://example.com")

# # Tag-Based Input for Fields
# fields = st_tags(
#     label="Enter Fields to Extract:",
#     text="Press Enter to add a tag",
#     value=["name", "image url", "price"],  # Default fields
#     suggestions=["title", "rating", "availability"],
#     maxtags=10,
#     key="1"
# )

# # Scrape Button
# scrape_button = st.sidebar.button("🔍 Scrape")

# # Main Content
# st.title("Universal Web Scraper 🦑")

# if scrape_button:
#     if not url.strip():
#         st.error("❌ Please enter a valid URL.")
#     elif not fields:
#         st.error("⚠️ Please enter at least one field to extract.")
#     else:
#         try:
#             # Fetch HTML content
#             response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
#             response.raise_for_status()  # Raise an error for failed requests
#             soup = BeautifulSoup(response.text, "html.parser")

#             # Scraping Logic
#             data = []
#             items = soup.find_all("div", class_="product")  # Adjust this based on your website structure

#             for item in items:
#                 extracted_data = {field: item.get_text(strip=True) for field in fields if field != "image url"}
#                 images = item.find_all("img")
#                 if "image url" in fields and images:
#                     extracted_data["image url"] = images[0]["src"]
#                 data.append(extracted_data)

#             # Convert to DataFrame
#             df = pd.DataFrame(data)

#             # Display Data
#             st.write("### Scraped Data:")
#             if df.empty:
#                 st.warning("No data found! Try adjusting field names or selectors.")
#             else:
#                 st.dataframe(df)

#                 # Download Buttons
#                 csv = df.to_csv(index=False).encode("utf-8")
#                 st.download_button("📥 Download CSV", csv, "scraped_data.csv", "text/csv")

#                 json_data = df.to_json(orient="records")
#                 st.download_button("📥 Download JSON", json_data, "scraped_data.json", "application/json")

#         except requests.exceptions.RequestException as e:
#             st.error(f"⚠️ Failed to fetch data: {e}")





# import streamlit as st
# from playwright.sync_api import sync_playwright
# from bs4 import BeautifulSoup
# import html2text
# import pandas as pd
# import os
# from streamlit_tags import st_tags  # Import for tag-based input

# # Streamlit UI Setup
# st.set_page_config(page_title="Universal Web Scraper", layout="wide")

# # Sidebar: Web Scraper Settings
# st.sidebar.title("🕷️ Web Scraper Settings")
# model = st.sidebar.selectbox("Select Model", ["gemini-2.0-flash", "gemini-pro"])
# url = st.sidebar.text_input("Enter URL", placeholder="https://example.com")

# # Tag-Based Input for Fields
# fields = st_tags(
#     label="Enter Fields to Extract:",
#     text="Press Enter to add a tag",
#     value=["name", "image url", "price"],  # Default fields
#     suggestions=["title", "rating", "availability"],
#     maxtags=10,
#     key="1"
# )

# # Scrape Button
# scrape_button = st.sidebar.button("🔍 Scrape")

# # Function to scrape HTML using Playwright
# def scrape_html(url):
#     """Fetch HTML content using Playwright"""
#     with sync_playwright() as p:
#         browser = p.chromium.launch(headless=True)
#         page = browser.new_page()
#         page.goto(url, timeout=60000)
#         html_content = page.content()
#         browser.close()
#     return html_content

# # Function to clean HTML using BeautifulSoup
# def clean_html(html_content):
#     """Remove headers, footers, and unnecessary elements"""
#     soup = BeautifulSoup(html_content, "html.parser")

#     # Remove unwanted elements (modify as needed)
#     for tag in soup(["header", "footer", "script", "style", "nav", "aside"]):
#         tag.decompose()

#     return str(soup)

# # Function to convert HTML to Markdown
# def convert_html_to_markdown(clean_html_content):
#     """Convert cleaned HTML to Markdown format"""
#     converter = html2text.HTML2Text()
#     converter.ignore_links = False  # Keep links in markdown
#     return converter.handle(clean_html_content)

# # Function to save Markdown content
# def save_markdown(content, url):
#     """Save Markdown content to a file"""
#     folder_name = "scraped_markdown"
#     os.makedirs(folder_name, exist_ok=True)  # Create folder if not exists

#     file_name = url.replace("https://", "").replace("/", "_") + ".md"
#     file_path = os.path.join(folder_name, file_name)

#     with open(file_path, "w", encoding="utf-8") as f:
#         f.write(content)

#     return file_path

# # Main Content
# st.title("Universal Web Scraper 🦑")

# if scrape_button:
#     if not url.strip():
#         st.error("❌ Please enter a valid URL.")
#     elif not fields:
#         st.error("⚠️ Please enter at least one field to extract.")
#     else:
#         try:
#             with st.spinner("Scraping the website..."):
#                 # Scrape and clean HTML
#                 html_content = scrape_html(url)
#                 cleaned_html = clean_html(html_content)
#                 markdown_content = convert_html_to_markdown(cleaned_html)
#                 file_path = save_markdown(markdown_content, url)

#                 # Extract specified fields
#                 soup = BeautifulSoup(cleaned_html, "html.parser")
#                 data = []
#                 items = soup.find_all("div")  # Adjust based on actual structure

#                 for item in items:
#                     extracted_data = {field: item.get_text(strip=True) for field in fields if field != "image url"}
#                     images = item.find_all("img")
#                     if "image url" in fields and images:
#                         extracted_data["image url"] = images[0]["src"]
#                     data.append(extracted_data)

#                 # Convert to DataFrame
#                 df = pd.DataFrame(data)

#                 st.success(f"Scraping completed! Markdown file saved at: {file_path}")

#                 # Display Scraped Data
#                 st.write("### Scraped Data:")
#                 if df.empty:
#                     st.warning("No data found! Try adjusting field names or selectors.")
#                 else:
#                     st.dataframe(df)

#                     # Download Buttons
#                     csv = df.to_csv(index=False).encode("utf-8")
#                     st.download_button("📥 Download CSV", csv, "scraped_data.csv", "text/csv")

#                     json_data = df.to_json(orient="records")
#                     st.download_button("📥 Download JSON", json_data, "scraped_data.json", "application/json")

#                     st.download_button(label="📥 Download Markdown", data=markdown_content, file_name=file_path.split("/")[-1], mime="text/markdown")

#         except Exception as e:
#             st.error(f"⚠️ Error during scraping: {e}")



import streamlit as st
from streamlit_tags import st_tags
import re
import sys
import os
import json
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup
import html2text
import google.generativeai as genai
from typing import List, Type
from pydantic import BaseModel, create_model
import pandas as pd
import asyncio
from dotenv import load_dotenv
import asyncio

load_dotenv()

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

os.makedirs("markdown_files", exist_ok=True)
os.makedirs("scraped_json_files", exist_ok=True)
def is_valid_url(url):
    pattern = re.compile(r"^(https?://)?(www\.)?[a-zA-Z0-9-]+(\.[a-zA-Z]{2,})+(/.*)?$")
    return re.match(pattern, url) is not None

def scrape_webpage(url):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            content = page.content()
            browser.close()
            return content
    except Exception as e:
        st.error(f"Error during scraping: {e}")
        return None

def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
    field_definitions = {field: (str, ...) for field in field_names}
    return create_model('DynamicListingModel', **field_definitions)

def create_listings_container_model(listing_model: Type[BaseModel]) -> Type[BaseModel]:
    return create_model('DynamicListingsContainer', listings=(List[listing_model], ...))

def clean_html(content):
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(["header", "footer", "script", "style", "meta"]):
        tag.decompose()
    return soup

def convert_html_to_markdown(html_content):
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = False
    return text_maker.handle(str(html_content))

def chunk_text(text, chunk_size=3000):
    words = text.split()
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks

def save_to_markdown(content):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"markdown_files/{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

def save_to_json(data):
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"scraped_json_files/{timestamp}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    return filename

def extract_json(text):
    try:
        # Find the first valid JSON-like structure
        json_start = text.find("{")
        json_end = text.rfind("}")
        if json_start != -1 and json_end != -1:
            json_str = text[json_start : json_end + 1]
            extracted = json.loads(json_str)
            if isinstance(extracted, dict):
                return extracted
    except json.JSONDecodeError as e:
        st.error(f"JSON Decode Error: {e}")
    except Exception as e:
        st.error(f"Unexpected error extracting JSON: {e}")
    return None

def call_gemini_api(model_name, chunks, DynamicListingsContainer):
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    combined_data = {}
    for i, chunk in enumerate(chunks):
        try:
            prompt = f"Extract structured data from this content:\n{chunk}"
            st.write(f"Processing chunk {i+1}/{len(chunks)}...")
            model = genai.GenerativeModel(model_name)
            response = model.generate_content(prompt,generation_config=genai.GenerationConfig(
            response_mime_type="application/json",response_schema=DynamicListingsContainer))
            if response and response.text:
                extracted_json = extract_json(response.text)
                if extracted_json:
                    combined_data.update(extracted_json)
        except Exception as e:
            st.error(f"Error calling Gemini API: {e}")
    return combined_data

def download_button(data, filename, file_format):
    if file_format == "json":
        file_data = json.dumps(data, indent=4).encode("utf-8")
    else:
        df = pd.DataFrame(data["listings"])
        file_data = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=f"Download {file_format.upper()} File",
        data=file_data,
        file_name=filename,
        mime=f"text/{file_format}"
    )

def main():
    st.set_page_config(layout="wide")
    ai_response = {}
    is_valid = False
    with st.sidebar:
        st.title("Web Scraper Settings")
        url = st.text_input(label="Enter URL", placeholder="https://example.com")
        if url and not is_valid_url(url):
            st.error("Please enter a valid URL!")
        model = st.selectbox("Choose a model", ("gemini-1.5-flash", "gemini-2.0-flash"))
        field_names = st_tags(label="Enter fields to validate", text="Press enter to add more") or []
        markdown_text = ""
        if st.button(label="Scrape & Analyze", type="secondary"):
            if not url:
                st.warning("Please enter a valid URL.")
            else:
                with st.spinner("Scraping webpage..."):
                    raw_html = scrape_webpage(url)
                    if raw_html:
                        soup = clean_html(raw_html)
                        markdown_text = convert_html_to_markdown(soup)
                        save_to_markdown(markdown_text)
                        text_chunks = chunk_text(markdown_text, chunk_size=5000)
                        DynamicListingModel = create_dynamic_listing_model(field_names)
                        DynamicListingsContainer = create_listings_container_model(DynamicListingModel)
                        ai_response = call_gemini_api(model, text_chunks, DynamicListingsContainer)
                        if ai_response:
                            is_valid = True
    st.title("Universal Web Scraper")
    if is_valid:
        if isinstance(ai_response, dict) and "listings" in ai_response:
            json_filename = save_to_json(ai_response)
            st.subheader("Extracted Data Table")
            df = pd.DataFrame(ai_response["listings"])
            st.dataframe(df)
            download_button(ai_response, "extracted_data.json", "json")
            download_button(ai_response, "extracted_data.csv", "csv")
        else:
            st.error("AI response did not return valid structured data.")

if __name__ == "__main__":
    main()