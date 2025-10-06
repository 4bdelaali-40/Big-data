# Reddit Real-Time Analysis Dashboard

## Vue d'ensemble

Ce projet implémente un système complet d'analyse en temps réel des posts Reddit utilisant une architecture de streaming basée sur Kafka, Spark, Elasticsearch 9.x et Django. Le système collecte, traite, analyse le sentiment et visualise les données Reddit via un dashboard interactif.

## Architecture du Système

```
Reddit API → Kafka Producer → Kafka Topic → Spark Consumer → Elasticsearch 9.x → Django API → Dashboard Web
```

### Composants Principaux

1. **Kafka Producer** (`kafka_producer.py`) : Collecte les posts Reddit en temps réel
2. **Spark Consumer** (`spark_consumer.py`) : Traite les données et effectue l'analyse de sentiment
3. **Elasticsearch 9.x** : Stocke et indexe les données analysées
4. **Django Backend** (`views.py`) : API REST pour le dashboard
5. **Dashboard Web** (`dashboard.html`) : Interface utilisateur interactive

## Prérequis

### Logiciels Requis

- Python 3.8+
- Apache Kafka 2.8+
- Apache Spark 3.4.0
- Elasticsearch 9.x
- Django 4.0+

### Dépendances Python

```bash
pip install pyspark==3.4.0
pip install kafka-python
pip install praw
pip install textblob
pip install elasticsearch==8.0+
pip install django
```

## Installation

### 1. Configuration de Kafka

```bash
# Démarrer Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Démarrer Kafka
bin/kafka-server-start.sh config/server.properties

# Créer le topic
bin/kafka-topics.sh --create --topic reddit_posts --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
```

### 2. Configuration d'Elasticsearch 9.x

```bash
# Démarrer Elasticsearch
./bin/elasticsearch

# Vérifier la connexion
curl http://localhost:9200

# Initialiser l'index
python elasticsearch_config.py
```

### 3. Configuration de Reddit API

1. Créez une application Reddit sur https://www.reddit.com/prefs/apps
2. Obtenez `client_id` et `client_secret`
3. Remplacez les credentials dans `kafka_producer.py`:

```python
reddit = praw.Reddit(
    client_id="VOTRE_CLIENT_ID",
    client_secret="VOTRE_CLIENT_SECRET",
    user_agent="script:RedditAnalysis:v1.0 (by /u/VOTRE_USERNAME)"
)
```

### 4. Configuration Django

```bash
# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Démarrer le serveur
python manage.py runserver
```

## Démarrage du Système

### Ordre de Démarrage

1. **Elasticsearch** (doit être démarré en premier)
```bash
./bin/elasticsearch
```

2. **Kafka & Zookeeper**
```bash
# Terminal 1 - Zookeeper
bin/zookeeper-server-start.sh config/zookeeper.properties

# Terminal 2 - Kafka
bin/kafka-server-start.sh config/server.properties
```

3. **Initialiser Elasticsearch**
```bash
python elasticsearch_config.py
```

4. **Spark Consumer**
```bash
python spark_consumer.py
```

5. **Kafka Producer**
```bash
python kafka_producer.py
```

6. **Django Server**
```bash
python manage.py runserver
```

7. **Accéder au Dashboard**
```
http://localhost:8000
```

## Fonctionnalités

### Analyse de Sentiment
- Classification automatique : Positif, Négatif, Neutre
- Utilise TextBlob pour l'analyse de polarité
- Seuils : >0.1 (positif), <-0.1 (négatif), sinon neutre

