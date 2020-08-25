from flask import Flask
from flask_cors import CORS

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

if __name__ == '__main__':
    app.run()
