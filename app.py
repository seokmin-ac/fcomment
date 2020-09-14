import os
import sys
import datetime
from pytz import utc
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import NotFound, UnprocessableEntity

from models import (
    Article,
    Comment,
    User,
    db_setup,
    db_rollback
)
from auth import AuthError, requires_auth, check_permissions

COMMENTS_PER_PAGE = 20


def get_current_utc():
    return utc.localize(datetime.datetime.utcnow())


def raise_db_error(description=''):
    print(sys.exc_info())
    db_rollback()
    raise UnprocessableEntity(description=description)


app = Flask(__name__)
CORS(app, resources={r'*': {'origins': os.environ['PUBLIC_DOMAIN']}})
db_setup(app, os.environ['DATABASE_URL'])


@app.route('/')
def index():
    return jsonify({
        'success': True
    })


# Check is the token valid
@app.route('/auth', methods=['POST'])
@requires_auth()
def check_authority(payload):
    return jsonify({
        'success': True
    })


@app.route('/users')
def get_users():
    users = User.query.all()
    return jsonify({
        'success': True,
        'users': [u.format() for u in users]
    })


@app.route('/users', methods=['POST'])
@requires_auth()
def update_user(payload):
    if payload['sub'] != request.json['id']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Requestor is not a user to update.'
        }, 403)

    try:
        user = User.query.filter_by(id=request.json['id']).one_or_none()
        # Already exists
        if (user is not None):
            user.nickname = request.json['nickname']
            user.picture = request.json['picture']
            user.update()
            return jsonify({
                'success': True,
                'id': request.json['id']
            })

        user = User(
            id=request.json['id'],
            nickname=request.json['nickname'],
            picture=request.json['picture']
        )
        user.insert()

        return jsonify({
            'success': True,
            'id': user.id
        })
    except Exception:
        raise_db_error(description='Cannot update user')


@app.route('/articles')
def get_articles():
    articles = Article.query.all()
    return jsonify({
        'success': True,
        'articles': [a.format() for a in articles]
    })


@app.route('/articles', methods=['POST'])
@requires_auth('post:articles')
def post_articles(payload):
    try:
        id = request.json['id']
        found = Article.query.filter_by(id=id).one_or_none()
        # Already exists
        if found is not None:
            return jsonify({
                'success': True,
                'id': id
            })

        article = Article(
            id=id
        )
        article.insert()
        return jsonify({
            'success': True,
            'id': article.id
        })
    except Exception:
        raise_db_error(description='Cannot add an article.')


@app.route('/articles/<string:id>', methods=['DELETE'])
@requires_auth('delete:articles')
def delete_articles(payload, id):
    found = Article.query.filter_by(id=id).one_or_none()
    if found is None:
        raise NotFound(description='Cannot find a given article.')

    try:
        # Remove all related comments with a given article.
        map(lambda c: c.delete(), Comment.query.filter_by(article=id).all())

        found.delete()
        return jsonify({
            'success': True,
            'id': id
        })
    except Exception:
        raise_db_error(description='Cannot remove a given article.')


@app.route('/articles/<string:id>/comments')
def get_comments_from_article(id):
    comments_from_article = Comment.query.filter_by(article=id)
    recursive_comments = (
        comments_from_article.filter_by(parent=None)
        .order_by(Comment.datetime).all()
    )
    return jsonify({
        'success': True,
        'count': comments_from_article.filter_by(removed=False).count(),
        'comments': [c.recursive_format() for c in recursive_comments]
    })


@app.route('/articles/<string:id>/comments', methods=['POST'])
@requires_auth('post:comments')
def post_comment_to_article(payload, id):
    try:
        comment = Comment(
            user=payload['sub'],
            datetime=get_current_utc(),
            content=request.json['content'],
            article=id,
            parent=None,
            removed=False
        )
        comment.insert()
        return jsonify({
            'success': True,
            'id': comment.id
        })
    except Exception:
        raise_db_error(description=f'Cannot add comment to article {id}')


@app.route('/comments')
def get_comments():
    page = request.args.get('page', 1, type=int)
    comments = (
        Comment.query.filter_by(removed=False).order_by(Comment.datetime)
        .paginate(page=page, per_page=COMMENTS_PER_PAGE).query.all()
    )
    return jsonify({
        'success': True,
        'comments': [c.format() for c in comments]
    })


@app.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.filter_by(id=id).one_or_none()
    if comment is None or comment.removed:
        raise NotFound(description='Cannot find having given ID.')

    return jsonify({
        'success': True,
        'comment': comment.format()
    })


@app.route('/comments/<int:id>', methods=['POST'])
@requires_auth('post:comments')
def post_reply(payload, id):
    parent = Comment.query.filter_by(id=id).one_or_none()
    if parent is None:
        raise NotFound(description='Cannot find a comment to reply.')
    if parent.removed:
        raise UnprocessableEntity(
            description='Cannot reply to removed comment.'
        )

    try:
        comment = Comment(
            user=payload['sub'],
            removed=False,
            datetime=get_current_utc(),
            content=request.json['content'],
            article=parent.article,
            parent=id
        )
        comment.insert()
        return jsonify({
            'success': True,
            'id': comment.id
        })
    except Exception:
        raise_db_error(description=f'Cannot add comment to article {id}')


@app.route('/comments/<int:id>', methods=['PATCH'])
@requires_auth('post:comments')
def edit_comment(payload, id):
    comment = Comment.query.filter_by(id=id).one_or_none()
    if comment is None:
        raise NotFound(description='Cannot find a comment to edit.')

    if comment.removed:
        raise UnprocessableEntity(description='Cannot edit removed comment.')

    if comment.user != payload['sub']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Requestor is not an author of the comment.'
        }, 403)

    try:
        comment.content = request.json['content']
        comment.update()
        return jsonify({
            'success': True,
            'id': id
        })
    except Exception:
        raise_db_error(description='Cannot edit the comment.')


@app.route('/comments/<int:id>', methods=['DELETE'])
@requires_auth()
def delete_comment(payload, id):
    comment = Comment.query.filter_by(id=id).one_or_none()
    if comment is None:
        raise NotFound(description='Cannot find a comment to remove.')

    if comment.removed:
        raise UnprocessableEntity(
            description='Cannot remove already removed comment.'
        )

    try:
        check_permissions('delete:comments', payload)
    except AuthError:
        if comment.user != payload['sub']:
            raise AuthError({
                'code': 'unauthorized',
                'description': (
                    'Requestor is neither an administrator nor',
                    'author of the comment.'
                )
            }, 403)

    try:
        comment.delete()

        return jsonify({
            'success': True,
            'id': id
        })
    except Exception:
        raise_db_error(description='Cannot edit the comment.')


@app.errorhandler(NotFound)
def not_found(error):
    return jsonify({
      'success': False,
      'error': error.code,
      'message': error.description
    }), error.code


@app.errorhandler(UnprocessableEntity)
def unprocessable_entity(error):
    return jsonify({
      'success': False,
      'error': error.code,
      'message': error.description
    }), error.code


@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': f'{error.error["code"]}: {error.error["description"]}'
    }), error.status_code
