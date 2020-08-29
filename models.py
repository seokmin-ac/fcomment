from sqlalchemy import Column, String, Integer, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

def setup_db(app, database_path):
    print(database_path)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

class Article(db.Model):
    __tablename__ = 'articles'

    id = Column(Integer, primary_key=True)
    url = Column(String)

class Comment(db.Model):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    article = Column(Integer, ForeignKey('articles.id'))