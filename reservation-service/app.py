# app.py
from threading import Thread
from app_factory import create_app
from kafka_listener import start_listener

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        from models import db
        db.create_all()
    Thread(target=start_listener, args=(app,)).start()
    app.run(debug=True, host='0.0.0.0', port=5003)
