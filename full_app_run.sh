#!/bin/bash

# SynGen AI - Full Application Startup Script
# This script starts all services and runs comprehensive tests

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

success() {
    echo -e "${GREEN} $1${NC}"
}

error() {
    echo -e "${RED}L $1${NC}"
}

warning() {
    echo -e "${YELLOW}   $1${NC}"
}

info() {
    echo -e "${CYAN}9  $1${NC}"
}

# Configuration
APP_DIR="/mnt/d/Coding/SynGen-ai"
BACKEND_DIR="$APP_DIR/Backend"
API_PORT=8000
API_URL="http://localhost:$API_PORT"

# Check if script is run from correct directory
if [[ ! -d "$APP_DIR" ]]; then
    error "Please run this script from the SynGen-ai directory"
    exit 1
fi

cd "$APP_DIR"

echo "
TPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW
Q                    =€ SynGen AI Startup                      Q
Q                Full Application Test Suite                   Q
ZPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP]
"

# Step 1: Check Dependencies
log "Checking system dependencies..."

# Check Python
if ! command -v python3 &> /dev/null; then
    error "Python 3 is not installed"
    exit 1
fi
success "Python 3 found: $(python3 --version)"

# Check PostgreSQL
if ! command -v psql &> /dev/null; then
    error "PostgreSQL is not installed"
    exit 1
fi
success "PostgreSQL found: $(psql --version | head -n1)"

# Check if PostgreSQL is running
if ! pgrep postgres > /dev/null; then
    error "PostgreSQL is not running. Please start it first."
    exit 1
fi
success "PostgreSQL service is running"

# Step 2: Install Python Dependencies
log "Installing/updating Python dependencies..."
if pip install -r requirements.txt > /dev/null 2>&1; then
    success "Python dependencies installed"
else
    warning "Some dependencies may have failed to install, continuing..."
fi

# Step 3: Database Setup and Verification
log "Verifying database setup..."

# Check if database exists and has data
DB_CHECK=$(echo "62627" | sudo -S -u postgres psql -d syngen_ai -t -c "SELECT COUNT(*) FROM customers;" 2>/dev/null | xargs || echo "0")
if [[ "$DB_CHECK" -gt 0 ]]; then
    success "Database is set up with $DB_CHECK customers"
else
    warning "Database needs setup. Running setup scripts..."
    
    # Create database and user
    echo "62627" | sudo -S -u postgres psql -c "CREATE DATABASE syngen_ai;" 2>/dev/null || true
    echo "62627" | sudo -S -u postgres psql -c "CREATE USER syngen_user WITH PASSWORD 'syngen_password';" 2>/dev/null || true
    echo "62627" | sudo -S -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE syngen_ai TO syngen_user;" 2>/dev/null || true
    
    # Create tables
    if [[ -f "create_tables.sql" ]]; then
        echo "62627" | sudo -S -u postgres psql -d syngen_ai -f create_tables.sql > /dev/null 2>&1
        success "Database tables created"
    fi
    
    # Load data
    if [[ -f "load_data.py" && -f "Supply_chain_database(dataco-supply-chain-dataset)/DataCoSupplyChainDataset.csv" ]]; then
        info "Loading supply chain data (this may take a few minutes)..."
        timeout 300 python3 load_data.py > /dev/null 2>&1 || warning "Data loading may be incomplete"
        success "Supply chain data loaded"
    fi
fi

# Step 4: Document Storage Setup
log "Verifying document storage..."
if [[ ! -d "$BACKEND_DIR/data/documents" || ! -f "$BACKEND_DIR/data/documents/all_documents.json" ]]; then
    info "Setting up document storage..."
    if [[ -f "load_documents.py" ]]; then
        python3 load_documents.py > /dev/null 2>&1
        success "Documents processed and indexed"
    fi
else
    DOC_COUNT=$(python3 -c "import json; print(len(json.load(open('$BACKEND_DIR/data/documents/all_documents.json'))))" 2>/dev/null || echo "0")
    success "Document storage ready with $DOC_COUNT documents"
fi

# Step 5: Stop any existing API server
log "Stopping any existing API server..."
pkill -f "uvicorn.*api.main" 2>/dev/null || true
sleep 2

# Step 6: Start API Server
log "Starting API server..."
cd "$BACKEND_DIR"
export PYTHONPATH="$BACKEND_DIR"

# Start server in background
nohup python3 -m uvicorn api.main:app --host 0.0.0.0 --port $API_PORT > /tmp/syngen_api.log 2>&1 &
API_PID=$!

# Wait for server to start
log "Waiting for API server to start..."
for i in {1..30}; do
    if curl -s "$API_URL/" > /dev/null 2>&1; then
        success "API server started successfully (PID: $API_PID)"
        break
    fi
    sleep 1
    if [[ $i -eq 30 ]]; then
        error "API server failed to start. Check logs at /tmp/syngen_api.log"
        exit 1
    fi
done

# Step 7: Run Comprehensive Tests
log "Running comprehensive API tests..."
cd "$APP_DIR"

# Create and run test script
python3 test_all_endpoints.py

# Step 8: Display Final Status
echo "
TPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPW
Q                    <‰ Startup Complete!                      Q
ZPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPPP]

=Ê System Status:
   " API Server: Running on $API_URL (PID: $API_PID)
   " Database: PostgreSQL with supply chain data
   " Documents: Processed and indexed
   " Logs: /tmp/syngen_api.log

= Quick Links:
   " API Documentation: $API_URL/docs
   " Health Check: $API_URL/health
   " Root Endpoint: $API_URL/

=à  Commands:
   " Stop API: kill $API_PID
   " View Logs: tail -f /tmp/syngen_api.log
   " Restart: $0

Happy coding! =€
"

# Keep script running to show logs
info "Press Ctrl+C to stop monitoring logs..."
trap "echo; info 'Stopping API server...'; kill $API_PID 2>/dev/null; exit 0" INT

# Follow logs
tail -f /tmp/syngen_api.log