from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json
from textblob import TextBlob
from elasticsearch import Elasticsearch
import logging
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration Spark
spark = SparkSession.builder \
    .appName("RedditAnalysis") \
    .config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.4.0") \
    .config("spark.sql.adaptive.enabled", "false") \
    .config("spark.sql.adaptive.coalescePartitions.enabled", "false") \
    .getOrCreate()

spark.sparkContext.setLogLevel("WARN")

# Configuration Elasticsearch 9.x
def get_elasticsearch_client():
    try:
        es = Elasticsearch(
            hosts=['http://localhost:9200'],
            verify_certs=False,
            request_timeout=30,
            # Configurations spécifiques ES 9.x
            headers={"Content-Type": "application/json"}
        )
        return es
    except Exception as e:
        logger.error(f"Erreur connexion Elasticsearch 9.x: {e}")
        return None

def analyze_sentiment(text):
    """Analyse le sentiment d'un texte"""
    if not text or text.strip() == '':
        return 'neutral'
    
    try:
        blob = TextBlob(str(text))
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            return 'positive'
        elif polarity < -0.1:
            return 'negative'
        else:
            return 'neutral'
    except:
        return 'neutral'

def extract_hashtags(text):
    """Extrait les hashtags d'un texte"""
    if not text:
        return []
    
    try:
        hashtags = re.findall(r'#\w+', str(text))
        return hashtags[:10]  # Limiter à 10 hashtags
    except:
        return []

def process_batch(df, epoch_id):
    """Traite un batch de données pour ES 9.x"""
    logger.info(f"Traitement du batch {epoch_id}")
    
    posts = df.collect()
    es = get_elasticsearch_client()
    
    if not es:
        logger.error("Elasticsearch 9.x non disponible")
        return
    
    processed_count = 0
    
    for row in posts:
        try:
            data = json.loads(row.value)
            
            # Combiner titre et contenu pour l'analyse
            full_text = f"{data.get('title', '')} {data.get('content', '')}"
            
            # Analyser le sentiment
            sentiment = analyze_sentiment(full_text)
            
            # Extraire les hashtags
            hashtags = extract_hashtags(full_text)
            
            # Préparer les données pour Elasticsearch 9.x
            es_data = {
                'title': data.get('title', ''),
                'content': data.get('content', ''),
                'author': data.get('author', 'Unknown'),
                'subreddit': data.get('subreddit', 'unknown'),
                'score': int(data.get('score', 0)),
                'sentiment': sentiment,
                'hashtags': hashtags,
                'created_utc': data.get('created_utc', 0),
                'timestamp': data.get('timestamp', 0)
            }
            
            # Envoyer à Elasticsearch 9.x avec gestion d'erreurs améliorée
            try:
                result = es.index(index='reddit_posts', body=es_data)
                processed_count += 1
                logger.info(f"✅ Document indexé ES 9.x: {result['_id']}")
            except Exception as es_error:
                logger.error(f"Erreur indexation ES 9.x: {es_error}")
                continue
            
        except Exception as e:
            logger.error(f"Erreur traitement post: {e}")
            continue
    
    logger.info(f"Batch {epoch_id} terminé: {processed_count} documents traités")

def main():
    try:
        logger.info("Démarrage du consommateur Spark pour ES 9.x...")
        
        # Lire depuis Kafka
        df = spark \
            .readStream \
            .format("kafka") \
            .option("kafka.bootstrap.servers", "localhost:9092") \
            .option("subscribe", "reddit_posts") \
            .option("startingOffsets", "latest") \
            .load()
        
        # Sélectionner la valeur
        df = df.select(col("value").cast("string"))
        
        # Traitement des données
        query = df.writeStream \
            .foreachBatch(process_batch) \
            .outputMode("append") \
            .trigger(processingTime='10 seconds') \
            .start()
        
        logger.info("Consommateur Spark démarré pour ES 9.x, en attente de données...")
        query.awaitTermination()
        
    except Exception as e:
        logger.error(f"Erreur dans le consommateur Spark ES 9.x: {e}")
    finally:
        spark.stop()

if __name__ == "__main__":
    main()
