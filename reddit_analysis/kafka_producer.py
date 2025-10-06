import praw
import json
from kafka import KafkaProducer
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ATTENTION: Remplacez par vos vraies credentials Reddit
reddit = praw.Reddit(
    client_id="SGplXeyDmX4I5DNzKYxoZA",
    client_secret="1GSYsap5_kwdpJ923JEJV_5BBD0WRg", 
    user_agent="script:TwitterAnalysisApp:v1.0 (by /u/Abdel_40)"
)

def create_kafka_producer():
    """Crée un producteur Kafka avec gestion d'erreurs"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x, default=str).encode('utf-8'),
            api_version=(0, 10, 1),
            retries=3
        )
        return producer
    except Exception as e:
        logger.error(f"Erreur création producteur Kafka: {e}")
        return None

def collect_reddit_posts():
    producer = create_kafka_producer()
    if not producer:
        logger.error("Impossible de créer le producteur Kafka")
        return
    
    try:
        logger.info("Démarrage de la collecte des posts Reddit...")
        
        for submission in reddit.subreddit('all').stream.submissions():
            try:
                post_data = {
                    'title': submission.title,
                    'content': submission.selftext if submission.selftext else '',
                    'author': str(submission.author) if submission.author else 'Unknown',
                    'subreddit': str(submission.subreddit),
                    'score': submission.score,
                    'created_utc': submission.created_utc,
                    'timestamp': time.time()
                }
                
                producer.send('reddit_posts', value=post_data)
                logger.info(f"✅ Envoyé: {submission.title[:50]}...")
                
                time.sleep(0.01)  # Pour éviter les limitations de l'API
                
            except Exception as e:
                logger.error(f"Erreur traitement post: {e}")
                continue
                
    except KeyboardInterrupt:
        logger.info("Arrêt demandé par l'utilisateur")
    except Exception as e:
        logger.error(f"Erreur dans collect_reddit_posts: {e}")
    finally:
        if producer:
            producer.close()

if __name__ == "__main__":
    collect_reddit_posts()