import subprocess
import sys
import os

def start_server():
    print("🚀 Starting Caregiver AI Agent Backend...")
    print("📍 Backend will be available at: http://localhost:8000")
    
    try:
        # Change to the backend directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Start uvicorn directly
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Backend stopped")
    except Exception as e:
        print(f"❌ Error starting backend: {e}")
        print("💡 Try: pip install fastapi uvicorn python-multipart")

if __name__ == "__main__":
    start_server() 