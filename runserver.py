from app import create_app
from app.config import Config
from app.database import db

if __name__ == "__main__":
    app = create_app(config=Config)
    app.run(debug=True)
