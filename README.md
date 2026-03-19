# 🚀 Pipeline Data - Guide de Démarrage

## 📋 Architecture

```
INPUT (XLS) → Selenium Downloader → Processor (DF) → PostgreSQL + CSV/Excel
                                                  ↓
                                            Celery Task
```

---

## ✅ AVANT DE LANCER - Checklist

### 1. **Installer les dépendances Python**
```bash
pip install -r requirements.txt
```

### 2. **Configurer les variables d'environnement**

Créer un fichier `.env` à la racine du projet (copier `.env.example`):
```bash
cp .env.example .env
```

Puis éditer `.env` avec tes paramètres:
```ini
# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/pipeline_db

# Redis
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
```

### 3. **Services externes à installer/démarrer**

#### PostgreSQL (Base de données)
```bash
# Windows - via WSL ou Docker
docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=pipeline_db -p 5432:5432 -d postgres:16

# Ou via Scoop/Chocolatey si préféré
```

#### Redis (Message broker pour Celery)
```bash
# Windows - via Docker
docker run --name redis -p 6379:6379 -d redis:7

# Ou via WSL
```

### 4. **Créer les tables de base de données**

Les tables se créent automatiquement au premier lancement! ✅
```python
# Par le script run_pipeline.py ou via Python shell:
from database.db import create_all_tables
create_all_tables()
```

---

## 🎯 LANCER LE PIPELINE

### Option 1️⃣ : Mode **ASYNCHRONE** (Production) ⭐ RECOMMANDÉ

#### Terminal 1 - Démarrer Celery Worker
```bash
celery -A tasks.celery_app worker --loglevel=info
```

#### Terminal 2 - Déclencher le pipeline
```bash
# Depuis Python
python -c "from tasks.pipeline_task import process_pipeline_task; result = process_pipeline_task.delay(); print(f'Task ID: {result.id}')"

# Ou via script
python run_pipeline.py
```

#### Terminal 3 (optionnel) - Monitoring Celery
```bash
celery -A tasks.celery_app events
# Ou
celery -A tasks.celery_app inspect active
```

---

### Option 2️⃣ : Mode **SYNCHRONE** (Développement)

```bash
python run_pipeline.py --sync
```

⚠️ Cela bloque jusqu'à la fin du traitement

---

### Option 3️⃣ : Via **FastAPI** (Bientôt - pour créer une API REST)

```python
# Exemple FastAPI app.py à créer:
from fastapi import FastAPI
from tasks.pipeline_task import process_pipeline_task

app = FastAPI()

@app.post("/pipeline/run")
def run_pipeline():
    task = process_pipeline_task.delay(
        download_data=True,
        export_csv_files=True,
        export_to_db=True
    )
    return {"task_id": task.id, "status": "submitted"}

@app.get("/pipeline/status/{task_id}")
def get_status(task_id: str):
    from celery.result import AsyncResult
    task = AsyncResult(task_id, app=...)
    return {"state": task.state, "result": task.result}

# Lancer:
# uvicorn app:app --reload
```

---

## 📊 Vérifier que tout fonctionne

### 1. Tester la connexion PostgreSQL
```python
from database.db import get_db_session
from database.models import AgentStat
session = get_db_session()
print("✅ PostgreSQL OK")
```

### 2. Tester la connexion Redis
```python
import redis
r = redis.Redis(host='localhost', port=6379, db=0)
print(r.ping())  # Should print True
```

### 3. Vérifier les tables
```sql
-- Via psql:
\dt agent_stats
SELECT * FROM agent_stats LIMIT 10;
```

---

## 📁 Structure finale du projet

```
.
├── .env                      # ⭐ A créer (copie de .env.example)
├── .env.example              # Template de configuration
├── config.py                 # Global config (lectures .env)
├── requirements.txt          # ✅ Mis à jour avec Celery, SQLAlchemy, Redis
├── main.py                   # Pipeline synchrone (existing)
├── run_pipeline.py           # Launcher async/sync
│
├── database/                 # ✅ NEW - PostgreSQL ORM
│   ├── __init__.py
│   ├── db.py                 # ✅ Connection & session
│   ├── models.py             # ✅ SQLAlchemy models
│   └── crud.py               # ✅ Bulk upsert functions
│
├── services/                 # ✅ NEW - Business logic
│   ├── __init__.py
│   └── pipeline_service.py   # ✅ DataFrame transformation + DB write
│
├── tasks/                    # ✅ NEW - Celery async
│   ├── __init__.py
│   ├── celery_app.py         # ✅ Celery configuration
│   └── pipeline_task.py      # ✅ Async task definition
│
├── downloader/               # Selenium scraper (existing)
├── processors/               # Data processing (existing)
├── exporters/                # CSV/Excel export (existing)
├── utils/                    # Helpers (existing)
├── input/                    # XLS input files
├── output/                   # CSV/Excel output
├── temp/                     # Intermediate files
└── logs/                     # App logs
```

---

## 🔧 Troubleshooting

| Problème | Solution |
|----------|----------|
| `ModuleNotFoundError: sqlalchemy` | `pip install -r requirements.txt` |
| `psycopg2: FATAL: database "pipeline_db" does not exist` | Créer la DB: `createdb -U postgres pipeline_db` |
| `Can't connect to Redis at localhost:6379` | Démarrer Redis: `docker run -d -p 6379:6379 redis:7` |
| `Celery worker ne reçoit pas les tasks` | Vérifier `CELERY_BROKER_URL` dans `.env` |
| `Task timeout` | Augmenter `CELERY_TASK_TIME_LIMIT` dans `.env` |

---

## 📚 Documentation des modules

- **`database/`**: SQLAlchemy ORM, modèles, opérations CRUD
- **`services/`**: Transformation DataFrame → Types DB, bulk upsert
- **`tasks/`**: Définition tasks Celery, coordination Selenium + processing
- **`run_pipeline.py`**: Launcher (async avec Celery vs sync)

---

## ✨ Résumé Actions À Faire

- [ ] `pip install -r requirements.txt`
- [ ] Créer `.env` (copie `.env.example`)
- [ ] Configurer `DATABASE_URL`, `CELERY_BROKER_URL`, `CELERY_RESULT_BACKEND`
- [ ] Docker: PostgreSQL + Redis
  ```bash
  docker run --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=pipeline_db -p 5432:5432 -d postgres:16
  docker run --name redis -p 6379:6379 -d redis:7
  ```
- [ ] Démarrer Celery worker: `celery -A tasks.celery_app worker --loglevel=info`
- [ ] Lancer pipeline: `python run_pipeline.py`
- [ ] Vérifier PostgreSQL: Check tables dans DB
- [ ] (Optionnel) FastAPI + Uvicorn pour API REST

---

## 🎓 Workflow en Production

1. **FastAPI reçoit** `POST /pipeline/run`
2. **FastAPI déclenche** `process_pipeline_task.delay()` (async)
3. **FastAPI retourne** immédiatement task_id + status
4. **Celery Worker** (separate process) télécharge → traite → stocke
5. **Client poll** `/pipeline/status/{task_id}` pour le progress
6. **Résultats** visibles dans PostgreSQL + fichiers CSV/Excel

---

**Besoin d'aide? Contacte-moi! 🚀**
