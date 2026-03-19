# 📖 GUIDE COMPLET D'INSTALLATION & LANCEMENT

## Table des Matières

1. [Architecture du système](#-architecture)
2. [Pré-requis](#-pré-requis)
3. [Installation pas à pas](#-installation-pas-à-pas)
4. [Configuration de l'environnement](#-configuration-de-lenvironnement)
5. [Lancer les services (PostgreSQL & Redis)](#-lancer-les-services)
6. [Lancer le pipeline](#-lancer-le-pipeline)
7. [Monitoring & Debugging](#-monitoring--debugging)
8. [Troubleshooting](#-troubleshooting)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    DATA PIPELINE 2.0                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  INPUT FILES (XLS)                                              │
│        ↓                                                         │
│  [Selenium Downloader] → Download reports from web             │
│        ↓                                                         │
│  [Processor] → Convert & parse CSV data                        │
│        ↓                                                         │
│  [Pipeline Service] → Transform DataFrame                      │
│        ├─→ Export CSV/Excel (files/)                           │
│        └─→ Bulk Upsert to PostgreSQL (database)                │
│        ↓                                                         │
│  ✅ Data stored in PostgreSQL                                   │
│                                                                   │
│  🔄 Execution: Celery Workers (async via Redis)                │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Pré-requis

Avant de commencer, tu dois avoir:

### Système d'exploitation
- **Windows 10/11** ✅ (Tu utilises Windows)
- Terminal (PowerShell, CMD, ou WSL)

### Logiciels à installer
- **Python 3.10+** → [Download](https://www.python.org/downloads/)
- **Docker Desktop** → [Download](https://www.docker.com/products/docker-desktop) (pour PostgreSQL & Redis)
- **Git** (optionnel pour versionning)

### Vérifier l'installation

```powershell
# Vérifie Python
python --version
# Devrait afficher: Python 3.10.x ou supérieur

# Vérifie Docker
docker --version
# Devrait afficher: Docker version 20.x ou supérieur

# Vérifie pip
pip --version
# Devrait afficher: pip 23.x ou supérieur
```

Si Python n'est pas installé:
```powershell
# Via Scoop (Windows Package Manager)
scoop install python

# Ou télécharge depuis: https://www.python.org/downloads/
```

---

## 🔧 Installation pas à pas

### ÉTAPE 1️⃣ : Créer et activer un environnement virtuel Python

⚠️ **IMPORTANT**: Toujours travailler dans un virtualenv, JAMAIS en global!

```powershell
# Ouvrir PowerShell dans le dossier du projet
cd "d:\Utilisateurs\soava.rakotomanana\Workspace\Automatisation\Traitement-donn-es"

# Créer virtualenv
python -m venv venv

# ✅ Activer l'environnement (Windows)
.\venv\Scripts\Activate.ps1

# Si erreur d'exécution sur PowerShell:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Après activation**, tu devrais voir `(venv)` au début du terminal:
```
(venv) PS D:\Utilisateurs\soava.rakotomanana\Workspace\Automatisation\Traitement-donn-es>
```

### ÉTAPE 2️⃣ : Installer les dépendances Python

```powershell
# S'assurer que pip est à jour
python -m pip install --upgrade pip

# Installer TOUTES les dépendances du projet
pip install -r requirements.txt

# ⏳ Cela prendra quelques minutes...
# Attends la fin du message: "Successfully installed ..."
```

**Vérifier l'installation:**
```powershell
pip list | grep -E "(sqlalchemy|celery|redis|django|fastapi)"
```

### ÉTAPE 3️⃣ : Créer le fichier `.env` (Configuration)

```powershell
# Copier le template
Copy-Item .env.example .env

# Vérifier qu'il est créé
Get-Content .env
```

**Éditer le fichier `.env` avec tes paramètres réels:**

Utilise VS Code ou un éditeur de texte:
```bash
code .env
```

Remplir les valeurs:
```ini
# DATABASE - PostgreSQL
DATABASE_URL=postgresql://postgres:password@localhost:5432/pipeline_db
DB_POOL_SIZE=10
DB_MAX_OVERFLOW=20
DB_POOL_RECYCLE=3600

# CELERY - Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
CELERY_TASK_TIME_LIMIT=1800
CELERY_TASK_SOFT_TIME_LIMIT=1500
CELERY_DEFAULT_RETRY_DELAY=60
CELERY_RESULT_EXPIRES=3600

# FILE PATHS
INPUT_DIR=input
OUTPUT_DIR=output
TEMP_DIR=temp
LOG_DIR=logs

# LOGGING
LOG_LEVEL=INFO
DEBUG=False

# SELENIUM
SELENIUM_HEADLESS=True
SELENIUM_IMPLICIT_WAIT=10
SELENIUM_PAGE_LOAD_TIMEOUT=30
```

⚠️ **IMPORTANT**: 
- `DATABASE_URL`: Change `password` par un vrai mot de passe sécurisé!
- Ne pas commit `.env` dans Git (mettre dans `.gitignore`)

---

## 🌍 Configuration de l'Environnement

### 1️⃣ Charger les variables d'environnement

Python lit automatiquement `.env` via `python-dotenv`. Vérifie que le fichier existe:

```powershell
# Vérifier que .env existe
Test-Path .env
# Devrait afficher: True

# Voir le contenu
Get-Content .env
```

### 2️⃣ Tester la lecture des variables

```powershell
# Lancer Python interactif
python

# Dans Python:
import os
from dotenv import load_dotenv
load_dotenv()

# Vérifier que les variables sont chargées
print(os.getenv("DATABASE_URL"))
print(os.getenv("CELERY_BROKER_URL"))

# Quitter
exit()
```

---

## 🐘 Lancer les Services

### Prérequis: Docker Desktop

1. Télécharge [Docker Desktop](https://www.docker.com/products/docker-desktop)
2. Installe et redémarre ton PC
3. Les commandes `docker` doivent être disponibles dans PowerShell

### Service 1️⃣ : PostgreSQL

**Créer et démarrer le conteneur PostgreSQL:**

```powershell
# Télécharger l'image PostgreSQL
docker pull postgres:16

# Démarrer le conteneur
docker run `
  --name pipeline_postgres `
  -e POSTGRES_USER=postgres `
  -e POSTGRES_PASSWORD=password `
  -e POSTGRES_DB=pipeline_db `
  -p 5432:5432 `
  -d `
  postgres:16

# Vérifier que c'est en cours d'exécution
docker ps
```

**En cas d'erreur** (port 5432 déjà utilisé):
```powershell
# Arrêter le conteneur existant
docker stop pipeline_postgres
docker rm pipeline_postgres

# Puis relancer les commandes ci-dessus
```

**Vérifier la connexion PostgreSQL:**

```powershell
# Via Python
python -c "
from sqlalchemy import create_engine
engine = create_engine('postgresql://postgres:password@localhost:5432/pipeline_db')
print('✅ PostgreSQL connecté!')
"
```

---

### Service 2️⃣ : Redis

**Créer et démarrer le conteneur Redis:**

```powershell
# Télécharger l'image Redis
docker pull redis:7

# Démarrer le conteneur
docker run `
  --name pipeline_redis `
  -p 6379:6379 `
  -d `
  redis:7

# Vérifier que c'est en cours d'exécution
docker ps
```

**Vérifier la connexion Redis:**

```powershell
# Via Python
python -c "
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print('Redis ping:', r.ping())
# Devrait afficher: Redis ping: True
"
```

---

### Résumé: Status des services

```powershell
# Voir tous les conteneurs en cours
docker ps

# Output attendu:
# CONTAINER ID   IMAGE      COMMAND                  PORTS
# <id>           postgres   "postgres"               0.0.0.0:5432->5432/tcp
# <id>           redis      "redis-server"           0.0.0.0:6379->6379/tcp
```

---

## 🚀 Lancer le Pipeline

### Option A️⃣ : Mode ASYNCHRONE (Production) ⭐ RECOMMANDÉ

Este es el modo que deberías usar en producción. El pipeline se ejecuta en background y puedes monitorear el progreso.

#### Terminal 1️⃣ - Démarrer Celery Worker

```powershell
# Activer virtualenv (si pas déjà activé)
.\venv\Scripts\Activate.ps1

# Démarrer le Celery worker
celery -A tasks.celery_app worker --loglevel=info

# Attendre le message:
# [*] Ready to accept tasks
```

**Ce terminal doit rester ouvert!** ⚠️

#### Terminal 2️⃣ - Lancer le Pipeline

Ouvrir un NOUVEAU PowerShell dans le même dossier du projet:

```powershell
# Activer virtualenv
.\venv\Scripts\Activate.ps1

# Lancer le pipeline (asynchrone)
python run_pipeline.py

# La commande devrait afficher:
# Task ID: 12345abc...
# Check task status with: celery -A tasks.celery_app inspect active
```

#### Terminal 3️⃣ (Optionnel) - Monitorer les Tasks

Ouvrir un TROISIÈME PowerShell pour surveiller en temps réel:

```powershell
# Activer virtualenv
.\venv\Scripts\Activate.ps1

# Voir les tasks en cours
celery -A tasks.celery_app inspect active

# Affichera quelque chose comme:
# {'celery@DESKTOP-XXX': 
#   {'active': [{'id': '12345abc...', 'name': 'tasks.pipeline_task.process_pipeline_task', ...}]}
# }

# Pour voir les resultats complétés:
celery -A tasks.celery_app inspect registered
```

---

### Option B️⃣ : Mode SYNCHRONE (Développement)

Mode direct, bloque du début à la fin. Utile pour déboguer.

```powershell
# Activer virtualenv (si pas déjà activé)
.\venv\Scripts\Activate.ps1

# Lancer le pipeline (synchrone)
python run_pipeline.py --sync

# Cela va:
# 1. Télécharger les fichiers XLS
# 2. Les traiter
# 3. Exporter en CSV/Excel
# 4. Stocker en PostgreSQL
# ⏳ Peut prendre 5-30 minutes selon la taille des données

# Attendre: "===== PIPELINE TASK COMPLETED ====="
```

⚠️ **Le terminal est bloqué pendant l'exécution!**

---

## 📊 Monitoring & Debugging

### Vérifier les données dans PostgreSQL

```powershell
# Option 1: Via Python
python

# Puis:
from database.db import get_db_session
from database.models import AgentStat
session = get_db_session()
stats = session.query(AgentStat).limit(5).all()
for stat in stats:
    print(stat)
exit()
```

```powershell
# Option 2: Via psql (si installé)
psql -U postgres -d pipeline_db

# Commandes SQL:
# SELECT COUNT(*) FROM agent_stats;
# SELECT * FROM agent_stats LIMIT 10;
# \dt  # voir toutes les tables
# \q  # quitter
```

### Vérifier les logs

```powershell
# Voir les logs en direct
Get-Content logs/app.log -Tail 50 -Wait

# Ou ouvrir dans VS Code
code logs/app.log
```

### Vérifier les fichiers générés

```powershell
# Fichiers CSV/Excel
Get-ChildItem output/

# Fichiers temporaires
Get-ChildItem temp/ | head -10

# Fichiers d'entrée
Get-ChildItem input/
```

---

## 🐛 Troubleshooting

### ❌ Erreur: `ModuleNotFoundError: No module named 'sqlalchemy'`

```powershell
# Solution: Réinstaller les dépendances
pip install -r requirements.txt

# Vérifier que pip list affiche les packages
pip list | grep sqlalchemy
```

### ❌ Erreur: `psycopg2: FATAL: database "pipeline_db" does not exist`

```powershell
# Solution 1: Vérifier que Docker PostgreSQL est en cours
docker ps
# Tu devrais voir 'pipeline_postgres' dans la liste

# Solution 2: Redémarrer PostgreSQL
docker restart pipeline_postgres

# Solution 3: Recréer le conteneur
docker stop pipeline_postgres
docker rm pipeline_postgres
# Puis relancer les commandes d'installation PostgreSQL
```

### ❌ Erreur: `Can't connect to Redis at localhost:6379`

```powershell
# Solution: Vérifier que Redis est en cours
docker ps
# Tu devrais voir 'pipeline_redis' dans la liste

# Redémarrer Redis
docker restart pipeline_redis

# Vérifier la connexion
python -c "import redis; print(redis.Redis().ping())"
```

### ❌ Erreur: `Celery worker doesn't receive tasks`

```powershell
# 1. Vérifier que Redis est en cours
docker ps | grep redis

# 2. Vérifier CELERY_BROKER_URL dans .env
Get-Content .env | grep CELERY_BROKER_URL

# 3. Redémarrer le worker
# (Arrête le worker avec Ctrl+C et relance)
celery -A tasks.celery_app worker --loglevel=debug
# Ajout du debug pour plus d'infos
```

### ❌ Erreur: `Task timeout after 25 minutes`

```powershell
# Solution: Augmenter le timeout dans .env
# CELERY_TASK_TIME_LIMIT=3600  # 1 heure au lieu de 30 min
# CELERY_TASK_SOFT_TIME_LIMIT=3300  # 55 min au lieu de 25 min

# Puis redémarrer le worker
# (Ctrl+C et relance)
```

### ❌ Erreur: `Port 5432 is already in use`

```powershell
# Lister les processus utilisant le port
netstat -ano | findstr :5432

# Ou arrêter l'autre service PostgreSQL
docker stop <container_id>

# Puis redémarrer le container correct
docker start pipeline_postgres
```

---

## 📋 Checklist d'Installation Complète

Copie-colle cette checklist et coche chaque étape:

```
🔧 INSTALLATION
 ☐ Python 3.10+ installé
 ☐ pip à jour: pip install --upgrade pip
 ☐ Docker Desktop installé
 ☐ Virtualenv créé: python -m venv venv
 ☐ Virtualenv activé: .\venv\Scripts\Activate.ps1
 ☐ Dépendances installées: pip install -r requirements.txt

🌍 CONFIGURATION
 ☐ .env créé (copie de .env.example)
 ☐ DATABASE_URL configurée
 ☐ CELERY_BROKER_URL configurée
 ☐ CELERY_RESULT_BACKEND configurée

🐘 SERVICES
 ☐ PostgreSQL conteneur créé et en cours
 ☐ Redis conteneur créé et en cours
 ☐ Test connexion PostgreSQL ✅
 ☐ Test connexion Redis ✅

🚀 LANCEMENT
 ☐ Terminal 1: Celery worker démarré
 ☐ Terminal 2: Pipeline lancé (python run_pipeline.py)
 ☐ Monitoring active (celery inspect)
 ☐ Logs générés dans logs/app.log
 ☐ Données visibles dans PostgreSQL

✅ SUCCÈS!
 ☐ Fichiers CSV/Excel dans output/
 ☐ Données dans agent_stats table
 ☐ Pas d'erreurs dans les logs
```

---

## 📞 Commandes Utiles pour Faire Face à des Problèmes

```powershell
# Voir tous les conteneurs (y compris arrêtés)
docker ps -a

# Voir les logs d'un conteneur
docker logs pipeline_postgres
docker logs pipeline_redis

# Arrêter un conteneur
docker stop pipeline_postgres

# Démarrer un conteneur (après arrêt)
docker start pipeline_postgres

# Supprimer un conteneur (après arrêt)
docker rm pipeline_postgres

# Voir l'utilisation des ressources
docker stats

# Nettoyer les ressources inutilisées
docker system prune

# Vérifier les variables d'environnement chargées
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print({k: v for k, v in os.environ.items() if 'DB' in k or 'CELERY' in k})"
```

---

## 🎓 Prochaines étapes

Une fois que le pipeline fonctionne en mode Celery async:

### Créer une API FastAPI (Optionnel)

```powershell
# Créer app.py à la racine
code app.py
```

```python
from fastapi import FastAPI
from tasks.pipeline_task import process_pipeline_task

app = FastAPI()

@app.post("/pipeline/run")
def run_pipeline(download_data: bool = True):
    """Déclenche le pipeline de manière asynchrone"""
    task = process_pipeline_task.delay(download_data=download_data)
    return {"task_id": task.id, "status": "submitted"}

@app.get("/pipeline/status/{task_id}")
def get_status(task_id: str):
    """Récupère le statut d'une task"""
    from celery.result import AsyncResult
    task = AsyncResult(task_id, app=...)
    return {"state": task.state, "result": task.result}
```

Lancer l'API:
```powershell
uvicorn app:app --reload --port 8000
# Puis accéder à: http://localhost:8000/docs
```

---

## 📞 Support

Si tu rencontres un problème:

1. **Vérifier les logs**: `Get-Content logs/app.log -Tail 50`
2. **Vérifier les services**: `docker ps`
3. **Relancer Celery**: Ctrl+C et relancer le worker
4. **Vérifier la configuration**: `Get-Content .env`

---

**Bonne chance! 🚀 N'hésite pas si tu as des questions!**
