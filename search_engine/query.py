import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://duckduckgo.com/"
}

def normalize_url(url):
    """Ensure the URL has a scheme. If it's protocol-relative, prepend 'https:'."""
    if url.startswith("//"):
        return "https:" + url
    return url

def extract_actual_url(url):
    """
    If the URL is a DuckDuckGo redirection (contains 'uddg' parameter),
    extract and return the actual target URL.
    """
    parsed = urlparse(url)
    qs = parse_qs(parsed.query)
    if "uddg" in qs:
        actual_url = unquote(qs["uddg"][0])
        return actual_url
    return url

def search_web(query: str, num_results: int = 5):
    """
    Query a search engine and return the top results.
    Returns a list of dicts: {"title": ..., "url": ...}.
    """
    base_url = "https://html.duckduckgo.com/html/"

    params = {
        'q': query,
        'kl': 'wt-wt'
    }

    try:
        resp = requests.get(base_url, headers=HEADERS, params=params, timeout=10)
    except Exception as e:
        print(f"Connection error: {e}")
        return []

    if resp.status_code != 200:
        print(f"Search request failed with status code {resp.status_code}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    result_links = []

    # Extract links from <a class="result__a"> tags.
    found_links = soup.find_all('a', class_='result__a')

    if not found_links:
        print("No results found parsing HTML (structure might have changed).")

    for a in found_links[:num_results]:
        link = a.get('href')
        title = a.get_text(strip=True)

        if link:
            normalized = normalize_url(link)
            actual = extract_actual_url(normalized)

            result_links.append({
                "title": title,
                "url": actual
            })

    return result_links
