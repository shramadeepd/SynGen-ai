#!/bin/bash

# SynGen AI - Production Startup Script
# This script starts both the backend and frontend services

set -e

echo "🚀 Starting SynGen AI Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if required directories exist
if [ ! -d "Backend" ]; then
    print_error "Backend directory not found!"
    exit 1
fi

if [ ! -d "Frontend/ai-agent-ui" ]; then
    print_error "Frontend directory not found!"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to start backend
start_backend() {
    print_status "Starting Backend API Server..."
    
    cd Backend
    
    # Check if virtual environment exists
    if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
        print_warning "Virtual environment not found. Creating one..."
        python -m venv .venv
        source .venv/bin/activate || source .venv/Scripts/activate
        pip install -r requirements.txt
    else
        # Activate virtual environment
        if [ -d ".venv" ]; then
            source .venv/bin/activate || source .venv/Scripts/activate
        else
            source venv/bin/activate || source venv/Scripts/activate
        fi
    fi
    
    # Check if port 8000 is available
    if check_port 8000; then
        print_warning "Port 8000 is already in use. Backend may already be running."
    else
        print_status "Starting FastAPI server on port 8000..."
        python main_app.py &
        BACKEND_PID=$!
        echo $BACKEND_PID > ../backend.pid
        print_success "Backend started with PID: $BACKEND_PID"
    fi
    
    cd ..
}

# Function to start frontend
start_frontend() {
    print_status "Starting Frontend Development Server..."
    
    cd Frontend/ai-agent-ui
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        print_warning "Node modules not found. Installing dependencies..."
        npm install
    fi
    
    # Check if port 3000 is available
    if check_port 3000; then
        print_warning "Port 3000 is already in use. Frontend may already be running."
    else
        print_status "Starting Vite development server on port 3000..."
        npm run dev &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../../frontend.pid
        print_success "Frontend started with PID: $FRONTEND_PID"
    fi
    
    cd ../..
}

# Function to build frontend for production
build_frontend() {
    print_status "Building Frontend for Production..."
    
    cd Frontend/ai-agent-ui
    
    if [ ! -d "node_modules" ]; then
        print_status "Installing dependencies..."
        npm install
    fi
    
    print_status "Building production bundle..."
    npm run build
    
    if [ $? -eq 0 ]; then
        print_success "Frontend built successfully! Files are in dist/ directory"
    else
        print_error "Frontend build failed!"
        exit 1
    fi
    
    cd ../..
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid)
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            print_success "Backend stopped"
        fi
        rm backend.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_success "Frontend stopped"
        fi
        rm frontend.pid
    fi
}

# Function to check service status
check_status() {
    print_status "Checking service status..."
    
    # Check backend
    if check_port 8000; then
        print_success "Backend API is running on http://localhost:8000"
        curl -s http://localhost:8000/health > /dev/null && print_success "Backend health check passed" || print_warning "Backend health check failed"
    else
        print_warning "Backend is not running"
    fi
    
    # Check frontend
    if check_port 3000; then
        print_success "Frontend is running on http://localhost:3000"
    else
        print_warning "Frontend is not running"
    fi
}

# Function to show help
show_help() {
    echo "SynGen AI Application Startup Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start     Start both backend and frontend services (default)"
    echo "  stop      Stop all running services"
    echo "  restart   Restart all services"
    echo "  status    Check status of services"
    echo "  build     Build frontend for production"
    echo "  backend   Start only backend service"
    echo "  frontend  Start only frontend service"
    echo "  help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                # Start all services"
    echo "  $0 start          # Start all services"
    echo "  $0 stop           # Stop all services"
    echo "  $0 status         # Check service status"
    echo "  $0 build          # Build for production"
}

# Main script logic
case "${1:-start}" in
    "start")
        print_status "Starting SynGen AI Application..."
        start_backend
        sleep 3  # Wait for backend to start
        start_frontend
        sleep 2
        check_status
        print_success "Application started successfully!"
        print_status "Backend API: http://localhost:8000"
        print_status "Frontend UI: http://localhost:3000"
        print_status "API Documentation: http://localhost:8000/docs"
        ;;
    "stop")
        stop_services
        ;;
    "restart")
        print_status "Restarting services..."
        stop_services
        sleep 2
        start_backend
        sleep 3
        start_frontend
        sleep 2
        check_status
        ;;
    "status")
        check_status
        ;;
    "build")
        build_frontend
        ;;
    "backend")
        start_backend
        sleep 2
        check_status
        ;;
    "frontend")
        start_frontend
        sleep 2
        check_status
        ;;
    "help"|"-h"|"--help")
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        show_help
        exit 1
        ;;
esac

# Trap to handle script interruption
trap 'print_status "Received interrupt signal. Stopping services..."; stop_services; exit 0' INT TERM 