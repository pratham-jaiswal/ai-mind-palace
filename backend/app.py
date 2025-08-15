from dotenv import load_dotenv

load_dotenv()

from flask import Flask
from flask_cors import CORS
from routes import register_routes
from config import Config
from models import db
from utils.env_vars import ALLOWED_ORIGINS

def create_app():
    app = Flask(__name__)
    CORS(app, supports_credentials=True, origins=ALLOWED_ORIGINS)
    app.config.from_object(Config)

    db.init_app(app)
    register_routes(app)

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
