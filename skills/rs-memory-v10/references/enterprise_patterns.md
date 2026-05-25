# RS Enterprise Patterns — Scalable Architecture

Every tool RS builds should be designed to scale from personal use to enterprise deployment. This reference provides patterns for building scalable, maintainable, and professional-grade tools.

---

## SCALABILITY TIERS

| Tier | Users | Data | Architecture | Database |
|------|-------|------|--------------|----------|
| **Personal** | 1 | MB | Single file | SQLite |
| **Team** | 1-50 | GB | Multi-module | PostgreSQL |
| **Enterprise** | 50-1000 | TB | Microservices | PostgreSQL + Redis |
| **SaaS** | 1000+ | PB | Cloud-native | Distributed |

---

## ARCHITECTURE PATTERNS

### Pattern 1: Modular Monolith (Personal → Team)

```
tool-name/
├── main.py              # Entry point
├── config.py            # Configuration management
├── core/
│   ├── __init__.py
│   ├── engine.py        # Core processing engine
│   └── models.py        # Data models
├── modules/
│   ├── __init__.py
│   ├── scanner.py       # Scanner module
│   ├── reporter.py      # Reporter module
│   └── exporter.py      # Export module
├── utils/
│   ├── __init__.py
│   ├── helpers.py       # Helper functions
│   └── validators.py    # Input validation
├── output/              # Output directory
├── logs/                # Log files
├── requirements.txt
└── README.md
```

**Advantages:**
- Easy to develop and debug
- Single deployment unit
- Can be split into microservices later

---

### Pattern 2: Microservices (Enterprise)

```
tool-platform/
├── api-gateway/         # API Gateway (FastAPI/Express)
│   ├── main.py
│   └── routes/
├── scanner-service/     # Scanner microservice
│   ├── main.py
│   └── scanner/
├── processor-service/   # Processing microservice
│   ├── main.py
│   └── processor/
├── report-service/      # Report generation
│   ├── main.py
│   └── templates/
├── shared/
│   ├── models.py        # Shared data models
│   └── utils.py         # Shared utilities
├── docker-compose.yml   # Container orchestration
└── kubernetes/          # K8s deployment files
```

**Docker Compose:**
```yaml
version: '3.8'
services:
  api-gateway:
    build: ./api-gateway
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/tools
      - REDIS_URL=redis://redis:6379
  
  scanner-service:
    build: ./scanner-service
    environment:
      - REDIS_URL=redis://redis:6379
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=tools
    volumes:
      - pgdata:/var/lib/postgresql/data
  
  redis:
    image: redis:7
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

---

### Pattern 3: Cloud-Native (SaaS)

```
tool-saas/
├── frontend/            # Next.js frontend
│   ├── app/
│   ├── components/
│   └── lib/
├── backend/             # API backend
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   └── models/
│   └── workers/         # Background workers
├── infrastructure/
│   ├── terraform/       # IaC
│   ├── kubernetes/      # K8s manifests
│   └── docker/          # Dockerfiles
├── shared/
│   └── types/           # Shared TypeScript types
└── scripts/
    └── deploy.sh
```

**Kubernetes Deployment:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: tool-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: tool-api
  template:
    metadata:
      labels:
        app: tool-api
    spec:
      containers:
      - name: api
        image: tool-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: tool-secrets
              key: database-url
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
---
apiVersion: v1
kind: Service
metadata:
  name: tool-api-service
spec:
  selector:
    app: tool-api
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

---

## DATABASE PATTERNS

### SQLite → PostgreSQL Compatible

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
import os

def get_database_url():
    """Get database URL based on environment."""
    # Production: PostgreSQL
    if os.environ.get("DATABASE_URL"):
        return os.environ["DATABASE_URL"]
    
    # Development: SQLite
    db_path = Path.home() / ".rs-tools" / "data" / "tools.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{db_path}"

# Works with both SQLite and PostgreSQL
engine = create_engine(get_database_url(), echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Models work with both
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Scan(Base):
    __tablename__ = "scans"
    
    id = Column(Integer, primary_key=True, index=True)
    target = Column(String, index=True)
    status = Column(String)
    created_at = Column(DateTime)
    results = Column(String)  # JSON string
```

---

### Database Migration (Alembic)

```bash
# Initialize Alembic
alembic init migrations

# Create migration
alembic revision --autogenerate -m "Initial migration"

# Apply migrations
alembic upgrade head
```

---

## API PATTERNS

### RESTful API (FastAPI)

```python
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
import uuid

app = FastAPI(title="[Tool Name] API", version="1.0.0")

# Models
class ScanRequest(BaseModel):
    target: str
    options: Optional[dict] = {}

class ScanResult(BaseModel):
    id: str
    target: str
    status: str
    results: Optional[dict] = None

# In-memory storage (use database in production)
scans = {}

# Endpoints
@app.post("/api/scan", response_model=ScanResult)
async def create_scan(request: ScanRequest, background_tasks: BackgroundTasks):
    scan_id = str(uuid.uuid4())
    scans[scan_id] = {
        "id": scan_id,
        "target": request.target,
        "status": "pending",
        "results": None
    }
    
    # Run scan in background
    background_tasks.add_task(run_scan, scan_id, request.target, request.options)
    
    return scans[scan_id]

@app.get("/api/scan/{scan_id}", response_model=ScanResult)
async def get_scan(scan_id: str):
    if scan_id not in scans:
        raise HTTPException(status_code=404, detail="Scan not found")
    return scans[scan_id]

@app.get("/api/scans", response_model=List[ScanResult])
async def list_scans():
    return list(scans.values())

async def run_scan(scan_id: str, target: str, options: dict):
    """Background task to run scan."""
    scans[scan_id]["status"] = "running"
    
    # Perform scan
    results = perform_scan(target, options)
    
    scans[scan_id]["status"] = "completed"
    scans[scan_id]["results"] = results
```

