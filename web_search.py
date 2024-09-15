from dotenv import load_dotenv
from tavily import TavilyClient
import os
import requests
from bs4 import BeautifulSoup

MAX_TOKENS=16000

load_dotenv()
client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

def get_content(query):
    response = client.search(query)

    urls = [r['url'] for r in response['results']]
    content = ""

    for url in urls:
        resp = requests.get(url)

        # Check if the request was successful
        if resp.status_code == 200:
            # Parse the page content
            soup = BeautifulSoup(resp.content, 'html.parser')
            
            # Extract all text from the page
            text = soup.get_text()

            # Optionally, clean up the text
            cleaned_text = ' '.join(text.split())

            # Print or save the extracted text
            content += cleaned_text
        else:
            continue

    return content[:min(MAX_TOKENS, len(content))]


