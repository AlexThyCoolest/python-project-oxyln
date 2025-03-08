import sqlite3

class News:
    def __init__(self, id, title, url, image_url, content, category, published_at, created_at):
        self.id = id
        self.title = title
        self.url = url
        self.image_url = image_url
        self.content = content
        self.category = category
        self.published_at = published_at
        self.created_at = created_at
    
    @classmethod
    def from_row(cls, row):
        return cls(
            id=row['id'],
            title=row['title'],
            url=row['url'],
            image_url=row['image_url'],
            content=row['content'],
            category=row['category'],
            published_at=row['published_at'],
            created_at=row['created_at']
        )
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'image_url': self.image_url,
            'content': self.content,
            'category': self.category,
            'published_at': self.published_at,
            'created_at': self.created_at
        }


def init_db(app):
    connection_string = app.config['DB_CONNECTION_STRING']
    connection = sqlite3.connect(connection_string)
    cursor = connection.cursor()
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


def get_db_connection(app):
    connection_string = app.config['DB_CONNECTION_STRING']
    connection = sqlite3.connect(connection_string)
    connection.row_factory = sqlite3.Row
    return connection