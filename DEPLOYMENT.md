# EZCare Production Deployment

This document provides instructions for deploying the EZCare application in production using Docker Compose and Caddy reverse proxy.

## Architecture

The production setup consists of:

- **Frontend**: Vue.js application served by Nginx (accessible at `localhost:8080`)
- **Backend**: Flask API with GraphQL (accessible at `localhost:5000`)
- **Database**: PostgreSQL 15
- **Reverse Proxy**: Caddy (handles routing and SSL termination)
- **Volumes**: Persistent storage for database, uploads, and Caddy configuration

## Prerequisites

Before deploying, ensure you have:

- Docker (version 20.10+)
- Docker Compose (version 2.0+)
- At least 2GB RAM available
- Ports 5000 and 8080 available

### Docker Permissions

If you get permission errors when running Docker commands, you have two options:

1. **Add your user to the docker group (recommended):**
   ```bash
   sudo usermod -aG docker $USER
   newgrp docker  # or log out and back in
   ```

2. **Use sudo (the scripts will detect this automatically):**
   The deployment and management scripts will automatically use `sudo` if needed.

## Quick Start

1. **Clone and navigate to the project:**
   ```bash
   cd /path/to/SE-Project
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env file with your production values
   nano .env
   ```

3. **Deploy the application:**
   ```bash
   ./deploy.sh
   ```

4. **Access the application:**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:5000
   - GraphQL Playground: http://localhost:5000/graphql

## Environment Configuration

Update the `.env` file with your production values:

```env
# Database Configuration
POSTGRES_DB=ezcare
POSTGRES_USER=ezcare_user
POSTGRES_PASSWORD=your_secure_password_here

# Backend Configuration
SECRET_KEY=your_random_secret_key_here
JWT_SECRET_KEY=your_random_jwt_secret_here
SQLALCHEMY_DATABASE_URI=postgresql://ezcare_user:your_secure_password_here@db:5432/ezcare

# Frontend Configuration
FRONTEND_BASE_URL=http://localhost:8080

# AI Configuration
AI_API_KEY=your_openai_api_key_here
```

## Manual Deployment

If you prefer to deploy manually:

1. **Build the images:**
   ```bash
   docker-compose build
   ```

2. **Start the services:**
   ```bash
   docker-compose up -d
   ```

3. **Check service status:**
   ```bash
   docker-compose ps
   ```

## Service Management

### View logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f db
docker-compose logs -f caddy
```

### Restart services
```bash
# All services
docker-compose restart

# Specific service
docker-compose restart backend
```

### Stop services
```bash
docker-compose down
```

### Update services
```bash
# Pull latest changes and rebuild
git pull
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

## Database Management

### Access PostgreSQL
```bash
docker-compose exec db psql -U ezcare_user -d ezcare
```

### Backup database
```bash
docker-compose exec db pg_dump -U ezcare_user ezcare > backup_$(date +%Y%m%d_%H%M%S).sql
```

### Restore database
```bash
docker-compose exec -T db psql -U ezcare_user -d ezcare < backup.sql
```

## Monitoring and Health Checks

### Check service health
```bash
# Backend health check
curl http://localhost:5000/health

# Frontend health check
curl http://localhost:8080
```

### Monitor resource usage
```bash
docker stats
```

### Check service status
```bash
docker-compose ps
```

## Troubleshooting

### Common Issues

1. **Port conflicts:**
   - Ensure ports 5000 and 8080 are not in use
   - Check with: `netstat -tulpn | grep -E ':(5000|8080)'`

2. **Database connection issues:**
   - Check database logs: `docker-compose logs db`
   - Verify environment variables in `.env`

3. **Frontend build failures:**
   - Check Node.js version compatibility
   - Clear node_modules: `docker-compose build --no-cache frontend`

4. **Backend startup issues:**
   - Check Python dependencies in requirements.txt
   - Verify database connection string

### Debug Mode

To run services in debug mode:

```bash
# Stop current services
docker-compose down

# Start with debug output
docker-compose up
```

## Security Considerations

For production deployment:

1. **Change default passwords** in `.env`
2. **Use strong secret keys** for JWT and Flask sessions
3. **Configure SSL/HTTPS** through Caddy
4. **Set up proper firewall rules**
5. **Regular security updates** for Docker images
6. **Monitor logs** for suspicious activity

## Backup Strategy

### Automated backups
Create a cron job for regular backups:

```bash
# Add to crontab (crontab -e)
0 2 * * * cd /path/to/SE-Project && docker-compose exec -T db pg_dump -U ezcare_user ezcare > backups/backup_$(date +\%Y\%m\%d).sql
```

### File backups
Important directories to backup:
- `backend/chroma_db/` - Vector database
- `backend/static/uploads/` - User uploads
- `.env` - Environment configuration

## Performance Optimization

### For production environments:

1. **Increase worker processes** in Gunicorn (backend Dockerfile)
2. **Configure Nginx caching** for static assets
3. **Set up CDN** for static content
4. **Database indexing** and optimization
5. **Monitor memory usage** and adjust container limits

## Support

For issues and questions:
- Check the logs: `docker-compose logs -f`
- Review the troubleshooting section above
- Submit issues to the project repository
