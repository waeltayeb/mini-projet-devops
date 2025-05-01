from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    salle_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(10), nullable=False)  # Format YYYY-MM-DD
    heure_debut = db.Column(db.String(5), nullable=False)  # Format HH:MM
    heure_fin = db.Column(db.String(5), nullable=False)    # Format HH:MM
