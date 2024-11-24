class AuthConfig:
    SQLALCHEMY_DATABASE_URI='sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS=True
    REDIS_URL = "redis://localhost:6379/0"