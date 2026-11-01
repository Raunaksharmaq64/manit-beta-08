#!/bin/bash
# ==============================================================================
# RIGHT FIT — Master All-In-One AWS EC2 Production Deployment
# Ubuntu 20.04 / 22.04 / 24.04 LTS Compatible
# ==============================================================================
set -e

echo "======================================================================"
echo "    🚀 STARTING RIGHT FIT PRODUCTION DEPLOYMENT ON AWS EC2"
echo "======================================================================"

# 1. Setup 2GB Swap Memory (Prevents OOM kill on t2.micro/small during Next.js build)
if ! swapon --show | grep -q "swapfile"; then
    echo "[1/8] Configuring 2GB Swap Memory..."
    sudo fallocate -l 2G /swapfile 2>/dev/null || sudo dd if=/dev/zero of=/swapfile bs=1M count=2048
    sudo chmod 600 /swapfile
    sudo mkswap /swapfile
    sudo swapon /swapfile
    echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
    echo "Swap allocated successfully."
else
    echo "[1/8] Swap space already present."
fi

# 2. System Updates & Core Packages
echo "[2/8] Installing System Dependencies (Python 3, Nginx, Redis, Git)..."
sudo apt-get update -y
sudo apt-get install -y curl wget git python3 python3-pip python3-venv nginx redis-server build-essential

# Ensure Redis is running
sudo systemctl enable redis-server 2>/dev/null || sudo systemctl enable redis 2>/dev/null || true
sudo systemctl restart redis-server 2>/dev/null || sudo systemctl restart redis 2>/dev/null || true

# 3. Install Node.js 20 LTS & PM2
echo "[3/8] Installing Node.js 20 LTS & PM2..."
if ! command -v node &> /dev/null || [ "$(node -v | cut -d'.' -f1 | tr -d 'v')" -lt 18 ]; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
fi
sudo npm install -g pm2

# 4. Clone or Pull Repository
REPO_DIR="$HOME/manit-beta-08"
REPO_URL="https://github.com/Raunaksharmaq64/manit-beta-08.git"

if [ -d "$REPO_DIR/.git" ]; then
    echo "[4/8] Existing repository found at $REPO_DIR. Pulling latest main..."
    cd "$REPO_DIR"
    git fetch origin main
    git reset --hard origin/main
elif [ -d "$PWD/.git" ]; then
    echo "[4/8] Running from existing local repository root: $PWD"
    REPO_DIR="$PWD"
    cd "$REPO_DIR"
else
    echo "[4/8] Cloning repository from GitHub..."
    git clone "$REPO_URL" "$REPO_DIR"
    cd "$REPO_DIR"
fi

# 5. Generate Production Environment Files
echo "[5/8] Configuring Production Environment Files (.env, .env.local)..."

# Fallback values from environment if passed
DB_URL="${DATABASE_URL:-postgresql+asyncpg://neondb_owner:npg_5T0YKcISFikZ@ep-noisy-firefly-b35mou1p-pooler.c-4.ap-southeast-1.aws.neon.tech/neondb?ssl=require}"
GEM_KEY="${GEMINI_API_KEY:-}"
RES_KEY="${RESEND_API_KEY:-}"
SERP_KEY="${SERPER_API_KEY:-}"
ADZ_ID="${ADZUNA_APP_ID:-4d096737}"
ADZ_KEY="${ADZUNA_APP_KEY:-3612fca6ffecd9ce96b304e690c39ddd}"
JOO_KEY="${JOOBLE_API_KEY:-62931f47-5827-4a07-9bdc-5c9c6f95120a}"

# If backend/.env already exists, preserve it; otherwise create it
if [ ! -f "$REPO_DIR/backend/.env" ]; then
cat << EOF > "$REPO_DIR/backend/.env"
APP_ENV=production
APP_NAME="RIGHT FIT Core Career Engine"
DEBUG=false
PORT=8000
API_V1_STR=/api/v1
FRONTEND_URL=http://localhost:3000
BACKEND_API_URL=http://localhost:8000/api/v1

DATABASE_URL=${DB_URL}

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_URL=redis://localhost:6379/0

SECRET_KEY=rightfit_dev_super_secret_signing_key_32bytes_min!
JWT_SECRET=rightfit_jwt_signing_secret_key_minimum_32_bytes!
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
REFRESH_TOKEN_EXPIRE_DAYS=7
AUTH_COOKIE_NAME=rightfit_session

