from flask import Blueprint, request, jsonify
from models import db, Reservation
from datetime import datetime
from kafka import KafkaProducer
import json




reservation_bp = Blueprint('reservation', __name__)

def get_kafka_producer():
    try:
        return KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception as e:
        print("Erreur lors de la connexion à Kafka:", e)
        return None

@reservation_bp.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.json

    # Vérifie les conflits
    conflits = Reservation.query.filter_by(
        salle_id=data['salle_id'],
        date=data['date']
    ).filter(
        Reservation.heure_debut < data['heure_fin'],
        Reservation.heure_fin > data['heure_debut']
    ).all()

    #if conflits:
    #    return jsonify({'error': 'Conflit de réservation'}), 409

    reservation = Reservation(
        user_id=data['user_id'],
        salle_id=data['salle_id'],
        date=data['date'],
        heure_debut=data['heure_debut'],
        heure_fin=data['heure_fin']
    )
    db.session.add(reservation)
    db.session.commit()

    # Envoi d’un message Kafka
    producer = get_kafka_producer()
    if producer:
        try:
            producer.send('reservation_created', {
                'reservation_id': reservation.id,
                'salle_id': reservation.salle_id,
                'user_id': reservation.user_id,
                'date': reservation.date,
                'heure_debut': reservation.heure_debut,
                'heure_fin': reservation.heure_fin
            })
        except Exception as e:
            print("Erreur lors de l'envoi Kafka:", e)

    return jsonify({'message': 'Réservation créée'}), 201


@reservation_bp.route('/reservations', methods=['GET'])
def list_reservations():
    reservations = Reservation.query.all()
    return jsonify([
        {
            'id': r.id,
            'user_id': r.user_id,
            'salle_id': r.salle_id,
            'date': r.date,
            'heure_debut': r.heure_debut,
            'heure_fin': r.heure_fin
        } for r in reservations
    ])

@reservation_bp.route('/reservations/<int:id>', methods=['DELETE'])
def delete_reservation(id):
    r = Reservation.query.get(id)
    if r:
        db.session.delete(r)
        db.session.commit()
        return jsonify({'message': 'Réservation supprimée'})
    return jsonify({'message': 'Réservation non trouvée'}), 404
