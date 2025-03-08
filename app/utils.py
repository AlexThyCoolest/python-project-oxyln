import requests
from datetime import datetime
from bs4 import BeautifulSoup
from app.models import News

def convert_to_datetime(date_str: str):
    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))

def fetch_news(api_key: str):
    url = 'https://newsapi.org/v2/top-headlines'
    allowed_sources = [
        'abc-news',
        'nbc-sports',
        'nbc-news',
        'npr',
        'cnn',
        'politico',
        'bbc-news',
        'al-jazeera-english'
    ]

    params = {
        'apiKey': api_key,
        'sources': ','.join(allowed_sources)
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        return []

    news_data = []
    articles = response.json().get('articles', [])
    for article in articles:
        if '[Removed]' in article.get('title'):
            continue
        published_at = article.get('publishedAt')
        if published_at:
            published_at = convert_to_datetime(published_at)
        news_data.append(
            News(
                id=article.get('id'),
                title=article.get('title'),
                url=article.get('url'),
                image_url=article.get('urlToImage'),
                content=article.get('content'),
                category=article.get('category'),
                published_at=published_at,
                created_at=datetime.now()
            )
        )
    return news_data


def fetch_news_content(news: News, app=None):
    from app.db import remove_news
    try:
        response = requests.get(news.url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Failed to fetch content for {news.url}: {e}")
        news_id = getattr(news, 'id', None)
        if news_id is not None:
            remove_news(news_id, app)
        else:
            print("News object does not have an id attribute, cannot remove news.")
        return None

    soup = BeautifulSoup(response.text, 'html.parser')
    content_text = None

    if 'abcnews.go.com' in news.url:
        content_els = soup.select('.Article__Content')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    elif 'nbcsports.com' in news.url:
        content_els = soup.select('.ArticlePage-articleBody')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    elif 'nbcnews.com' in news.url:
        content_els = soup.select('.article-body__content')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    elif 'npr.org' in news.url:
        content_els = soup.select('.storytext')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    elif 'cnn.com' in news.url:
        content_els = soup.select('.article__content')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    elif 'politico.com' in news.url:
        content_els = soup.select('.story-text')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    elif 'bbc.com' in news.url:
        content_els = soup.select('[data-component="text-block"]')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    elif 'phys.org' in news.url:
        content_els = soup.select('.article-body')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    elif 'aljazeera.com' in news.url:
        content_els = soup.select('.wysiwyg')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    elif 'marketwatch.com' in news.url:
        content_els = soup.select('.article__body')
        if content_els:
            content_text_list = [el.get_text().strip() for el in content_els]
            content_text = '\n\n'.join(content_text_list)
    else:
        content_text = None

    if content_text and len(content_text) >= 50:
        news.content = content_text
        return news
    else:
        print(f"Scraped content is insufficient for {news.url}")
        news_id = getattr(news, 'id', None)
        if news_id:
            remove_news(news_id, app)
        return None

async def fetch_news_content_with_crawl4ai(url):
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

    css_selector = ".article-content"
    browser_config = BrowserConfig()
    if 'abcnews.go.com' in url:
        css_selector=".Article__Content"
    elif 'nbcsports.com' in url:
        css_selector=".ArticlePage-articleBody"
    elif 'nbcnews.com' in url:
        css_selector=".article-body__content"
    elif 'npr.org' in url:
        css_selector=".storytext"
    elif 'cnn.com' in url:
        css_selector=".article__content"
    elif 'politico.com' in url:
        css_selector=".story-text"
    elif 'bbc.com' in url:
        css_selector="[data-component='text-block']"
    elif 'phys.org' in url:
        css_selector=".article-body"
    elif 'aljazeera.com' in url:
        css_selector=".wysiwyg"
    elif 'marketwatch.com' in url:
        css_selector=".article__body"

    run_config = CrawlerRunConfig(css_selector=css_selector)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url, config=run_config)
        if result.success:
            return result.markdown
        return None