LEADHUNTER_BASE_URL=http://localhost:8001
STARTUP_INTELLIGENCE_BASE_URL=http://127.0.0.1:8002
INTERNAL_SERVICE_KEY=rightfit_internal_shared_secret_key_123

GEMINI_API_KEY=${GEM_KEY}
GEMINI_MODEL=gemini-2.5-flash
OPENAI_API_KEY=

SERPAPI_KEY=
APIFY_TOKEN=
SERPER_API_KEY=${SERP_KEY}
HUNTER_API_KEY=

ADZUNA_APP_ID=${ADZ_ID}
ADZUNA_APP_KEY=${ADZ_KEY}
JOOBLE_API_KEY=${JOO_KEY}

RESEND_API_KEY=${RES_KEY}
RESEND_SENDER_EMAIL=onboarding@resend.dev

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email@gmail.com
SMTP_PASSWORD=
SMTP_FROM_EMAIL=notifications@rightfit.internal

AWS_REGION=us-east-1
S3_BUCKET_RESUMES=rightfit-resumes-prod
S3_BUCKET_REPORTS=rightfit-reports-prod
S3_BUCKET_BACKUPS=rightfit-backups-prod
USE_S3_STORAGE=false
RESUME_STORAGE_DIR=./storage/resumes
EOF
fi

cp -f "$REPO_DIR/backend/.env" "$REPO_DIR/.env"

# Startup Intelligence .env
mkdir -p "$REPO_DIR/services/startup_intelligence"
if [ ! -f "$REPO_DIR/services/startup_intelligence/.env" ]; then
cat << EOF > "$REPO_DIR/services/startup_intelligence/.env"
PORT=8002
INTERNAL_SERVICE_KEY=rightfit_internal_shared_secret_key_123
GEMINI_API_KEY=${GEM_KEY}
GEMINI_MODEL=gemini-2.5-flash
SERPER_API_KEY=${SERP_KEY}
RESEND_API_KEY=${RES_KEY}
RESEND_SENDER_EMAIL=onboarding@resend.dev
EOF
fi

# Frontend .env.local
mkdir -p "$REPO_DIR/frontend"
cat << 'EOF' > "$REPO_DIR/frontend/.env.local"
NEXT_PUBLIC_API_URL=/api/v1
NEXT_PUBLIC_APP_ENV=production
EOF

mkdir -p "$REPO_DIR/storage/resumes"

# 6. Setup Python Virtual Environment & Install Requirements
echo "[6/8] Setting up Python virtual environment..."
cd "$REPO_DIR"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r backend/requirements.txt
if [ -f "services/startup_intelligence/requirements.txt" ]; then
    pip install -r services/startup_intelligence/requirements.txt
fi

# 7. Frontend Dependencies & Production Build
echo "[7/8] Installing Frontend packages and compiling Next.js..."
cd "$REPO_DIR/frontend"
npm install
npm run build
cd "$REPO_DIR"

# 8. Configure Nginx Reverse Proxy
echo "[8/8] Configuring Nginx Reverse Proxy..."
sudo tee /etc/nginx/sites-available/rightfit > /dev/null << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    client_max_body_size 25M;

    # Gzip Compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml image/svg+xml;

    # Core FastAPI Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
        proxy_connect_timeout 120s;
    }

    # API Documentation & OpenAPI schema
    location ~ ^/(docs|redoc|openapi.json|health) {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Next.js Frontend Web Application
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/rightfit /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx

# 9. Launch & Persist Services via PM2
echo "Starting Application Processes with PM2..."
cd "$REPO_DIR"
pm2 delete all 2>/dev/null || true
pm2 start ecosystem.config.js
pm2 save

STARTUP_CMD=$(pm2 startup systemd -u "$USER" --hp "$HOME" | grep "sudo env" || true)
if [ -n "$STARTUP_CMD" ]; then
    eval "$STARTUP_CMD"
fi

PUBLIC_IP=$(curl -s http://checkip.amazonaws.com 2>/dev/null || curl -s https://ifconfig.me 2>/dev/null || echo "your-ec2-ip")

echo "======================================================================"
echo "    🎉 RIGHT FIT PRODUCTION DEPLOYMENT FINISHED SUCCESSFULLY!"
echo "======================================================================"
echo ""
echo "Access your live platform:"
echo "👉 Web Application:     http://${PUBLIC_IP}"
echo "👉 Backend API Docs:    http://${PUBLIC_IP}/docs"
echo "👉 API Health Check:    http://${PUBLIC_IP}/health/live"
echo ""
echo "To monitor your processes anytime:"
echo "  pm2 status"
echo "  pm2 logs"
echo "======================================================================"
