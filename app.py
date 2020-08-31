import os
from flask import Flask, jsonify
from flask_cors import CORS
from models import setup_db

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

def create_app():
    app = Flask(__name__)
    CORS(app)


    @app.route('/articles')
    def get_articles():
        pass


    @app.route('/articles', methods=['POST'])
    def post_articles():
        pass


    @app.route('/articles', methods=['DELETE'])
    def delete_articles():
        pass


    @app.route('/articles/<int:id>')
    def get_comments_from_article():
        pass


    @app.route('/articles/<int:id>', methods=['POST'])
    def post_comment_to_article():
        pass


    @app.route('/comments')
    def get_comments():
        pass


    @app.route('/comments/<int:id>')
    def get_comment():
        pass


    @app.route('/comments/<int:id>', methods=['POST'])
    def post_reply():
        pass


    @app.route('/comments/<int:id>', methods=['PATCH'])
    def edit_comment():
        pass


    @app.route('/comments/<int:id>', methods=['DELETE'])
    def delete_comment():
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

    return app

app = create_app()
setup_db(app, os.environ['DATABASE_URL'])


if __name__ == '__main__':
    app.run()
