from sqlalchemy import (
    Column,
    String,
    Integer,
    ForeignKey,
    DateTime,
    Boolean
)
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def db_setup(app, database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


def db_rollback():
    db.session.rollback()
    db.session.close()


def db_exists(query):
    return db.session.query(query.exists()).scalar()


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
    datetime = Column(DateTime)
    user = Column(String, ForeignKey('users.id'))
    content = Column(String)
    article = Column(String, ForeignKey('articles.id'))
    parent = Column(Integer, ForeignKey('comments.id'))
    removed = Column(Boolean)

    def delete(self):
        if db_exists(Comment.query.filter_by(parent=self.id)):
            self.removed = True
            self.content = None
            self.user = None
            self.update()
        else:
            super().delete()
            if self.parent is not None:
                parent_comment = (
                    Comment.query.filter_by(id=self.parent)
                    .one_or_none()
                )
                if (parent_comment.removed and
                    not db_exists(
                        Comment.query
                        .filter_by(parent=parent_comment.id))):
                    parent_comment.delete()

    def format(self):
        if self.removed:
            return {
                'id': self.id,
                'removed': True,
                'datetime': self.datetime,
                'article': self.article,
                'parent': self.parent
            }
        return {
            'id': self.id,
            'removed': False,
            'user': self.user,
            'datetime': self.datetime,
            'content': self.content,
            'article': self.article,
            'parent': self.parent
        }

    def recursive_format(self):
        ret = self.format()
        replies = (
            Comment.query.filter_by(parent=self.id)
            .order_by(Comment.datetime).all()
        )
        if replies != []:
            ret['replies'] = [r.recursive_format() for r in replies]
        return ret


class User(db.Model, DBInterface):
    __tablename__ = 'users'

    id = Column(String, primary_key=True)
    nickname = Column(String)
    picture = Column(String)

    def format(self):
        return {
            'id': self.id,
            'nickname': self.nickname,
            'picture': self.picture
        }
