from flask import Flask
from flask_migrate import Migrate
from arnhub import create_app, db
import os
from arnhub.models import User
from arnhub import db
from werkzeug.security import generate_password_hash

app = create_app()

# Set maximum video upload size to 1 GB
app.config['MAX_CONTENT_LENGTH'] = 1024 * 1024 * 1024  # 1 GB

# Register Flask-Migrate
migrate = Migrate(app, db)

if __name__ == "__main__":
    app.run(debug=True)
    
    
@app.before_first_request
def create_admin():
    with app.app_context():
        if not User.query.filter_by(username="ARNcode").first():
            admin = User(
                username="ARNcode",
                email="arncode.app@gmail.com",
                password=generate_password_hash("Abd123an@", method="sha256"),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("⚡ Admin created:", admin.username)
        else:
            print("⚠️ Admin already exists.")