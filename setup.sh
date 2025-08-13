#!/bin/bash

# JMA Client Knowledge Base Platform - Setup Script
# This script sets up the complete development environment

set -e

echo "=========================================="
echo "JMA Client Knowledge Base Platform Setup"
echo "=========================================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is required but not installed."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is required but not installed."
    exit 1
fi

echo "✅ Prerequisites check passed"

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your configuration (especially OPENAI_API_KEY)"
fi

# Start PostgreSQL with Docker
echo "🐳 Starting PostgreSQL database..."
docker-compose up -d postgres

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Initialize database
echo "🗄️  Initializing database with sample data..."
python scripts/init_db.py

echo "=========================================="
echo "✅ Setup completed successfully!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Update .env file with your OpenAI API key (optional)"
echo "2. Start the application: python backend/main.py"
echo "3. Run the demo: python scripts/demo.py"
echo "4. Access API docs: http://localhost:8000/docs"
echo ""
echo "To stop the database: docker-compose down"
echo "To start the database: docker-compose up -d postgres"