---

### API Authentication

```python
from fastapi import Depends, HTTPException, Header
from typing import Optional

async def get_api_key(api_key: Optional[str] = Header(None)):
    """Validate API key."""
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    # Validate against database
    valid_keys = get_valid_api_keys()  # Implement this
    if api_key not in valid_keys:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    return api_key

@app.get("/api/protected")
async def protected_endpoint(api_key: str = Depends(get_api_key)):
    return {"message": "Access granted"}
```

---

## BACKGROUND PROCESSING

### Celery + Redis

```python
# tasks.py
from celery import Celery
import time

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def run_scan_task(target, options):
    """Background scan task."""
    # Long-running scan logic
    time.sleep(60)  # Simulate work
    return {"target": target, "status": "completed"}

# API endpoint
@app.post("/api/scan")
async def create_scan(request: ScanRequest):
    task = run_scan_task.delay(request.target, request.options)
    return {"task_id": task.id, "status": "pending"}

@app.get("/api/scan/{task_id}")
async def get_scan_status(task_id: str):
    task = run_scan_task.AsyncResult(task_id)
    return {
        "task_id": task_id,
        "status": task.status,
        "result": task.result if task.ready() else None
    }
```

---

## CACHING

### Redis Caching

```python
import redis
import json
from functools import wraps

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(ttl=3600):
    """Cache decorator for function results."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache
            cached = redis_client.get(key)
            if cached:
                return json.loads(cached)
            
            # Execute function
            result = func(*args, **kwargs)
            
            # Cache result
            redis_client.setex(key, ttl, json.dumps(result))
            
            return result
        return wrapper
    return decorator

@cache_result(ttl=300)
def expensive_operation(target):
    # Expensive operation
    return {"result": "data"}
```

---

## MONITORING & LOGGING

### Structured Logging

```python
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        return json.dumps(log_data)

# Setup
logger = logging.getLogger("tool-name")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info("Scan started", extra={"target": "example.com"})
```

---

### Prometheus Metrics

```python
from prometheus_client import Counter, Histogram, start_http_server
import time

# Metrics
scans_total = Counter('scans_total', 'Total number of scans')
scans_duration = Histogram('scan_duration_seconds', 'Time spent scanning')
active_scans = Counter('active_scans', 'Currently active scans')

# Start metrics server
start_http_server(9090)

# Use in code
@scans_duration.time()
def perform_scan(target):
    scans_total.inc()
    active_scans.inc()
    
    # Scan logic
    time.sleep(5)
    
    active_scans.dec()
    return {"status": "completed"}
```

---

## SECURITY PATTERNS

### Input Validation

```python
from pydantic import BaseModel, validator, constr
from typing import List
import re

class ScanRequest(BaseModel):
    target: constr(min_length=1, max_length=255)
    ports: List[int] = []
    
    @validator('target')
    def validate_target(cls, v):
        # Validate domain or IP
        domain_pattern = r'^[a-zA-Z0-9][-a-zA-Z0-9]{0,62}(\.[a-zA-Z0-9][-a-zA-Z0-9]{0,62})+$'
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        
        if not (re.match(domain_pattern, v) or re.match(ip_pattern, v)):
            raise ValueError('Invalid target format')
        return v
    
    @validator('ports')
    def validate_ports(cls, v):
        for port in v:
            if not 1 <= port <= 65535:
                raise ValueError(f'Invalid port: {port}')
        return v
```

### Rate Limiting

```python
from fastapi import Request, HTTPException
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/scan")
@limiter.limit("10/minute")
async def scan_endpoint(request: Request):
    # Limited to 10 requests per minute per IP
    return {"status": "ok"}
```

---

## DEPLOYMENT CHECKLIST

### Production Readiness

- [ ] Environment variables for all secrets
- [ ] Database migrations automated
- [ ] Logging to structured format
- [ ] Metrics endpoint exposed
- [ ] Health check endpoint
- [ ] Rate limiting enabled
- [ ] Input validation on all endpoints
- [ ] Authentication required for sensitive endpoints
- [ ] CORS configured correctly
- [ ] SSL/TLS enabled
- [ ] Backup strategy defined
- [ ] Monitoring alerts configured
- [ ] Error tracking (Sentry)
- [ ] Load testing completed
- [ ] Documentation updated

### Health Check Endpoint

```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health/ready")
async def readiness_check():
    # Check database
    try:
        db.execute("SELECT 1")
        db_healthy = True
    except:
        db_healthy = False
    
    # Check Redis
    try:
        redis_client.ping()
        redis_healthy = True
    except:
        redis_healthy = False
    
    return {
        "database": "healthy" if db_healthy else "unhealthy",
        "redis": "healthy" if redis_healthy else "unhealthy",
        "status": "ready" if all([db_healthy, redis_healthy]) else "not_ready"
    }
```

---

## COST OPTIMIZATION

### Resource Sizing

| Scale | CPU | RAM | Storage | Est. Cost/month |
|-------|-----|-----|---------|-----------------|
| Personal | 1 vCPU | 1 GB | 10 GB | $5-10 |
| Team | 2 vCPU | 4 GB | 50 GB | $20-50 |
| Enterprise | 4+ vCPU | 16+ GB | 500 GB+ | $100-500 |
| SaaS | Auto-scale | Auto-scale | Distributed | Variable |

### Auto-Scaling (Kubernetes)

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: tool-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: tool-api
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```
