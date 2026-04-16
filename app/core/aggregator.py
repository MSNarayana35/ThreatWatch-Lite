import logging
import requests
from bs4 import BeautifulSoup

_logger = logging.getLogger(__name__)

def fetch_thehackernews_articles():
    """
    Fetches the latest articles from The Hacker News.
    """
    url = "https://thehackernews.com/"
    articles = []
    try:
        response = requests.get(
            url,
            timeout=10,
            headers={
                "User-Agent": "ThreatWatchLite/1.0 (+https://localhost)",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.text, 'html.parser')
        
        items = soup.find_all('div', class_='body-post')
        if not items:
            items = soup.select('div.body-post, div.body-post.clear')

        for item in items:
            title_element = item.find('h2', class_='home-title') or item.find('h2')
            description_element = item.find('div', class_='home-desc') or item.find('div', class_='home-desc')
            link_element = item.find('a', class_='story-link') or item.find('a', href=True)

            if title_element and description_element and link_element and link_element.get('href'):
                title = title_element.text.strip()
                description = description_element.text.strip()
                source = link_element['href']
                if title and description and source:
                    articles.append({
                        'title': title,
                        'description': description,
                        'source': source
                    })
        return articles

    except requests.exceptions.RequestException as e:
        _logger.warning("Error fetching data from The Hacker News: %s", e)
        return []
