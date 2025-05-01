from flask import Flask
from config import *
from models import db
from routes import salle_bp

app = Flask(__name__)
app.config.from_object('config')

db.init_app(app)
app.register_blueprint(salle_bp)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5002)

