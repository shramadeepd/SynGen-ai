"""
SynGen AI - Final Production Application
Clean, optimized application with real data connections
"""

# Import the main application
from main_app import app

# This is the main entry point for the application
if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting SynGen AI Production Server...")
    uvicorn.run(app, host="0.0.0.0", port=8000)