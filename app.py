import os
from flask import Flask
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

    @app.route('/')
    def get_default():
        return 'Hello!'

    @app.route('/hello')
    def get_hello():
        return 'World!'

    return app

app = create_app()
setup_db(app, os.environ['DATABASE_URL'])


if __name__ == '__main__':
    app.run()
