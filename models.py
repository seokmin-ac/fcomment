import sys
from sqlalchemy import Column, String, Integer, ForeignKey
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def setup_db(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def db_rollback():
    db.session.rollback()
    print(sys.exc_info())
    db.session.close()


class DBInterface:
    def insert(self):
        db.session.add(self)
        db.session.commit()


    def delete(self):
        db.session.delete(self)
        db.session.commit()


    def update(self):
        db.session.commit()


class Article(db.Model, DBInterface):
    __tablename__ = 'articles'

    id = Column(String, primary_key=True)

    def format(self):
        return {
            'id': self.id
        }


class Comment(db.Model, DBInterface):
    __tablename__ = 'comments'

    id = Column(Integer, primary_key=True)
    user = Column(String)
    content = Column(String)
    article = Column(String, ForeignKey('articles.id'))
    parent = Column(Integer, ForeignKey('comments.id'))

    def format(self):
        return {
            'id': self.id,
            'user': self.user,
            'content': self.content,
            'article': self.article,
            'parent': self.parent
        }
