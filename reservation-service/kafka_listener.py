from kafka import KafkaConsumer
import json
from models import db, Reservation

# Configuration du KafkaConsumer avec gestion des erreurs de connexion
def create_consumer():
    try:
        consumer = KafkaConsumer(
            'room_deleted',
            bootstrap_servers='kafka:9092',  # Kafka address in the Docker network
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='earliest',  # Reprendre à partir du début
            group_id='reservation-service'  # Identifiant du groupe de consommateurs
        )
        return consumer
    except Exception as e:
        print(f"[Kafka] Erreur lors de la connexion à Kafka: {e}")
        return None


def start_listener(app):
    with app.app_context():
        consumer = create_consumer()
        if not consumer:
            print("[Kafka] Impossible de démarrer le consommateur. Kafka non disponible.")
            return
        
        print("[Kafka] En écoute des messages sur 'room_deleted'...")
        
        # Boucle d'écoute des messages Kafka
        for msg in consumer:
            try:
                data = msg.value
                salle_id = data.get('salle_id')
                
                if salle_id:
                    # Suppression des réservations associées à la salle supprimée
                    reservations_to_delete = Reservation.query.filter_by(salle_id=salle_id).all()
                    if reservations_to_delete:
                        for reservation in reservations_to_delete:
                            db.session.delete(reservation)
                        db.session.commit()
                        print(f"[Kafka] Réservations supprimées pour salle {salle_id}")
                    else:
                        print(f"[Kafka] Aucune réservation trouvée pour la salle {salle_id}")
                else:
                    print("[Kafka] Données invalides reçues (salle_id manquant).")
            
            except Exception as e:
                print(f"[Kafka] Erreur lors du traitement du message: {e}")
