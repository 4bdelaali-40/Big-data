from django.shortcuts import render
from django.http import JsonResponse
from elasticsearch import Elasticsearch
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)

def get_elasticsearch_client():
    """Retourne un client Elasticsearch configuré pour ES 9.x"""
    try:
        es = Elasticsearch(
            hosts=['http://localhost:9200'],
            verify_certs=False,
            request_timeout=30,
            # Configurations spécifiques ES 9.x
            api_key=None,  # Si vous utilisez l'authentification par clé API
            basic_auth=None,  # Si vous utilisez l'authentification basique
            # Nouvelle syntaxe pour les headers
            headers={"Content-Type": "application/json"}
        )
        return es
    except Exception as e:
        logger.error(f"Erreur connexion Elasticsearch: {e}")
        return None

def dashboard(request):
    return render(request, 'reddit_app/dashboard.html')

def get_stats(request):
    try:
        es = get_elasticsearch_client()
        if not es or not es.ping():
            logger.warning("Elasticsearch non disponible, utilisation de données par défaut")
            return JsonResponse({
                'total_posts': 0,
                'hashtags': [
                    {'tag': '#test', 'count': 5},
                    {'tag': '#reddit', 'count': 3},
                ],
                'sentiments': {
                    'positive': 2,
                    'negative': 1,
                    'neutral': 2
                },
                'status': 'elasticsearch_offline'
            })
        
        # Vérifier si l'index existe
        if not es.indices.exists(index='reddit_posts'):
            logger.warning("Index reddit_posts n'existe pas")
            return JsonResponse({
                'total_posts': 0,
                'hashtags': [],
                'sentiments': {'positive': 0, 'negative': 0, 'neutral': 0},
                'status': 'index_missing'
            })
        
        # Statistiques générales - Nouvelle syntaxe ES 9.x
        total_query = {"query": {"match_all": {}}}
        total_result = es.search(index='reddit_posts', body=total_query, size=0)
        
        # ES 9.x peut retourner le total sous différents formats
        if isinstance(total_result['hits']['total'], dict):
            total_posts = total_result['hits']['total']['value']
        else:
            total_posts = total_result['hits']['total']
        
        # Top hashtags avec la nouvelle syntaxe d'agrégation
        hashtags = []
        try:
            hashtags_query = {
                "size": 0,
                "aggs": {
                    "hashtags": {
                        "terms": {
                            "field": "hashtags",
                            "size": 10
                        }
                    }
                }
            }
            
            hashtags_result = es.search(index="reddit_posts", body=hashtags_query)
            if 'aggregations' in hashtags_result:
                hashtags = [
                    {"tag": bucket["key"], "count": bucket["doc_count"]} 
                    for bucket in hashtags_result["aggregations"]["hashtags"]["buckets"]
                ]
        except Exception as e:
            logger.warning(f"Erreur hashtags: {e}")
        
        # Analyse des sentiments
        sentiments = {'positive': 0, 'negative': 0, 'neutral': 0}
        try:
            sentiment_query = {
                "size": 0,
                "aggs": {
                    "sentiments": {
                        "terms": {
                            "field": "sentiment",
                            "size": 10
                        }
                    }
                }
            }
            
            sentiment_result = es.search(index="reddit_posts", body=sentiment_query)
            if 'aggregations' in sentiment_result:
                for bucket in sentiment_result["aggregations"]["sentiments"]["buckets"]:
                    sentiment_type = bucket["key"]
                    if sentiment_type in sentiments:
                        sentiments[sentiment_type] = bucket["doc_count"]
        except Exception as e:
            logger.warning(f"Erreur sentiments: {e}")
        
        return JsonResponse({
            'total_posts': total_posts,
            'hashtags': hashtags,
            'sentiments': sentiments,
            'status': 'success'
        })
        
    except Exception as e:
        logger.error(f"Erreur dans get_stats: {e}")
        return JsonResponse({
            'error': str(e),
            'total_posts': 0,
            'hashtags': [],
            'sentiments': {'positive': 0, 'negative': 0, 'neutral': 0},
            'status': 'error'
        }, status=500)

def test_elasticsearch(request):
    """Endpoint pour tester la connexion Elasticsearch ES 9.x"""
    try:
        es = get_elasticsearch_client()
        
        if not es:
            return JsonResponse({
                'status': 'error',
                'message': 'Impossible de créer le client Elasticsearch'
            })
        
        # Test de ping avec gestion des erreurs ES 9.x
        try:
            ping_result = es.ping()
            if ping_result:
                # Obtenir les informations sur le cluster ES 9.x
                info = es.info()
                es_version = info['version']['number']
                
                # Vérifier l'index
                if es.indices.exists(index='reddit_posts'):
                    doc_count = es.search(index='reddit_posts', body={"query": {"match_all": {}}}, size=0)
                    
                    # Gestion du format de retour différent en ES 9.x
                    if isinstance(doc_count['hits']['total'], dict):
                        total_docs = doc_count['hits']['total']['value']
                    else:
                        total_docs = doc_count['hits']['total']
                    
                    return JsonResponse({
                        'status': 'success',
                        'elasticsearch': 'connected',
                        'version': es_version,
                        'index_exists': True,
                        'document_count': total_docs
                    })
                else:
                    return JsonResponse({
                        'status': 'warning',
                        'elasticsearch': 'connected',
                        'version': es_version,
                        'index_exists': False,
                        'message': 'Index reddit_posts n\'existe pas. Exécutez elasticsearch_config.py'
                    })
            else:
                return JsonResponse({
                    'status': 'error',
                    'elasticsearch': 'disconnected',
                    'message': 'Elasticsearch ne répond pas'
                })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'elasticsearch': 'error',
                'message': f'Erreur de connexion: {str(e)}'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'elasticsearch': 'error',
            'message': str(e)
        })