### Extraction de Hashtags
- Détection automatique des hashtags (#mot)
- Limitation à 10 hashtags par post
- Agrégation et comptage des hashtags populaires

### Dashboard Interactif
- **Statistiques générales** : Nombre total de posts analysés
- **Analyse des sentiments** : Graphiques circulaires et en barres
- **Hashtags populaires** : Top 10 des hashtags avec visualisations
- **Actualisation automatique** : Mise à jour toutes les 30 secondes
- **Test de connexion** : Vérification d'Elasticsearch en temps réel

## API Endpoints

### `/api/stats/`
Retourne les statistiques complètes du système

**Réponse:**
```json
{
  "total_posts": 150,
  "hashtags": [
    {"tag": "#python", "count": 25},
    {"tag": "#data", "count": 18}
  ],
  "sentiments": {
    "positive": 60,
    "negative": 30,
    "neutral": 60
  },
  "status": "success"
}
```

### `/api/test-es/`
Teste la connexion Elasticsearch

**Réponse:**
```json
{
  "status": "success",
  "elasticsearch": "connected",
  "version": "9.0.0",
  "index_exists": true,
  "document_count": 150
}
```

## Dépannage

### Elasticsearch ne démarre pas
```bash
# Vérifier le status
curl http://localhost:9200

# Vérifier les logs
tail -f logs/elasticsearch.log
```

### Kafka Producer échoue
```bash
# Vérifier que le topic existe
bin/kafka-topics.sh --list --bootstrap-server localhost:9092

# Vérifier les messages
bin/kafka-console-consumer.sh --topic reddit_posts --from-beginning --bootstrap-server localhost:9092
```

### Spark Consumer ne traite pas les données
```bash
# Vérifier les logs Spark
# Les logs apparaissent dans le terminal où spark_consumer.py est exécuté

# Vérifier la connexion Kafka
# Le consumer doit afficher: "Consommateur Spark démarré pour ES 9.x, en attente de données..."
```

### Dashboard ne charge pas les données
```bash
# Vérifier que Django tourne
curl http://localhost:8000/api/stats/

# Vérifier les logs Django
python manage.py runserver --verbosity 3
```


## Configuration Elasticsearch 9.x

### Mapping de l'Index

```json
{
  "mappings": {
    "properties": {
      "title": {"type": "text"},
      "content": {"type": "text"},
      "author": {"type": "keyword"},
      "subreddit": {"type": "keyword"},
      "score": {"type": "integer"},
      "sentiment": {"type": "keyword"},
      "hashtags": {"type": "keyword"},
      "created_utc": {"type": "date"},
      "timestamp": {"type": "date"}
    }
  }
}
```

## Performance

### Optimisations Recommandées

1. **Kafka**: Augmenter les partitions pour plus de parallélisme
2. **Spark**: Ajuster `processingTime` selon le volume de données
3. **Elasticsearch**: Configurer les shards et réplicas selon les besoins

## Améliorations Futures

- [ ] Ajouter l'authentification utilisateur
- [ ] Implémenter le filtrage par subreddit
- [ ] Ajouter des alertes en temps réel
- [ ] Exporter les données en CSV/PDF
- [ ] Intégrer des modèles ML plus avancés pour le sentiment
- [ ] Ajouter la détection de tendances
- [ ] Implémenter un système de cache Redis

## Guide de Démarrage Complet - Dans l'Ordre !

## Pré-requis à installer/télécharger

1. **Elasticsearch** (téléchargez depuis elastic.co)
2. **Apache Kafka** (inclut Zookeeper)
3. **Apache Spark** 
4. **Python** avec les packages du requirements.txt

---

## Ordre de Démarrage (TRÈS IMPORTANT!)

### Étape 1: Démarrer Elasticsearch
```bash
# Naviguez vers le dossier Elasticsearch
cd /chemin/vers/elasticsearch/bin

# Windows
elasticsearch.bat

# Linux/Mac
./elasticsearch
```
**✅ Vérifiez:** Ouvrez http://localhost:9200 dans votre navigateur

---

### Étape 2: Démarrer Zookeeper (Terminal séparé)
```bash
# Naviguez vers le dossier Kafka
cd /chemin/vers/kafka/bin

# Windows
zookeeper-server-start.bat ../config/zookeeper.properties

.\bin\windows\zookeeper-server-start.bat .\config\zookeeper.properties

**✅ Vérifiez:** Aucune erreur dans les logs

---

### Étape 3: Démarrer Kafka (Terminal séparé)
```bash
# Dans le même dossier Kafka/bin

# Windows
kafka-server-start.bat ../config/server.properties

.\bin\windows\kafka-server-start.bat .\config\server.properties

**✅ Vérifiez:** Aucune erreur dans les logs

---

### Étape 4: Configurer Elasticsearch (Terminal séparé)
```bash
# Dans votre dossier projet
cd /chemin/vers/votre/projet

# Configurez l'index Elasticsearch
python elasticsearch_config.py
```
**✅ Vérifiez:** Message "Index créé avec succès"

---

### Étape 5: Démarrer Django (Terminal séparé)
```bash
# Migrations d'abord
python manage.py makemigrations
python manage.py migrate

# Démarrer le serveur
python manage.py runserver
```
**✅ Vérifiez:** Ouvrez http://localhost:8000

---

### Étape 6: Démarrer Kafka Producer (Terminal séparé)
```bash
# ATTENTION: Configurez d'abord vos clés Reddit API dans kafka_producer.py
python kafka_producer.py
```
**✅ Vérifiez:** Messages "Envoyé:" dans la console

---

### Étape 7: Démarrer Spark Consumer (Terminal séparé)
```bash
# Démarrez le consumer Spark
python spark_consumer.py

set HADOOP_HOME=C:\hadoop
set HADOOP_CONF_DIR=C:\hadoop\bin
set PATH=%PATH%;C:\hadoop\bin

spark-submit --conf spark.pyspark.python="python" --conf spark.pyspark.driver.python="python" --conf spark.sql.warehouse.dir="file:///C:/tmp/spark-warehouse" --conf spark.sql.streaming.checkpointLocation="file:///C:/tmp/checkpoint" --conf spark.hadoop.fs.file.impl=org.apache.hadoop.fs.LocalFileSystem --packages org.apache.spark:spark-sql-kafka-0-10_2.13:4.0.0 spark_consumer.py

```
**✅ Vérifiez:** Messages "Consumer Spark démarré..."

---

## Résumé des Terminaux Nécessaires

Vous aurez besoin de **7 terminaux** au total :

1. **Terminal 1:** `elasticsearch.bat` 
2. **Terminal 2:** `zookeeper-server-start.bat`
3. **Terminal 3:** `kafka-server-start.bat`
4. **Terminal 4:** `python elasticsearch_config.py` (une fois seulement)
5. **Terminal 5:** `python manage.py runserver`
6. **Terminal 6:** `python kafka_producer.py`
7. **Terminal 7:** `python spark_consumer.py`

---

## Points Importants

### Configuration Reddit API (OBLIGATOIRE)
Avant l'étape 6, modifiez `kafka_producer.py` :
```python
reddit = praw.Reddit(
    client_id="VOTRE_CLIENT_ID_ICI",
    client_secret="VOTRE_CLIENT_SECRET_ICI", 
    user_agent="reddit_analysis"
)
```

### Créer une app Reddit :
1. Allez sur https://www.reddit.com/prefs/apps
2. Cliquez "Create App"
3. Choisissez "script"
4. Copiez client_id et client_secret

---

## Vérifications Rapides

### Test Elasticsearch
```bash
curl http://localhost:9200
```

### Test Kafka
```bash
# Créer un topic de test
kafka-topics.bat --create --topic test --bootstrap-server localhost:9092

# Lister les topics
kafka-topics.bat --list --bootstrap-server localhost:9092
```

### Test Django
```bash
curl http://localhost:8000/api/stats/
```

---

## Dépannage Commun

### Erreur "Port déjà utilisé"
```bash
# Windows - Tuer les processus
taskkill /F /IM java.exe
taskkill /F /IM elasticsearch.exe

# Redémarrez dans l'ordre
```

### Erreur "Connexion refusée"
- Vérifiez que tous les services sont démarrés
- Attendez 30 secondes entre chaque service
- Vérifiez les ports : 9200 (Elasticsearch), 9092 (Kafka), 2181 (Zookeeper)

### Dashboard vide
1. Vérifiez les logs du Producer
2. Vérifiez les logs du Consumer
3. Testez l'API : `curl http://localhost:8000/api/stats/`

---

## Résultat Attendu

Quand tout fonctionne :
- **Dashboard** : http://localhost:8000 (avec graphiques)
- **API Stats** : http://localhost:8000/api/stats/ (JSON)
- **Elasticsearch** : http://localhost:9200/reddit_posts/_search (données)

---

## Ordre Simplifié de Démarrage

1. **Elasticsearch** → Attendez 30 secondes
2. **Zookeeper** → Attendez 10 secondes  
3. **Kafka** → Attendez 10 secondes
4. **elasticsearch_config.py** → Une fois
5. **Django** → Testez le dashboard
6. **Kafka Producer** → Vérifiez les logs
7. **Spark Consumer** → Vérifiez les logs