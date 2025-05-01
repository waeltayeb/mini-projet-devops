from flask import Flask
from config import *
from models import db, bcrypt
from routes import user_bp

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
bcrypt.init_app(app)

app.register_blueprint(user_bp, url_prefix='/user')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5001)

