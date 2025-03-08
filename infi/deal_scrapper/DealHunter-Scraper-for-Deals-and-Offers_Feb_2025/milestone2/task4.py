import streamlit as st
from playwright.sync_api import sync_playwright
from datetime import datetime
from bs4 import BeautifulSoup
import html2text
import sys
from streamlit_tags import st_tags_sidebar
from typing import List, Type
from pydantic import BaseModel, create_model
import json
import google.generativeai as genai
import os
import pandas as pd
from dotenv import load_dotenv
import re
from langchain.text_splitter import RecursiveCharacterTextSplitter

if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Configure Google Generative AI
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Function to scrape a webpage
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

# Function to clean HTML
def clean_html(content):
    soup = BeautifulSoup(content, "html.parser")
    for tag in soup(["header", "footer", "script", "style", "meta"]):
        tag.decompose()
    return soup

def save_markdown(content):
    filename = f"scraped_content_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

# Function to convert HTML to Markdown
def convert_html_to_markdown(html_content):
    text_maker = html2text.HTML2Text()
    text_maker.ignore_links = False
    return text_maker.handle(str(html_content))

# Function to split text into chunks
def get_text_chunks(cleaned_content, chunk_size, chunk_overlap):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = text_splitter.split_text(cleaned_content)
    return chunks

# Function to create dynamic Pydantic model
def create_dynamic_listing_model(field_names: List[str]) -> Type[BaseModel]:
    return create_model("DynamicListingModel", **{field: (str, ...) for field in field_names})

# Function to query Gemini for each chunk and combine results
def query_gemini(model_name, chunks, dynamic_listing_model, system_message):
    model = genai.GenerativeModel(model_name)
    combined_responses = []

    # Create a placeholder for processing messages
    message_placeholder = st.empty()

    for idx, chunk in enumerate(chunks):
        message_placeholder.text(f"Processing chunk {idx + 1}/{len(chunks)}...")

        prompt = f"""
        {system_message}
        Model Schema:
        {json.dumps(dynamic_listing_model.model_json_schema(), indent=2)}
        Text:
        {chunk}
        """
        try:
            response = model.generate_content(prompt)
            cleaned_response = re.sub(r'```(?:json)?\n([\s\S]*?)\n```', r'\1', response.text).strip()
            combined_responses.append(json.loads(cleaned_response))
        except Exception as e:
            st.error(f"Error in Gemini query: {e}")

    # Clear the processing message after completion
    message_placeholder.empty()

    return combined_responses

# Streamlit UI
def main():
    st.header("Universal Web Scraper")
    st.sidebar.header("Web Scraper Settings")
    
    model = st.sidebar.selectbox("Select Model", ["gemini-2.0-flash"])
    url = st.sidebar.text_input("Enter URL:", placeholder="https://example.com")
    fields = st_tags_sidebar(label="Enter fields to extract", text="Press enter to add more fields")
    
    chunk_size = st.sidebar.slider("Chunk Size", 1000, 20000, 10000)
    chunk_overlap = st.sidebar.slider("Chunk Overlap", 100, 2000, 400)
    
    if st.sidebar.button("Scrape"):
        if not url:
            st.warning("Please enter a URL.")
            return
        
        with st.spinner("Scraping and processing..."):
            raw_html = scrape_webpage(url)
            if raw_html:
                soup = clean_html(raw_html)
                markdown_text = convert_html_to_markdown(soup)
                chunks = get_text_chunks(markdown_text, chunk_size, chunk_overlap)
                
                # Create a placeholder for markdown file message
                markdown_message = st.empty()
                markdown_filename = save_markdown(markdown_text)
                markdown_message.text(f"Markdown file saved: {markdown_filename}")
                
                DynamicListingModel = create_dynamic_listing_model(fields)
                SYSTEM_MESSAGE = """
                Extract structured data into a JSON list from the given text.
                If data is missing, return "N/A".
                """
                
                responses = query_gemini(model, chunks, DynamicListingModel, SYSTEM_MESSAGE)
                
                # Hide the markdown message after processing
                markdown_message.empty()
                
                if responses:
                    flat_responses = [item for sublist in responses for item in sublist]
                    df = pd.DataFrame(flat_responses)
                    df = df.loc[~(df.eq("N/A").all(axis=1))]  # Remove rows where all columns are "N/A"
                    
                    st.subheader("Extracted Data")
                    st.dataframe(df)
                    
                    json_filename = f"gemini_output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json"
                    st.download_button(
                        "Download JSON", json.dumps(flat_responses, indent=4).encode("utf-8"), json_filename, "application/json"
                    )
                    csv_filename = json_filename.replace(".json", ".csv")
                    st.download_button(
                        "Download CSV", df.to_csv(index=False).encode("utf-8"), csv_filename, "text/csv"
                    )
                    excel_filename = json_filename.replace(".json", ".xlsx")
                    df.to_excel(excel_filename, index=False)
                    st.download_button(
                        "Download Excel", open(excel_filename, "rb").read(), excel_filename, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                else:
                    st.warning("No valid data extracted.")
            else:
                st.error("Failed to scrape the webpage.")

if __name__ == "__main__":
    main()