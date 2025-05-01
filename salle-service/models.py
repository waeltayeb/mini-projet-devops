from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

class Salle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    capacite = db.Column(db.Integer, nullable=False)
