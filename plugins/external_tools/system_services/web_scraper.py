import trafilatura
import requests
from bs4 import BeautifulSoup

def setup(kernel):
    print("[NAVIGATOR] Deep Scrape protocols initialized.")

    def deep_scrape_url(url: str):
        """
        Ingests a URL and extracts the core text content, removing ads and navigation.
        Use this after finding a relevant link via web search.
        """
        print(f"[NAVIGATOR] Commencing deep extraction: {url}")
        
        try:
            # Step 1: Attempt high-fidelity extraction with Trafilatura
            downloaded = trafilatura.fetch_url(url)
            result = trafilatura.extract(downloaded, include_formatting=True, include_links=True)
            
            if result:
                # Truncate to avoid blowing out context window (approx 3000 words)
                return f"SOURCE: {url}\n\nCONTENT:\n{result[:15000]}"
            
            # Step 2: Fallback to BeautifulSoup if Trafilatura misses
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            # Extract text from paragraphs only for a cleaner fallback
            paragraphs = [p.get_text() for p in soup.find_all('p')]
            fallback_text = "\n".join(paragraphs)
            
            if len(fallback_text) > 100:
                return f"FALLBACK EXTRACTION: {url}\n\n{fallback_text[:10000]}"
            
            return "ERROR: Page content was inaccessible or empty."

        except Exception as e:
            return f"EXTRACTION FAILURE: {str(e)}"

    if kernel.brain:
        kernel.brain.register_tool(deep_scrape_url)