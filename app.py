from flask import Flask
from flask_migrate import Migrate
from arnhub import create_app, db
import os

app = create_app()

# Set maximum video upload size to 1 GB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1 GB

# Register Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True)