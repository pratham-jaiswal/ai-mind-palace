from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from routes import register_routes
from config import Config
from models import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    register_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
