# EZCare Senior Care Management System - Implementation Guide

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Technologies and Tools](#technologies-and-tools)
3. [Prerequisites](#prerequisites)
4. [Installation & Setup](#installation--setup)
5. [Running the Application](#running-the-application)
6. [Application Architecture](#application-architecture)
7. [API Documentation](#api-documentation)
8. [Troubleshooting](#troubleshooting)
9. [Development Workflow](#development-workflow)

---

## 🏥 Project Overview

EZCare is a comprehensive Senior Care Management System designed to facilitate healthcare coordination between seniors, doctors, and caregivers. The platform provides appointment scheduling, vital signs monitoring, prescription management, and AI-powered health insights.

---

## 🛠 Technologies and Tools

### **Frontend Technologies**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Vue.js** | 3.x | Progressive JavaScript framework |
| **Vite** | Latest | Fast build tool and development server |
| **PrimeVue** | Latest | UI component library |
| **Apollo Client** | 3.x | GraphQL client |
| **Tailwind CSS** | Latest | Utility-first CSS framework |
| **SCSS** | Latest | CSS preprocessor |
| **Axios** | Latest | HTTP client for REST APIs |

### **Backend Technologies**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.12 | Backend programming language |
| **Flask** | Latest | Lightweight web framework |
| **GraphQL** | Latest | Query language and API runtime |
| **Graphene** | Latest | GraphQL framework for Python |
| **SQLAlchemy** | Latest | ORM for database operations |
| **PostgreSQL** | 15 | Primary relational database |
| **ChromaDB** | Latest | Vector database for AI embeddings |
| **InsightFace** | Latest | AI face recognition library |
| **Gunicorn** | Latest | WSGI HTTP server |
| **Flask-JWT-Extended** | Latest | JWT authentication |
| **Flask-CORS** | Latest | Cross-origin resource sharing |
| **APScheduler** | Latest | Background task scheduling |

### **DevOps & Infrastructure**
| Technology | Version | Purpose |
|------------|---------|---------|
| **Docker** | Latest | Containerization platform |
| **Docker Compose** | 2.x | Multi-container orchestration |
| **Caddy** | 2.x | Reverse proxy and load balancer |
| **Nginx** | Alpine | Web server for frontend |
| **GitHub** | - | Version control and CI/CD |

### **AI & Machine Learning**
| Technology | Version | Purpose |
|------------|---------|---------|
| **InsightFace** | Latest | Facial recognition and analysis |
| **ONNX Runtime** | Latest | AI model inference |
| **ChromaDB** | Latest | Vector similarity search |
| **NumPy** | Latest | Numerical computing |
| **OpenCV** | Latest | Computer vision processing |

---

## 📋 Prerequisites

### **System Requirements**
- **Operating System**: Linux, macOS, or Windows 10/11
- **RAM**: Minimum 8GB (16GB recommended for AI features)
- **Storage**: At least 10GB free space
- **Internet**: Stable connection for dependencies and AI models

### **Required Software**

#### 1. **Docker & Docker Compose**
```bash
# Install Docker (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group (avoid sudo)
sudo usermod -aG docker $USER
newgrp docker

# Verify installation
docker --version
docker compose version
```

#### 2. **Git** (for cloning repository)
```bash
# Ubuntu/Debian
sudo apt update && sudo apt install git

# Verify installation
git --version
```

#### 3. **Optional: Node.js & Python** (for local development)
```bash
# Node.js (for frontend development)
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Python (for backend development)
sudo apt update && sudo apt install python3.12 python3.12-pip python3.12-venv
```

---

## 🚀 Installation & Setup

### **Step 1: Clone the Repository**
```bash
git clone https://github.com/mahi028/SE-Project.git
cd SE-Project
```

### **Step 2: Environment Configuration**
```bash
# Create environment file (if not exists)
cp .env.example .env

# Edit environment variables
nano .env
```

**Required Environment Variables:**
```env
# Database Configuration
POSTGRES_DB=ezcare
POSTGRES_USER=ezcare_user
POSTGRES_PASSWORD=your_secure_password_here

# Security Keys
SECRET_KEY=your_super_secret_key_change_in_production
JWT_SECRET_KEY=your_jwt_secret_key_change_in_production

# Application URLs
FRONTEND_BASE_URL=http://localhost:8080
BACKEND_BASE_URL=http://localhost:5000

# Email Configuration (optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### **Step 3: Make Scripts Executable**
```bash
chmod +x deploy.sh health-check.sh
```

---

## 🎯 Running the Application

### **Production Deployment (Recommended)**

#### **Quick Start**
```bash
# Deploy all services with a single command
./deploy.sh
```

#### **Manual Deployment Steps**
```bash
# 1. Build Docker images
docker compose build

# 2. Start all services
docker compose up -d

# 3. Check service health
./health-check.sh
```

### **Development Mode**

#### **Backend Development**
```bash
cd backend

# Create virtual environment
python3.12 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
export FLASK_ENV=development
python run.py
```

#### **Frontend Development**
```bash
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### **Service Access Points**
| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:8080 | Main application interface |
| **Backend API** | http://localhost:5000 | REST API endpoints |
| **GraphQL Playground** | http://localhost:5000/graphql | Interactive GraphQL interface |
| **Database** | localhost:5433 | PostgreSQL (external port) |

---

## 🏗 Application Architecture

### **System Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Caddy Proxy   │    │   Backend       │
│   (Vue.js)      │◄──►│   (Reverse      │◄──►│   (Flask +      │
│   Port: 8080    │    │   Proxy)        │    │   GraphQL)      │
└─────────────────┘    └─────────────────┘    │   Port: 5000    │
                                              └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │   PostgreSQL    │
                                              │   Database      │
                                              │   Port: 5432    │
                                              └─────────────────┘
                                                       │
                                              ┌─────────────────┐
                                              │   ChromaDB      │
                                              │   (Vector DB)   │
                                              └─────────────────┘
```

### **Container Architecture**
- **ezcare_frontend**: Nginx serving Vue.js SPA
- **ezcare_backend**: Gunicorn WSGI server with Flask
- **ezcare_db**: PostgreSQL database with persistent storage
- **ezcare_caddy**: Caddy reverse proxy handling routing

### **Data Flow**
1. **User Request** → Caddy Proxy → Nginx (Frontend)
2. **API Calls** → Caddy Proxy → Flask Backend
3. **Database Operations** → SQLAlchemy ORM → PostgreSQL
4. **AI Processing** → InsightFace Models → ChromaDB

---

## 📚 API Documentation

### **GraphQL Schema**
Access the interactive GraphQL playground at: http://localhost:5000/graphql

### **Key GraphQL Operations**

#### **Authentication**
```graphql
# Login
mutation {
  login(username: "user@example.com", password: "password") {
    token
    user {
      id
      email
      userType
    }
  }
}
```

#### **User Management**
```graphql
# Get user profile
query {
  user(id: "123") {
    id
    email
    profile {
      firstName
      lastName
      dateOfBirth
    }
  }
}
```

#### **Appointments**
```graphql
# Create appointment
mutation {
  createAppointment(
    doctorId: "doc123"
    patientId: "patient123"
    dateTime: "2025-08-15T10:00:00Z"
    notes: "Regular checkup"
  ) {
    id
    status
    dateTime
  }
}
```

### **REST API Endpoints**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Service health check |
| POST | `/user-lookup/register` | User's Face Embeddings registeration |
| POST | `/user-lookup/recognize` | Get user profile |

---

## 🔧 Management Commands

### **Container Management**
```bash
# View running containers
docker compose ps

# View service logs
docker compose logs -f [service_name]

# Restart specific service
docker compose restart [service_name]

# Stop all services
docker compose down

# Remove everything (including volumes)
docker compose down --volumes --remove-orphans
```

### **Database Management**
```bash
# Access PostgreSQL shell
docker compose exec db psql -U ezcare_user -d ezcare

# Create database backup
docker compose exec db pg_dump -U ezcare_user ezcare > backup.sql

# Restore database
docker compose exec -T db psql -U ezcare_user -d ezcare < backup.sql
```

### **Health Monitoring**
```bash
# Run comprehensive health check
./health-check.sh

# Check specific service health
curl http://localhost:5000/health
curl http://localhost:8080

# Monitor resource usage
docker stats
```

---

## 🚨 Troubleshooting

### **Common Issues**

#### **Port Conflicts**
```bash
# Check if ports are in use
netstat -tulpn | grep :8080
netstat -tulpn | grep :5000

# Kill processes using ports
sudo fuser -k 8080/tcp
sudo fuser -k 5000/tcp
```

#### **Docker Permission Issues**
```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo with docker commands
sudo docker compose up -d
```

#### **Database Connection Issues**
```bash
# Check database logs
docker compose logs db

# Verify database is running
docker compose exec db pg_isready -U ezcare_user -d ezcare
```

#### **ChromaDB Permission Issues**
```bash
# Reset ChromaDB volume
docker compose down --volumes
docker volume rm se-project_chroma_data
docker compose up -d
```

### **Performance Optimization**

#### **Memory Usage**
- Minimum 8GB RAM recommended
- Monitor with `docker stats`
- Adjust worker processes in `backend/Dockerfile`

#### **Storage Cleanup**
```bash
# Remove unused Docker resources
docker system prune -a

# Remove unused volumes
docker volume prune
```

---

## 👨‍💻 Development Workflow

### **Local Development Setup**
1. Clone repository and checkout development branch
2. Set up local environment variables
3. Run backend and frontend separately for hot-reload
4. Use GraphQL playground for API testing

### **Code Style & Standards**
- **Frontend**: ESLint + Prettier configuration
- **Backend**: PEP 8 Python style guide
- **Commits**: Conventional commit messages

### **Testing**
```bash
# Backend tests
cd backend
python -m pytest tests/
```

### **Building for Production**
```bash
# Build optimized Docker images
docker compose build --no-cache

# Deploy to production
./deploy.sh
```

---

## 📊 Monitoring & Logs

### **Application Logs**
```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### **Health Monitoring**
- Automated health checks every 30 seconds
- Service restart policies configured
- Comprehensive health check script available

### **Performance Metrics**
```bash
# Resource usage
docker stats

# Service status
docker compose ps
```

---

## 🔐 Security Considerations

### **Production Security**
- Change all default passwords and secret keys
- Use HTTPS in production with proper SSL certificates
- Implement proper CORS policies
- Regular security updates for dependencies
- Database connection encryption

### **Authentication & Authorization**
- JWT-based authentication
- Role-based access control (Senior, Doctor, Admin)
- Session management and token expiration

---

## 📝 License & Support

This project is exclusively built as a pre-requisite for Software Engineering Course for IIT-Madras by Team 6 | May'2025. For support or questions, please refer to the project documentation or create an issue in the repository.

---

## 👥 Contributors

| Name | Role in Project | Roll Number |
|------|-----------------|-------------|
| **Mohit Tewari** | Frontend, Backend, API Integration, Project Design, Code Documentation | 23f1002364 |
| **Akhileshwer Pandey** | Project Manager, Backend, Testing | 21f3002866 |
| **Dev Gupta** | Backend, Project Documentation | 22f2000888 |
| **Rashi Singal** | Frontend, Project Documentation | 21f1005286 |
| **Affan Bin Nishat** | Testing | 21f1003441 |
| **Ajay Sharma** | Frontend | 21f1005414 |
| **Ambuj Pratap** | Frontend | 22f3002778 |

---

**Last Updated**: August 10, 2025  
**Version**: 1.0.0  
**Maintainer**: EZCare Development Team
