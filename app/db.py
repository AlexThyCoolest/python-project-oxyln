import sqlite3
from app.models import News 
from app.utils import fetch_news_content

def init_db(app):
    connection_string = app.config['DB_CONNECTION_STRING']
    connection = sqlite3.connect(connection_string)
    cursor = connection.cursor()

    cursor.execute("DROP TABLE IF EXISTS news")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            url TEXT,
            image_url TEXT,
            content TEXT,
            category TEXT,
            published_at DATETIME,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    connection.commit()
    connection.close()


def get_db_connection(app=None):
    if app:
        connection_string = app.config['DB_CONNECTION_STRING']
    else:
        from flask import current_app
        connection_string = current_app.config['DB_CONNECTION_STRING']

    connection = sqlite3.connect(connection_string)
    connection.row_factory = sqlite3.Row
    return connection

def get_news(category: str | None = None, search_term: str | None = None) -> list[News]:
    connection = get_db_connection()
    cursor = connection.cursor()
    
    query = "SELECT * FROM news"
    params = []
    
    if category:
        query += ' WHERE category = ?'
        params.append(category)
    
    if search_term:
        query += ' AND' if category else ' WHERE'
        query += ' (title LIKE ? OR content LIKE ?)'
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    try:
        cursor.execute(query, params)
        news = [News.from_row(row) for row in cursor.fetchall()]
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
        news = []
    finally:
        connection.close()
    
    return news
    
def add_news(news: News, app=None) -> News | None:
    
    connection = get_db_connection(app)
    cursor = connection.cursor()
    cursor.execute('''
        INSERT INTO news (title, url, image_url, content, category, published_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        news.title,
        news.url,
        news.image_url,
        news.content,
        news.category,
        news.published_at
    ))
    inserted_id = cursor.lastrowid
    connection.commit()
    connection.close()
    
    news.id = inserted_id
    return news

def get_news_by_id(news_id: int):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM news WHERE id = ?', (news_id,))
    row = cursor.fetchone()
    connection.close()
    return News.from_row(row) if row else None

def remove_news(news_id: int, app=None):
    connection = get_db_connection(app)
    cursor = connection.cursor()
    cursor.execute('DELETE FROM news WHERE id = ?', (news_id,))
    connection.commit()
    connection.close()


def update_news(news: News, app=None):
    connection = get_db_connection(app)
    cursor = connection.cursor()
    cursor.execute('''
        UPDATE news
        SET 
            title = ?,
            url = ?,
            image_url = ?,
            content = ?,
            category = ?,
            published_at = ?
        WHERE id = ?
    ''', (
        news.title,
        news.url,
        news.image_url,
        news.content,
        news.category,
        news.published_at,
        news.id
    ))
    connection.commit()
    connection.close()
    return news