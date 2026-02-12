# AI-Based Conceptual Design Generator for Architects

Production-ready FastAPI backend for generating architectural designs using Stable Diffusion and ControlNet.

## Features

✅ **AI Design Generation**
- Text-to-Design generation using Stable Diffusion 2.1
- Sketch-to-Concept generation using ControlNet
- Climate-aware and orientation-optimized prompts

✅ **Environmental Analysis**
- Sun exposure estimation (0-100 score)
- Ventilation analysis and scoring
- Energy efficiency calculation
- Sustainability index with passive design factors

✅ **Compliance Validation**
- Minimum room area validation
- Window-to-wall ratio compliance (≥15%)
- Ventilation requirement checking
- Floor space index (FSI) validation
- Setback rule enforcement

✅ **Explainable AI**
- Design reasoning documentation
- Top influencing factors
- Environmental summary
- Optimization suggestions

✅ **Production Ready**
- Async FastAPI with proper error handling
- PostgreSQL with SQLAlchemy ORM
- JWT authentication with role-based access
- Docker & docker-compose support
- GPU inference optimization
- Comprehensive logging

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration management
│   ├── database.py          # Database setup & session
│   ├── models/
│   │   └── __init__.py      # SQLAlchemy models
│   ├── schemas/
│   │   └── __init__.py      # Pydantic schemas
│   ├── routes/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── users.py         # User management
│   │   ├── projects.py      # Project management
│   │   ├── designs.py       # Design generation
│   │   ├── environment.py   # Environmental analysis
│   │   ├── compliance.py    # Compliance validation
│   │   └── analytics.py     # Analytics endpoints
│   ├── services/
│   │   ├── user_service.py
│   │   └── project_service.py
│   ├── ai/
│   │   └── generator.py     # Stable Diffusion integration
│   ├── environmental/
│   │   └── analyzer.py      # Environmental analysis engine
│   ├── compliance/
│   │   └── validator.py     # Compliance rule engine
│   └── utils/
│       ├── auth.py          # Password & JWT utilities
│       ├── dependencies.py  # FastAPI dependencies
│       └── logger.py        # Logging setup
├── requirements.txt         # Python dependencies
├── Dockerfile              # Production Docker image
├── docker-compose.yml      # Multi-service orchestration
├── .env.example            # Environment variables template
└── README.md              # This file
```

## Architecture Highlights

### Database Models
- **User**: Authentication, roles, profile
- **Project**: Architectural projects with location & climate
- **PlotConfiguration**: Plot dimensions, setbacks, FSI
- **Design**: Generated designs with metadata
- **EnvironmentalMetrics**: Analysis results
- **ComplianceResult**: Validation results
- **Log**: Audit trail

### Environmental Analysis Engine
Calculates comprehensive sustainability metrics:
```
Energy Score = (0.4 × Sun Score) + (0.4 × Ventilation Score) + (0.2 × Orientation Factor)
Sustainability Index = (0.4 × Energy Score) + (0.3 × Natural Lighting %) + (0.3 × Passive Design Score)
```

### Compliance Validator
Validates against rules:
- Minimum room area ≥ 10m²
- Window-to-wall ratio ≥ 15%
- Ventilation score ≥ 50
- FSI ≤ 3.0
- Minimum setbacks ≥ 3m

### AI Generator
- Climate-aware prompt engineering
- Orientation-based design optimization
- Cultural style conditioning
- Seed-based reproducibility
- ControlNet for sketch-to-design conversion

## Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL 14+
- NVIDIA GPU (for CUDA, or use CPU mode)
- Docker & Docker Compose (optional)

### Local Setup

1. **Clone and setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

2. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your settings
```

3. **Create database**
```bash
# Using Docker PostgreSQL
docker run -d \
  --name arch_postgres \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=arch_design_db \
  -p 5432:5432 \
  postgres:16-alpine
```

4. **Run application**
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API available at: http://localhost:8000
Docs at: http://localhost:8000/docs

### Docker Deployment

1. **Build and run**
```bash
docker-compose up -d
```

2. **Initialize database**
```bash
docker-compose exec api alembic upgrade head
```

3. **Access services**
- API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin: http://localhost:5050

## API Endpoints

### Authentication
```
POST   /auth/register           - Register new user
POST   /auth/login              - Login (JWT token)
```

### Users
```
GET    /users/me                - Get current user profile
PUT    /users/me                - Update profile
DELETE /users/me                - Deactivate account
```

### Projects
```
POST   /projects/create         - Create project
GET    /projects/{id}           - Get project details
GET    /projects               - List user projects
PUT    /projects/{id}          - Update project
DELETE /projects/{id}          - Delete project
```

### Design Generation
```
POST   /design/generate         - Text-to-Design generation
POST   /design/generate-from-sketch - Sketch-to-Concept (ControlNet)
GET    /design/{id}            - Get design details
```

### Environmental Analysis
```
POST   /environment/analyze     - Run environmental analysis
GET    /environment/{id}/sustainability - Get sustainability index
```

### Compliance Validation
```
POST   /compliance/check        - Check compliance rules
GET    /compliance/{id}/status  - Get compliance status
```

### Analytics
```
GET    /analytics/summary       - User analytics summary
GET    /analytics/health        - Health check
```

## Example Workflows

### Workflow 1: Generate Design

