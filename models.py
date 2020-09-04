from sqlalchemy import Column, String, Integer, ForeignKey
from flask_sqlalchemy import SQLAlchemy
import uuid

db = SQLAlchemy()

def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

class Article(db.Model):
    __tablename__ = 'articles'

    id = Column(String, primary_key=True)

class Comment(db.Model):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    text = Column(String)
    article = Column(String, ForeignKey('articles.id'))
    parent = Column(Integer, ForeignKey('comments.id'))
