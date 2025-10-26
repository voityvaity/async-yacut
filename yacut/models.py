from datetime import datetime

from yacut import db
from yacut.constants import MAX_SHORT_ID_LENGTH


class URLMap(db.Model):
    """Модель для хранения коротких ссылок."""

    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String(256), nullable=False)
    short = db.Column(db.String(MAX_SHORT_ID_LENGTH),
                      unique=True, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Преобразует в словарь для API."""
        return {
            'id': self.id,
            'original': self.original,
            'short': self.short,
            'timestamp': (self.timestamp.isoformat()
                          if self.timestamp else None)
        }
