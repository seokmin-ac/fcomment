import os
from flask import Flask, jsonify, request, abort
from flask_cors import CORS
from models import setup_db, Article, Comment, db_rollback
from auth import AuthError

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

app = Flask(__name__)
CORS(app)
setup_db(app, os.environ['DATABASE_URL'])

@app.route('/')
def index():
    return 'Hello!'


@app.route('/articles')
def get_articles():
    articles = Article.query.all()
    return jsonify({
        'success': True,
        'articles': [a.format() for a in articles]
    })


@app.route('/articles', methods=['POST'])
def post_articles():
    try:
        article = Article(
            id=request.json['id']
        )
        article.insert()
        return jsonify({
            'success': True,
            'id': article.id
        })
    except Exception:
        db_rollback()
        abort(422)


@app.route('/articles', methods=['DELETE'])
def delete_articles():
    pass


@app.route('/articles/<string:id>')
def get_comments_from_article(id):
    pass


@app.route('/articles/<string:id>', methods=['POST'])
def post_comment_to_article(id):
    pass


@app.route('/comments')
def get_comments():
    pass


@app.route('/comments/<int:id>')
def get_comment(id):
    pass


@app.route('/comments/<int:id>', methods=['POST'])
def post_reply(id):
    pass


@app.route('/comments/<int:id>', methods=['PATCH'])
def edit_comment(id):
    pass


@app.route('/comments/<int:id>', methods=['DELETE'])
def delete_comment(id):
    pass


@app.errorhandler(404)
def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': 'Resource not found.'
    }), 404


@app.errorhandler(422)
def unprocessable_entity(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': 'Unprocessable entity.'
    }), 422


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({
      'success': False,
      'error': 500,
      'message': 'Internal Server error.'
    }), 500

@app.errorhandler(AuthError)
def auth_error(error):
    return jsonify({
        'success': False,
        'error': error.status_code,
        'message': f'{error.error.code}: {error.error.description}'
    }), error.status_code


if __name__ == '__main__':
    app.run()
