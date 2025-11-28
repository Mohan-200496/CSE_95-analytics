#!/bin/bash

echo "🚀 Punjab Rozgar Portal - Production Deployment Setup"
echo "======================================================"

# Create production environment file
cat > .env.production << EOF
# Production Environment Configuration
ENVIRONMENT=production
DATABASE_URL=sqlite:///./punjab_rozgar.db
JWT_SECRET_KEY=your-super-secret-jwt-key-change-in-production
CORS_ORIGINS=["http://localhost:3000","https://yourdomain.com"]
DEBUG=False

# Email Configuration (Add your SMTP settings)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USER=your-email@gmail.com
EMAIL_PASSWORD=your-app-password

# Analytics
ANALYTICS_ENABLED=True
EOF

echo "✅ Environment configuration created"

# Create deployment requirements
cat > requirements-prod.txt << EOF
# Production Requirements
fastapi==0.104.1
uvicorn[standard]==0.24.0
gunicorn==21.2.0
sqlalchemy[asyncio]==2.0.23
aiosqlite==0.19.0
alembic==1.12.1
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-multipart==0.0.6
bcrypt==4.0.1
pydantic[email]==2.5.0
pydantic-settings==2.1.0
httpx==0.25.2
python-dotenv==1.0.0
pillow==10.1.0
jinja2==3.1.2
email-validator==2.1.0
EOF

echo "✅ Production requirements created"

# Create systemd service file
cat > punjab-rozgar.service << EOF
[Unit]
Description=Punjab Rozgar Portal API
After=network.target

[Service]
Type=exec
User=www-data
Group=www-data
WorkingDirectory=/opt/punjab-rozgar
Environment="PATH=/opt/punjab-rozgar/venv/bin"
ExecStart=/opt/punjab-rozgar/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
ExecReload=/bin/kill -HUP \$MAINPID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service file created"

# Create nginx configuration
cat > nginx-punjab-rozgar.conf << EOF
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect to HTTPS
    return 301 https://\$server_name\$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration (add your certificates)
    ssl_certificate /path/to/your/certificate.pem;
    ssl_certificate_key /path/to/your/private.key;
    
    # Frontend static files
    location / {
        root /opt/punjab-rozgar/frontend;
        try_files \$uri \$uri/ /index.html;
        add_header Cache-Control "public, max-age=31536000";
    }
    
    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
    
    # WebSocket support
    location /ws/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF

echo "✅ Nginx configuration created"

# Create deployment script
cat > deploy.sh << 'EOF'
#!/bin/bash

echo "🚀 Deploying Punjab Rozgar Portal..."

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3.11 python3.11-venv python3-pip nginx postgresql postgresql-contrib

# Create application directory
sudo mkdir -p /opt/punjab-rozgar
sudo chown $USER:$USER /opt/punjab-rozgar

# Copy application files
cp -r . /opt/punjab-rozgar/

# Create virtual environment
cd /opt/punjab-rozgar
python3.11 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements-prod.txt

# Run database migrations
cd backend
python -m alembic upgrade head

# Set up systemd service
sudo cp ../punjab-rozgar.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable punjab-rozgar
sudo systemctl start punjab-rozgar

# Set up nginx
sudo cp ../nginx-punjab-rozgar.conf /etc/nginx/sites-available/punjab-rozgar
sudo ln -s /etc/nginx/sites-available/punjab-rozgar /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx

# Set file permissions
sudo chown -R www-data:www-data /opt/punjab-rozgar
sudo chmod -R 755 /opt/punjab-rozgar

echo "✅ Deployment complete!"
echo "🌐 Access your portal at: https://yourdomain.com"
echo "📊 API docs at: https://yourdomain.com/api/docs"

EOF

chmod +x deploy.sh

echo "✅ Deployment script created"

# Create Docker deployment option
cat > Dockerfile << EOF
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements-prod.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements-prod.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
RUN chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Set working directory to backend
WORKDIR /app/backend

# Run the application
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
EOF

cat > docker-compose.yml << EOF
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=production
    volumes:
      - ./data:/app/backend/data
    restart: unless-stopped
  
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./frontend:/usr/share/nginx/html
      - ./ssl:/etc/nginx/ssl  # Add your SSL certificates here
    depends_on:
      - web
    restart: unless-stopped

volumes:
  data:
EOF

echo "✅ Docker configuration created"

echo ""
echo "🎉 DEPLOYMENT FILES CREATED!"
echo "================================"
echo ""
echo "📁 Files created:"
echo "  • .env.production - Production environment config"
echo "  • requirements-prod.txt - Production Python packages"
echo "  • punjab-rozgar.service - Systemd service"
echo "  • nginx-punjab-rozgar.conf - Nginx configuration"
echo "  • deploy.sh - Automated deployment script"
echo "  • Dockerfile - Docker container setup"
echo "  • docker-compose.yml - Docker Compose setup"
echo ""
echo "🚀 Deployment Options:"
echo "  1. Traditional Server: Run './deploy.sh'"
echo "  2. Docker: Run 'docker-compose up -d'"
echo ""
echo "⚙️  Before deployment:"
echo "  • Update domain name in nginx config"
echo "  • Add SSL certificates"
echo "  • Configure email settings in .env.production"
echo "  • Update JWT secret key"
echo ""
echo "🔧 Manual start commands:"
echo "  Backend: cd backend && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000"
echo "  Frontend: Serve frontend/ with any web server"