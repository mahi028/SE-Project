# EZCare Docker Production Setup

Complete Docker-based production deployment for EZCare Senior Care Management System.

## 🏗️ Architecture

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│             │    │             │    │             │
│   Caddy     │    │  Frontend   │    │   Backend   │
│ Port: 8080  │───▶│   (Nginx)   │    │  (Flask)    │
│ Port: 5000  │    │             │    │ Port: 5000  │
│             │    └─────────────┘    └─────────────┘
└─────────────┘                              │
       │                                     │
       │                              ┌─────────────┐
       │                              │             │
       └──────────────────────────────│ PostgreSQL  │
                                      │ Port: 5432  │
                                      │             │
                                      └─────────────┘
```

## 🚀 Quick Start

1. **Setup environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your production values
   ```

2. **Deploy:**
   ```bash
   ./deploy.sh
   ```

3. **Access:**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:5000/graphql

## 🐳 Docker Permissions

If you need to run Docker commands with `sudo`, the scripts will automatically detect this and use `sudo` when necessary. However, for better security and convenience, you can add your user to the docker group:

```bash
# Add your user to the docker group
sudo usermod -aG docker $USER

# Apply the group membership (or log out and back in)
newgrp docker

# Test Docker access
docker ps
```

If you prefer to use the helper script for common Docker operations:
```bash
./docker-helper.sh up        # Start services
./docker-helper.sh logs      # View logs  
./docker-helper.sh down      # Stop services
```

## 📋 Services

### Frontend (Vue.js + Nginx)
- **Container**: `ezcare_frontend`
- **Technology**: Vue.js 3, PrimeVue, Vite
- **Server**: Nginx Alpine
- **Port**: 8080 (via Caddy proxy)

### Backend (Flask + Gunicorn)
- **Container**: `ezcare_backend`
- **Technology**: Flask, GraphQL, SQLAlchemy
- **Server**: Gunicorn with 4 workers
- **Port**: 5000 (via Caddy proxy)

### Database (PostgreSQL)
- **Container**: `ezcare_db`
- **Technology**: PostgreSQL 15 Alpine
- **Port**: 5432 (internal)
- **Persistent**: Volume `postgres_data`

### Reverse Proxy (Caddy)
- **Container**: `ezcare_caddy`
- **Technology**: Caddy 2 Alpine
- **Ports**: 8080 (frontend), 5000 (backend)
- **Features**: Automatic HTTPS, CORS handling

## 🔧 Management Commands

### Service Management
```bash
# Start all services
docker-compose up -d

# Stop all services
docker-compose down

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f backend

# Check service status
docker-compose ps
```

### Database Management
```bash
# Initialize database
./db-setup.sh init

# Run migrations
./db-setup.sh migrate

# Reset database (⚠️ destroys data)
./db-setup.sh reset

# Database backup
docker-compose exec db pg_dump -U ezcare_user ezcare > backup.sql

# Database restore
docker-compose exec -T db psql -U ezcare_user -d ezcare < backup.sql
```

### Development Mode
```bash
# Run in development mode with hot reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Access development services:
# - Frontend dev server: http://localhost:3000
# - Backend dev server: http://localhost:5001
# - MailHog UI: http://localhost:8025
```

## 🔐 Environment Configuration

### Required Environment Variables

```env
# Database
POSTGRES_DB=ezcare
POSTGRES_USER=ezcare_user
POSTGRES_PASSWORD=your_secure_password

# Backend Security
SECRET_KEY=your_32_character_secret_key
JWT_SECRET_KEY=your_jwt_secret_key

# External Services
AI_API_KEY=your_openai_api_key
MAIL_SERVER=localhost
MAIL_PORT=1025

# URLs
FRONTEND_BASE_URL=http://localhost:8080
```

### Security Best Practices

1. **Generate secure keys:**
   ```bash
   # Generate SECRET_KEY
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   
   # Generate JWT_SECRET_KEY
   openssl rand -hex 32
   ```