```python
# 1. Register
POST /auth/register
{
  "email": "architect@example.com",
  "username": "architect1",
  "password": "securepassword123",
  "full_name": "John Architect"
}

# 2. Login
POST /auth/login
{
  "email": "architect@example.com",
  "password": "securepassword123"
}
# Returns: {"access_token": "...", "expires_in": 1800}

# 3. Create Project
POST /projects/create
{
  "name": "Residential Complex - Mumbai",
  "latitude": 19.0760,
  "longitude": 72.8777,
  "climate_zone": "tropical",
  "building_type": "residential",
  "orientation": 180,
  "plot_configuration": {
    "length": 50.0,
    "width": 40.0,
    "floor_limit": 5,
    "setbacks_north": 5.0,
    "setbacks_south": 5.0,
    "setbacks_east": 5.0,
    "setbacks_west": 5.0
  }
}
# Returns: project_id = 1

# 4. Generate Design
POST /design/generate
{
  "project_id": 1,
  "prompt": "Modern sustainable residential building with terraces and courtyards",
  "guidance_scale": 7.5,
  "num_inference_steps": 50
}
# Returns: design_id = 101

# 5. Analyze Environment
POST /environment/analyze
{
  "project_id": 1,
  "design_id": 101,
  "latitude": 19.0760,
  "orientation": 180,
  "window_ratio": 0.30,
  "window_to_wall_ratio": 0.20,
  "climate_zone": "tropical"
}
# Returns: sustainability_index = 78.5, energy_score = 75.0

# 6. Check Compliance
POST /compliance/check
{
  "project_id": 1,
  "design_id": 101
}
# Returns: compliance_status = true, violations = []
```

## Configuration

### AI Model Settings
```python
# config.py
MODEL_ID = "stabilityai/stable-diffusion-2.1"
CONTROLNET_MODEL_ID = "lllyasviel/sd-controlnet-canny"
DEVICE = "cuda"  # cuda or cpu
DTYPE = "float16"  # float16 or float32
ENABLE_ATTENTION_SLICING = True
ENABLE_MODEL_CPU_OFFLOAD = False
```

### Environmental Analysis Thresholds
```python
# environmental/analyzer.py
CLIMATE_CONFIGS = {
    "tropical": {"max_sunlight_hours": 10, "optimal_window_ratio": 0.20},
    "temperate": {"max_sunlight_hours": 8, "optimal_window_ratio": 0.25},
    "desert": {"max_sunlight_hours": 12, "optimal_window_ratio": 0.15},
    "cold": {"max_sunlight_hours": 6, "optimal_window_ratio": 0.30}
}
```

### Compliance Rules
```python
# compliance/validator.py
MINIMUM_ROOM_AREA = 10  # m²
MINIMUM_WINDOW_TO_WALL_RATIO = 0.15  # 15%
MINIMUM_VENTILATION_SCORE = 50  # 0-100
MAXIMUM_FSI = 3.0
MINIMUM_SETBACK = 3.0  # meters
```

## Performance Optimization

### GPU Inference
```python
# Settings for efficient GPU usage
DTYPE = "float16"  # Use half precision
ENABLE_ATTENTION_SLICING = True  # Reduce memory
ENABLE_MODEL_CPU_OFFLOAD = True  # Offload to CPU when not in use
```

### Database
- Connection pooling (20 connections, 40 overflow)
- Async queries with asyncpg
- Indexed on frequently queried columns
- Proper foreign key relationships

### API
- Async/await throughout
- Dependency injection for session management
- Request/response compression
- Caching headers where appropriate

## Security

✅ **Authentication & Authorization**
- JWT tokens with configurable expiration (default: 30 min)
- bcrypt password hashing (rounds: 12)
- Role-based access control (ADMIN, ARCHITECT, USER)

✅ **Database Security**
- SQL injection prevention via SQLAlchemy ORM/parameterized queries
- Prepared statements
- Connection SSL optional

✅ **API Security**
- CORS configuration
- Rate limiting ready
- Request validation via Pydantic
- Comprehensive error handling

## Logging

All activities logged to `logs/` directory:
- Application logs: `app_YYYYMMDD.log`
- Rotating handler (10MB per file, 5 backups)
- Debug level in development, Info in production

## Error Handling

Comprehensive error responses:
```json
{
  "detail": "Project not found"
}
```

HTTP Status Codes:
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Server Error

## Testing

Run tests (create conftest.py in tests/):
```bash
pytest tests/ -v --cov=app
```

## Deployment

### Production Checklist
- [ ] Change SECRET_KEY in .env
- [ ] Update CORS_ORIGINS
- [ ] Use strong DATABASE passwords
- [ ] Set DEBUG=false
- [ ] Use HTTPS/SSL
- [ ] Configure GPU memory limits
- [ ] Setup monitoring & alerting
- [ ] Configure backups

### Environment Variables Required
```
DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME
SECRET_KEY
DEVICE, DTYPE
DEBUG
```

## Technology Stack

- **Framework**: FastAPI 0.104.1
- **Server**: Uvicorn 0.24.0
- **Database**: PostgreSQL 16 + SQLAlchemy 2.0
- **AI**: Stable Diffusion, ControlNet, Diffusers
- **Auth**: JWT + bcrypt
- **Containerization**: Docker, Docker Compose
- **GPU**: NVIDIA CUDA 12.1

## License

Proprietary - Capstone Project

## Support

For issues or questions, contact the development team.
