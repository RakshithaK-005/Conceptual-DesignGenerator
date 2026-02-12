# AI-Based Conceptual Design Generator for Architects

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12+-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

A full-stack AI-powered architectural design generator that uses **Stable Diffusion** and **ControlNet** to create conceptual designs from text descriptions or sketches. Features environmental analysis, compliance validation, and explainable AI for architects.

---

## Features

### AI Design Generation
- **Text-to-Design** - Generate architectural concepts from natural language descriptions using Stable Diffusion 2.1
- **Sketch-to-Concept** - Transform rough sketches into detailed designs using ControlNet
- **Climate-Aware Prompts** - Designs optimized for local climate and orientation

### Environmental Analysis
- **Sun Exposure Estimation** - Calculate sun exposure scores (0-100)
- **Ventilation Analysis** - Evaluate natural ventilation potential
- **Energy Efficiency** - Calculate comprehensive energy scores
- **Sustainability Index** - Factor in passive design elements

### Compliance Validation
- **Room Area Validation** - Minimum room area checks (≥10m²)
- **Window-to-Wall Ratio** - Ensure adequate natural lighting (≥15%)
- **Ventilation Requirements** - Check ventilation compliance
- **FSI Validation** - Floor Space Index compliance checking
- **Setback Rules** - Building setback enforcement

### Explainable AI
- **Design Reasoning** - Understand why the AI made specific choices
- **Influencing Factors** - See top factors affecting the design
- **Optimization Suggestions** - Get recommendations for improvements

### User Features
- **User Authentication** - Secure JWT-based login/registration
- **Project Management** - Organize designs into projects
- **Contact Form** - Built-in contact form with API backend
- **Responsive UI** - Works on mobile, tablet, and desktop

---

## Tech Stack

### Backend
- **FastAPI** - Modern async Python web framework
- **PostgreSQL** - Robust relational database
- **SQLAlchemy** - Async ORM with relationship support
- **Stable Diffusion 2.1** - AI image generation
- **ControlNet** - Sketch-to-image conditioning
- **PyTorch** - Deep learning framework
- **JWT Authentication** - Secure token-based auth

### Frontend
- **HTML5/CSS3** - Semantic markup with modern styling
- **Vanilla JavaScript** - No framework dependencies
- **Responsive Design** - Mobile-first approach
- **CSS Animations** - Smooth UI transitions

### DevOps
- **Docker & Docker Compose** - Containerized deployment
- **Multi-stage Builds** - Optimized production images
- **Health Checks** - Database connectivity monitoring

---

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/Conceptual-DesignGenerator.git
cd Conceptual-DesignGenerator

# Start all services
cd backend
docker-compose up -d

# Frontend is served at: http://localhost:80
# Backend API at: http://localhost:8000
# API Docs at: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Prerequisites
- Python 3.10+
- PostgreSQL 12+
- Node.js (optional, for live-server)

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials

# Start the server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend

# Using Python's built-in server
python -m http.server 8080

# Or using live-server (npm)
npx live-server --port=8080
```

**Visit**: http://localhost:8080

---

## Environment Variables

Create a `.env` file in the `backend/` directory:

```env
# API Configuration
API_TITLE=AI Architectural Design Generator
API_VERSION=1.0.0
DEBUG=True

# Database
DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=arch_design_db

# Security
SECRET_KEY=your-super-secret-key-change-in-production-min-32-chars

# AI Models
DEVICE=cpu          # Use 'cuda' for GPU
DTYPE=float32       # Use 'float16' on GPU for speed

# File Storage
UPLOAD_DIR=uploads
LOGS_DIR=logs
```

---

## API Documentation

Once the backend is running, access the interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | User login |
| GET | `/projects` | List user projects |
| POST | `/projects` | Create new project |
| POST | `/designs/generate` | Generate AI design |
| POST | `/designs/sketch-to-concept` | Convert sketch to design |
| POST | `/environment/analyze` | Analyze environmental factors |
| POST | `/compliance/validate` | Validate design compliance |
| GET | `/analytics/dashboard` | Get analytics data |

---

## Project Structure

```
Conceptual-DesignGenerator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   ├── routes/              # API endpoints
│   │   │   ├── auth.py          # Authentication
│   │   │   ├── users.py         # User management
│   │   │   ├── projects.py      # Project CRUD
│   │   │   ├── designs.py       # Design generation
│   │   │   ├── environment.py   # Environmental analysis
│   │   │   ├── compliance.py    # Compliance validation
│   │   │   └── analytics.py     # Analytics
│   │   ├── services/            # Business logic
│   │   ├── ai/                  # AI model integration
│   │   │   └── generator.py     # Stable Diffusion wrapper
│   │   ├── environmental/       # Environmental analysis
│   │   │   └── analyzer.py      # Analysis engine
│   │   ├── compliance/          # Compliance checking
│   │   │   └── validator.py     # Rule engine
│   │   └── utils/               # Utilities
│   ├── tests/                   # Test suite
│   ├── requirements.txt         # Python dependencies
│   ├── Dockerfile              # Production image
│   └── docker-compose.yml      # Multi-service setup
│
├── frontend/
│   ├── index.html              # Home page
│   ├── login.html              # Authentication page
│   ├── contact.html            # Contact form
│   ├── generate.html           # Design generation UI
│   ├── css/
│   │   └── styles.css          # Styling
│   └── js/
│       └── script.js           # Frontend logic
│
├── QUICK_START.md              # Quick start guide
├── SETUP_AND_RUN.md            # Detailed setup instructions
├── TESTING_CHECKLIST.md        # Testing guide
└── README.md                   # This file
```

---

## Screenshots

<details>
<summary>Click to view screenshots</summary>

### Home Page
![Home Page](docs/screenshots/home.png)

### Design Generation
![Design Generation](docs/screenshots/generate.png)

### Environmental Analysis
![Environmental Analysis](docs/screenshots/analysis.png)

</details>

---

## Development

### Running Tests

```bash
cd backend
pytest tests/ -v
```

### Code Quality

```bash
# Install dev dependencies
pip install black flake8 mypy

# Format code
black app/

# Lint
flake8 app/

# Type check
mypy app/
```

---

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgements

- [Stable Diffusion](https://github.com/CompVis/stable-diffusion) - Foundation AI model
- [ControlNet](https://github.com/lllyasviel/ControlNet) - Sketch conditioning
- [FastAPI](https://fastapi.tiangolo.com) - Web framework
- [Hugging Face Diffusers](https://github.com/huggingface/diffusers) - Diffusion model library

---

## Contact

For questions or support, please open an issue or use the contact form in the application.
