from elasticsearch import Elasticsearch
import logging
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_elasticsearch():
    try:
        logger.info("🚀 Configuration d'Elasticsearch 9.x...")
        
        # Configuration client ES 9.x
        es = Elasticsearch(
            hosts=["http://localhost:9200"],
            verify_certs=False,
            request_timeout=60,
            # Configurations spécifiques pour ES 9.x
            headers={"Content-Type": "application/json"},
            # Si vous avez la sécurité activée
            # basic_auth=("username", "password"),
            # api_key="your_api_key",
        )
        
        # Test de connexion avec retry
        max_retries = 5
        for attempt in range(max_retries):
            try:
                if es.ping():
                    # Obtenir la version d'Elasticsearch
                    info = es.info()
                    version = info['version']['number']
                    logger.info(f"✅ Connexion à Elasticsearch {version} réussie")
                    break
                else:
                    logger.warning(f"❌ Tentative {attempt + 1}/{max_retries} échouée")
                    if attempt < max_retries - 1:
                        time.sleep(2)
            except Exception as e:
                logger.warning(f"Tentative {attempt + 1}/{max_retries}: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        else:
            logger.error("❌ Impossible de se connecter à Elasticsearch après plusieurs tentatives")
            return False
        
        # Supprimer l'index s'il existe
        if es.indices.exists(index='reddit_posts'):
            es.indices.delete(index='reddit_posts')
            logger.info("🗑️ Index existant supprimé")
        
        # Mapping adapté pour ES 9.x
        mapping = {
            "settings": {
                "number_of_shards": 1,
                "number_of_replicas": 0,
                "analysis": {
                    "analyzer": {
                        "custom_text_analyzer": {
                            "tokenizer": "standard",
                            "filter": ["lowercase", "stop"]
                        }
                    }
                },
                # Nouvelles options ES 9.x
                "index": {
                    "max_result_window": 10000,
                    "refresh_interval": "1s"
                }
            },
            "mappings": {
                "properties": {
                    "title": {
                        "type": "text",
                        "analyzer": "custom_text_analyzer",
                        # ES 9.x supporte de nouveaux types de champs
                        "fields": {
                            "keyword": {
                                "type": "keyword",
                                "ignore_above": 256
                            }
                        }
                    },
                    "content": {
                        "type": "text",
                        "analyzer": "custom_text_analyzer"
                    },
                    "author": {
                        "type": "keyword"
                    },
                    "subreddit": {
                        "type": "keyword"
                    },
                    "score": {
                        "type": "integer"
                    },
                    "sentiment": {
                        "type": "keyword"
                    },
                    "hashtags": {
                        "type": "keyword"
                    },
                    "created_utc": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    },
                    "timestamp": {
                        "type": "date",
                        "format": "strict_date_optional_time||epoch_millis"
                    }
                }
            }
        }
        
        # Créer l'index avec la nouvelle API
        try:
            es.indices.create(index='reddit_posts', body=mapping)
            logger.info("✅ Index 'reddit_posts' créé avec succès")
        except Exception as e:
            if "already_exists" in str(e).lower():
                logger.info("ℹ️ Index existe déjà")
            else:
                raise e
        
        # Données de test adaptées pour ES 9.x
        test_data = [
            {
                "title": "Analyse de données avec Python #python #data",
                "content": "Excellente discussion sur l'analyse de données",
                "author": "data_scientist",
                "subreddit": "datascience",
                "score": 25,
                "sentiment": "positive",
                "hashtags": ["#python", "#data"],
                "created_utc": "2025-06-22T10:00:00Z",
                "timestamp": "2025-06-22T10:00:00Z"
            },
            {
                "title": "Problème avec Elasticsearch #elasticsearch #help",
                "content": "Configuration difficile, besoin d'aide",
                "author": "dev_user",
                "subreddit": "elasticsearch",
                "score": 5,
                "sentiment": "negative",
                "hashtags": ["#elasticsearch", "#help"],
                "created_utc": "2025-06-22T11:00:00Z",
                "timestamp": "2025-06-22T11:00:00Z"
            },
            {
                "title": "Tutorial Django #django #web",
                "content": "Guide complet pour débuter avec Django",
                "author": "django_expert",
                "subreddit": "django",
                "score": 42,
                "sentiment": "positive",
                "hashtags": ["#django", "#web"],
                "created_utc": "2025-06-22T12:00:00Z",
                "timestamp": "2025-06-22T12:00:00Z"
            },
            {
                "title": "Machine Learning avec Spark #ml #spark",
                "content": "Discussion sur l'utilisation de Spark pour ML",
                "author": "ml_enthusiast",
                "subreddit": "MachineLearning",
                "score": 18,
                "sentiment": "neutral",
                "hashtags": ["#ml", "#spark"],
                "created_utc": "2025-06-22T13:00:00Z",
                "timestamp": "2025-06-22T13:00:00Z"
            },
            {
                "title": "Kafka streaming #kafka #realtime",
                "content": "Implémentation de streaming en temps réel",
                "author": "streaming_pro",
                "subreddit": "kafka",
                "score": 31,
                "sentiment": "positive",
                "hashtags": ["#kafka", "#realtime"],
                "created_utc": "2025-06-22T14:00:00Z",
                "timestamp": "2025-06-22T14:00:00Z"
            }
        ]
        
        # Indexer les données de test avec la nouvelle API
        for i, doc in enumerate(test_data):
            try:
                result = es.index(index='reddit_posts', body=doc)
                logger.info(f"📄 Document {i+1} indexé: {result['_id']}")
            except Exception as e:
                logger.error(f"Erreur indexation doc {i+1}: {e}")
        
        # Forcer la mise à jour
        es.indices.refresh(index='reddit_posts')
        
        # Vérification finale avec gestion ES 9.x
        search_result = es.search(index='reddit_posts', body={"query": {"match_all": {}}})
        
        # ES 9.x peut retourner le total sous différents formats
        if isinstance(search_result['hits']['total'], dict):
            total_docs = search_result['hits']['total']['value']
        else:
            total_docs = search_result['hits']['total']
        
        # Obtenir la version ES
        info = es.info()
        es_version = info['version']['number']
        
        print("\n" + "="*70)
        print("🎉 CONFIGURATION ELASTICSEARCH 9.x TERMINÉE AVEC SUCCÈS!")
        print("="*70)
        print(f"🔧 Version Elasticsearch: {es_version}")
        print(f"✅ Index créé: reddit_posts")
        print(f"📊 Documents de test: {total_docs}")
        print(f"🌐 Elasticsearch 9.x prêt pour Django!")
        print("="*70)
        print("\n📋 ÉTAPES SUIVANTES:")
        print("1. python manage.py makemigrations")
        print("2. python manage.py migrate")
        print("3. python manage.py runserver")
        print("4. Ouvrez http://localhost:8000")
        print("="*70)
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Erreur: {e}")
        print("\n" + "="*50)
        print("⚠️ TROUBLESHOOTING ES 9.x:")
        print("="*50)
        print("1. Vérifiez qu'Elasticsearch 9.x est démarré:")
        print("   curl http://localhost:9200")
        print("2. Vérifiez la version:")
        print("   curl http://localhost:9200/_cluster/health")
        print("3. Vérifiez les logs Elasticsearch")
        print("4. Si sécurité activée, configurez l'authentification")
        print("="*50)
        return False

if __name__ == "__main__":
    setup_elasticsearch()