2. **Use strong database passwords**
3. **Keep .env file secure and never commit it**

## 🐛 Troubleshooting

### Common Issues

1. **Port conflicts:**
   ```bash
   # Check if ports are in use
   netstat -tulpn | grep -E ':(5000|8080)'
   
   # Solution: Stop conflicting services or change ports
   ```

2. **Database connection failed:**
   ```bash
   # Check database logs
   docker-compose logs db
   
   # Verify database is running
   docker-compose exec db pg_isready -U ezcare_user
   ```

3. **Frontend build failed:**
   ```bash
   # Rebuild without cache
   docker-compose build --no-cache frontend
   
   # Check build logs
   docker-compose logs frontend
   ```

4. **Backend startup issues:**
   ```bash
   # Check backend logs
   docker-compose logs backend
   
   # Test database connection
   docker-compose exec backend python -c "
   from app import create_app
   app = create_app()
   print('Backend started successfully')
   "
   ```

### Health Checks

```bash
# Backend health
curl http://localhost:5000/health

# Frontend health
curl http://localhost:8080

# Database health
docker-compose exec db pg_isready -U ezcare_user -d ezcare

# All services status
docker-compose ps
```

## 📊 Monitoring

### Resource Usage
```bash
# Monitor container resources
docker stats

# Check disk usage
docker system df

# View container processes
docker-compose top
```

### Log Management
```bash
# Follow logs for all services
docker-compose logs -f

# View logs for specific timeframe
docker-compose logs --since="1h" backend

# Save logs to file
docker-compose logs backend > backend.log
```

## 🚀 Production Deployment

### Server Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 20GB minimum, SSD recommended
- **Network**: Stable internet connection

### Production Optimizations

1. **Enable SSL/TLS with Caddy:**
   ```caddyfile
   your-domain.com {
       reverse_proxy frontend:80
   }
   
   api.your-domain.com {
       reverse_proxy backend:5000
   }
   ```

2. **Configure firewall:**
   ```bash
   # Only allow necessary ports
   ufw allow 22    # SSH
   ufw allow 80    # HTTP
   ufw allow 443   # HTTPS
   ufw enable
   ```

3. **Set up automated backups:**
   ```bash
   # Add to crontab
   0 2 * * * cd /path/to/project && docker-compose exec -T db pg_dump -U ezcare_user ezcare > backups/backup_$(date +\%Y\%m\%d).sql
   ```

### Scaling

For higher load, consider:

1. **Backend scaling:**
   ```yaml
   backend:
     deploy:
       replicas: 3
   ```

2. **Database optimization:**
   - Connection pooling
   - Read replicas
   - Query optimization

3. **CDN for static assets**
4. **Load balancer for multiple instances**

## 🧪 Testing

### Run Tests in Containers
```bash
# Backend tests
docker-compose exec backend python -m pytest tests/

# Frontend tests (if available)
docker-compose exec frontend npm test

# Integration tests
curl -X POST http://localhost:5000/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'
```

## 📝 File Structure

```
SE-Project/
├── docker-compose.yml          # Main compose file
├── docker-compose.dev.yml      # Development overrides
├── Caddyfile                   # Proxy configuration
├── deploy.sh                   # Deployment script
├── db-setup.sh                 # Database management
├── .env.example                # Environment template
├── DEPLOYMENT.md               # This documentation
│
├── backend/
│   ├── Dockerfile              # Backend container
│   ├── .dockerignore          # Build exclusions
│   ├── requirements.txt        # Python dependencies
│   └── ...
│
└── frontend/
    ├── Dockerfile              # Frontend container
    ├── .dockerignore          # Build exclusions
    ├── nginx.conf             # Nginx configuration
    └── ...
```

## 🤝 Contributing

1. Make changes to source code
2. Test locally with development compose
3. Update documentation if needed
4. Submit pull request

## 📞 Support

For deployment issues:
1. Check the logs: `docker-compose logs -f [service]`
2. Review this documentation
3. Check common issues in troubleshooting section
4. Submit issue with logs and environment details
