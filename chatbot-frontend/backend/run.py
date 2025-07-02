#!/usr/bin/env python3
"""
Simple script to run the FastAPI backend server
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("🚀 Starting Caregiver AI Agent Backend...")
    print("📍 Backend will be available at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔗 Frontend should connect to: http://localhost:8000")
    
    uvicorn.run(
        "main:app",  # Use import string for reload to work
        host="0.0.0.0", 
        port=8000,
        reload=True,  # Auto-reload on code changes during development
        log_level="info"
    ) 