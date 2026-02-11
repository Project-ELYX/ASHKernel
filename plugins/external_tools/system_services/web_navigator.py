import requests
from bs4 import BeautifulSoup

def setup(kernel):
    print("[SYSTEM] Web Navigator Module Online. The internet is now an open book.")

    def search_the_web(query: str):
        """
        Performs a general internet search to find information, documentation, 
        or verify facts. Returns the top relevant results.
        """
        print(f"[NAVIGATOR] Searching: {query}")
        
        # Using the DuckDuckGo HTML endpoint for a 'clean' scrape without API keys
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        url = f"https://html.duckduckgo.com/html/?q={query}"
        
        try:
            response = requests.get(url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            results = []
            for result in soup.find_all('div', class_='result__body')[:5]: # Grab top 5
                title = result.find('a', class_='result__a').text
                link = result.find('a', class_='result__a')['href']
                snippet = result.find('a', class_='result__snippet').text
                results.append(f"Title: {title}\nLink: {link}\nSnippet: {snippet}\n")
            
            if not results:
                return "No results found. Maybe I'm being rate-limited or the query was too obscure."
                
            return "\n---\n".join(results)
        except Exception as e:
            return f"NAVIGATION ERROR: {str(e)}"

    if kernel.brain:
        kernel.brain.register_tool(search_the_web)