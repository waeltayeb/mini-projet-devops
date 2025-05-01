from flask import Blueprint, request, jsonify
from models import db, Salle
from kafka import KafkaProducer
import json

salle_bp = Blueprint('salle', __name__)


def get_kafka_producer():
    try:
        return KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception as e:
        print("Erreur lors de la connexion à Kafka:", e)
        return None


@salle_bp.route('/rooms', methods=['POST'])
def add_room():
    data = request.json
    salle = Salle(nom=data['nom'], capacite=data['capacite'])
    db.session.add(salle)
    db.session.commit()
    return jsonify({'message': 'Salle ajoutée'}), 201

@salle_bp.route('/rooms', methods=['GET'])
def list_rooms():
    salles = Salle.query.all()
    return jsonify([{'id': s.id, 'nom': s.nom, 'capacite': s.capacite} for s in salles])

@salle_bp.route('/rooms/<int:id>', methods=['DELETE'])
def delete_room(id):
    salle = Salle.query.get(id)
    if salle:
        db.session.delete(salle)
        db.session.commit()

        #  Envoi d’un message Kafka
        producer = get_kafka_producer()
        if producer:
            try:
                producer.send('room_deleted', {'salle_id': id})
            except Exception as e:
                print("Erreur lors de l'envoi Kafka:", e)
        

        return jsonify({'message': 'Salle supprimée'})
    return jsonify({'message': 'Salle non trouvée'}), 404
