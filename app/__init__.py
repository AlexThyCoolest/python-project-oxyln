from flask import Flask
from app.db import init_db, add_news
from dotenv import load_dotenv
from app.utils import fetch_news
from app.routes import api_blueprint

def create_app():
    app = Flask(__name__)
    load_dotenv()
    app.config.from_object('app.config.Config')
    init_db(app)

    app.register_blueprint(api_blueprint)
    news = fetch_news(app.config['NEWSAPI_API_KEY'])
    for news_item in news:
        add_news(news_item, app=app)

    return app
