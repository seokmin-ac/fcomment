import os
import datetime
from pytz import utc
from flask import Flask, jsonify, request
from flask_cors import CORS
from werkzeug.exceptions import NotFound, UnprocessableEntity

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from models import setup_db, Article, Comment, db_rollback
from auth import AuthError, requires_auth, check_permissions

COMMENTS_PER_PAGE = 20


def get_current_utc():
    return utc.localize(datetime.datetime.utcnow())


app = Flask(__name__)
CORS(app)
setup_db(app, os.environ['DATABASE_URL'])


# Check is the token valid
@app.route('/auth', methods=['POST'])
@requires_auth()
def check_authority(payload):
    return jsonify({
        'success': True
    })


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
        db_rollback()
        raise UnprocessableEntity(description='Cannot add an article.')


@app.route('/articles/<string:id>', methods=['DELETE'])
@requires_auth('delete:articles')
def delete_articles(payload, id):
    found = Article.query.filter_by(id=id).one_or_none()
    if found is None:
        raise NotFound(description='Cannot find a given article.')

    try:
        # TODO: Remove all related comments with a given article.
        found.delete()
        return jsonify({
            'success': True,
            'id': id
        })
    except Exception:
        db_rollback()
        raise UnprocessableEntity(description='Cannot remove a given article.')


@app.route('/articles/<string:id>/comments')
def get_comments_from_article(id):
    comments_from_article = Comment.query.filter_by(article=id)
    recursive_comments = comments_from_article.filter_by(parent=None).order_by(Comment.datetime).all()
    return jsonify({
        'success': True,
        'count': comments_from_article.count(),
        'comments': [c.recursive_format() for c in recursive_comments]
    })


@app.route('/articles/<string:id>/comments', methods=['POST'])
@requires_auth()
def post_comment_to_article(payload, id):
    try:
        comment = Comment(
            user=payload['sub'],
            datetime=get_current_utc(),
            content=request.json['content'],
            article=id,
            parent=None
        )
        comment.insert()
        return jsonify({
            'success': True,
            'id': comment.id
        })
    except Exception:
        raise UnprocessableEntity(description=f'Cannot add comment to article {id}')


@app.route('/comments')
def get_comments():
    page = request.args.get('page', 1, type=int)
    comments = Comment.query.order_by(Comment.datetime).paginate(page=page, per_page=COMMENTS_PER_PAGE).query.all()
    return jsonify({
        'success': True,
        'comments': [c.format() for c in comments]
    })


@app.route('/comments/<int:id>')
def get_comment(id):
    comment = Comment.query.filter_by(id=id).one_or_none()
    if comment is None:
        raise NotFound(description='Cannot find having given ID.')

    return jsonify({
        'success': True,
        'comment': comment.format()
    })


@app.route('/comments/<int:id>', methods=['POST'])
@requires_auth()
def post_reply(payload, id):
    parent = Comment.query.filter_by(id=id).one_or_none()
    if parent is None:
        raise NotFound(description='Cannot find a comment to reply.')
    try:
        comment = Comment(
            user=payload['sub'],
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
        raise UnprocessableEntity(description=f'Cannot add comment to article {id}')


@app.route('/comments/<int:id>', methods=['PATCH'])
@requires_auth()
def edit_comment(payload, id):
    comment = Comment.query.filter_by(id=id).one_or_none()
    if comment is None:
        raise NotFound(description='Cannot find a comment to edit.')

    try:
        check_permissions('admin', payload)
    except AuthError:
        if comment.user != payload['sub']:
            raise AuthError({
                'code': 'unauthorized',
                'description': 'Requestor is neither a administrator nor author of the comment.'
            }, 403)
    
    try:
        comment.content = request.json['content']
        comment.update()
        return jsonify({
            'success': True,
            'id': id
        })
    except Exception:
        raise UnprocessableEntity(description='Cannot edit the comment.')


@app.route('/comments/<int:id>', methods=['DELETE'])
@requires_auth()
def delete_comment(id):
    pass


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


if __name__ == '__main__':
    app.run()
