from app import create_app
from app.config import TestConfig


if __name__ == "__main__":
    app = create_app(config=TestConfig)
    app.run()
