from flask import Blueprint, request, jsonify
from app.db import get_news, get_news_by_id, add_news, update_news, remove_news
from app.utils import fetch_news_content, fetch_news_content_with_crawl4ai
from app.models import News

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/news', methods=['GET'])
def get_news_route():
    category = request.args.get('category')
    search = request.args.get('q')
    news_list = get_news(category=category, search_term=search)
    news_dicts = [news.to_dict() for news in news_list]
    return jsonify({'news': news_dicts})

@api_blueprint.route('/news/<int:news_id>', methods=['GET'])
async def get_news_by_id_route(news_id):
    news = get_news_by_id(news_id)
    if not news:
        return jsonify({'error': 'News not found'}), 404
    if not ' chars]' in news.content:
        return jsonify(news.to_dict())
    content = await fetch_news_content_with_crawl4ai(news.url)
    print("DEBUG type of content:", type(content))
    if content:
        news.content = content
        update_news(news)
        return jsonify(news.to_dict())
    else:
        if news_id:
            remove_news(news.id)
        else:
            print("News object does exist in db, cannot remove news.")
        return jsonify({'error': 'Could not fetch news'})