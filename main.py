# To load .env file for local development.
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from app import app

if __name__ == '__main__':
    app.run()
