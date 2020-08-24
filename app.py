from flask import Flask

def create_app():
    app = Flask(__name__)

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
