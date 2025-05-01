from flask import Blueprint, request, jsonify
from models import db, bcrypt, User
import jwt
from config import SECRET_KEY
from kafka import KafkaProducer
import json




user_bp = Blueprint('user', __name__)

def get_kafka_producer():
    try:
        return KafkaProducer(
            bootstrap_servers='kafka:9092',
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
    except Exception as e:
        print("Erreur lors de la connexion à Kafka:", e)
        return None


@user_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    hashed_pw = bcrypt.generate_password_hash(data['password']).decode('utf-8')
    user = User(email=data['email'], password=hashed_pw)
    db.session.add(user)
    db.session.commit()

    producer = get_kafka_producer()
    if producer:
        try:
            producer.send('user_created', {'user_id': user.id, 'email': user.email})
        except Exception as e:
            print("Erreur lors de l'envoi Kafka:", e)

    return jsonify({'message': 'Utilisateur créé'}), 201



@user_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    user = User.query.filter_by(email=data['email']).first()
    if user and bcrypt.check_password_hash(user.password, data['password']):
        token = jwt.encode({'id': user.id, 'role': user.role}, SECRET_KEY, algorithm='HS256')
        return jsonify({'token': token})
    return jsonify({'message': 'Email ou mot de passe incorrect'}), 401

@user_bp.route('/', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([{'id': u.id, 'email': u.email, 'role': u.role} for u in users])

@user_bp.route('/me', methods=['GET'])
def me():
    auth = request.headers.get('Authorization')
    if not auth:
        return jsonify({'error': 'Token manquant'}), 401
    try:
        token = auth.split()[1]
        data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        user = User.query.get(data['id'])
        return jsonify({'id': user.id, 'email': user.email, 'role': user.role})
    except Exception:
        return jsonify({'error': 'Token invalide'}), 401
