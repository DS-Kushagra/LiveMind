# LiveMind - Quick Setup & Test Script
# Run this to verify your installation works!

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}")
    print(f"Running: {command}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("Success!")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False

def main():
    print("LiveMind Backend Setup & Test")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("backend"):
        print("Please run this script from the LiveMind root directory")
        return
    
    # Change to backend directory
    os.chdir("backend")
    
    # Check Python version
    print(f"Python version: {sys.version}")
    
    # Create virtual environment if it doesn't exist
    if not os.path.exists("venv"):
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return
    
    # Activate virtual environment and install dependencies
    if sys.platform == "win32":
        activate_cmd = "venv\\Scripts\\activate"
        pip_cmd = "venv\\Scripts\\pip"
        python_cmd = "venv\\Scripts\\python"
    else:
        activate_cmd = "source venv/bin/activate"
        pip_cmd = "venv/bin/pip"
        python_cmd = "venv/bin/python"
    
    # Install dependencies
    if not run_command(f"{pip_cmd} install -r requirements.txt", "Installing dependencies"):
        print("Some dependencies might have failed. This is normal for optional packages.")
    
    # Test basic imports
    test_script = '''
import sys
sys.path.append(".")
try:
    from app.core.config import settings
    from app.core.logging import setup_logging
    print("Core imports successful")
    print(f"Data directory: {settings.CHROMA_PERSIST_DIRECTORY}")
    print(f"Cache directory: {settings.PATHWAY_CACHE_DIR}")
    print("LiveMind backend is ready to run!")
except Exception as e:
    print(f"Import error: {e}")
    sys.exit(1)
'''
    
    with open("test_imports.py", "w", encoding="utf-8") as f:
        f.write(test_script)
    
    if run_command(f"{python_cmd} test_imports.py", "Testing imports"):
        print("\nSetup completed successfully!")
        print("\nTo start the server, run:")
        print(f"   cd backend")
        if sys.platform == "win32":
            print(f"   venv\\Scripts\\activate")
        else:
            print(f"   source venv/bin/activate")
        print(f"   python -m uvicorn main:app --reload")
        print("\nAPI docs will be available at: http://localhost:8000/docs")
    else:
        print("\nSetup failed. Please check the errors above.")
    
    # Cleanup
    if os.path.exists("test_imports.py"):
        os.remove("test_imports.py")

if __name__ == "__main__":
    main()
