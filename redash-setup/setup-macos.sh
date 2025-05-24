#!/bin/bash

echo "🚀 Redash Setup for macOS"
echo "=========================="

# Check if pwgen is installed
if ! command -v pwgen &> /dev/null; then
    echo "❌ pwgen is not installed. Installing it now..."
    if command -v brew &> /dev/null; then
        brew install pwgen
    else
        echo "❌ Homebrew is not installed. Please install Homebrew first or install pwgen manually."
        exit 1
    fi
fi

echo "✅ pwgen is available"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Check if Docker Compose is available
if ! docker compose version > /dev/null 2>&1; then
    echo "❌ Docker Compose is not available. Please install Docker Desktop with Compose support."
    exit 1
fi

echo "✅ Docker Compose is available"

# Generate secure secrets
echo "🔐 Generating secure secrets..."
COOKIE_SECRET=$(pwgen -1s 32)
SECRET_KEY=$(pwgen -1s 32)
PG_PASSWORD=$(pwgen -1s 32)

# Create .env file with generated secrets
echo "📝 Creating environment file..."
cat > .env << EOF
PYTHONUNBUFFERED=0
REDASH_LOG_LEVEL=INFO
REDASH_REDIS_URL=redis://redis:6379/0
REDASH_COOKIE_SECRET=$COOKIE_SECRET
REDASH_SECRET_KEY=$SECRET_KEY
POSTGRES_PASSWORD=$PG_PASSWORD
REDASH_DATABASE_URL=postgresql://postgres:$PG_PASSWORD@postgres/postgres
REDASH_ENFORCE_CSRF=true
REDASH_GUNICORN_TIMEOUT=60
EOF

echo "✅ Environment file created with fresh secrets"

# Pull the latest Redash images
echo "📥 Pulling Redash Docker images..."
docker compose pull

# Start the services
echo "🏗️  Starting Redash services..."
docker compose up -d postgres redis

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 10

# Initialize the database
echo "🗄️  Initializing Redash database..."
docker compose run --rm server create_db

# Start all services
echo "🚀 Starting all Redash services..."
docker compose up -d

echo ""
echo "🎉 Redash installation completed!"
echo ""
echo "📍 Redash is now available at: http://localhost:5005"
echo ""
echo "🔧 To manage Redash:"
echo "   • Stop:    docker compose down"
echo "   • Start:   docker compose up -d"
echo "   • Logs:    docker compose logs -f"
echo "   • Status:  docker compose ps"
echo ""
echo "📊 PostgreSQL is also available at localhost:5433"
echo "   • Database: postgres"
echo "   • Username: postgres"
echo "   • Password: $PG_PASSWORD"
echo ""
echo "⚠️  Note: It may take a few minutes for Redash to fully start up."
echo "   The first load can be slow as Python code is being compiled."
echo ""
echo "🔐 Your generated secrets have been saved to .env file" 