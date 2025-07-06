#!/usr/bin/env python3
"""
Setup testing script for Calendar Booking Agent.
This script helps verify that all configurations are correct.
"""

import os
import sys
from pathlib import Path
import json

def test_backend_setup():
    """Test backend configuration."""
    print("\n🔍 Testing Backend Setup...")
    
    # Check if in backend directory
    backend_path = Path("backend")
    if not backend_path.exists():
        print("❌ Backend directory not found. Run this from the project root.")
        return False
    
    # Check environment variables
    env_file = backend_path / ".env"
    if not env_file.exists():
        print("❌ No .env file found in backend directory")
        print("   Create one by copying .env.example and filling in your values")
        return False
    
    print("✅ Backend .env file found")
    
    # Try to load and validate environment
    try:
        # Add backend to path temporarily
        sys.path.insert(0, str(backend_path))
        from config import settings, validate_settings
        
        validate_settings()
        print("✅ Backend configuration is valid")
        
        # Check service account file
        sa_path = Path(settings.google_calendar_credentials_path)
        if sa_path.exists():
            print("✅ Service account file found")
            # Try to parse it
            try:
                with open(sa_path) as f:
                    sa_data = json.load(f)
                    if "client_email" in sa_data:
                        print(f"✅ Service account email: {sa_data['client_email']}")
            except:
                print("⚠️  Could not parse service account file")
        else:
            print("❌ Service account file not found")
            return False
            
    except Exception as e:
        print(f"❌ Backend configuration error: {e}")
        return False
    finally:
        # Remove from path
        if str(backend_path) in sys.path:
            sys.path.remove(str(backend_path))
    
    return True


def test_frontend_setup():
    """Test frontend configuration."""
    print("\n🔍 Testing Frontend Setup...")
    
    frontend_path = Path("frontend")
    if not frontend_path.exists():
        print("❌ Frontend directory not found")
        return False
    
    # Check if requirements exist
    req_file = frontend_path / "requirements.txt"
    if req_file.exists():
        print("✅ Frontend requirements.txt found")
    else:
        print("❌ Frontend requirements.txt not found")
        return False
    
    # Check main app file
    app_file = frontend_path / "app.py"
    if app_file.exists():
        print("✅ Frontend app.py found")
    else:
        print("❌ Frontend app.py not found")
        return False
    
    return True


def test_dependencies():
    """Test if required Python packages are installed."""
    print("\n🔍 Testing Dependencies...")
    
    required_packages = {
        "backend": [
            "fastapi",
            "uvicorn",
            "google-auth",
            "google-api-python-client",
            "langchain",
            "langchain-google-genai"
        ],
        "frontend": [
            "streamlit",
            "requests"
        ]
    }
    
    # Test backend dependencies
    print("\nBackend dependencies:")
    backend_ok = True
    for package in required_packages["backend"]:
        try:
            __import__(package.replace("-", "_"))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (not installed)")
            backend_ok = False
    
    # Test frontend dependencies
    print("\nFrontend dependencies:")
    frontend_ok = True
    for package in required_packages["frontend"]:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package} (not installed)")
            frontend_ok = False
    
    if not backend_ok:
        print("\n⚠️  Install backend dependencies: cd backend && pip install -r requirements.txt")
    
    if not frontend_ok:
        print("\n⚠️  Install frontend dependencies: cd frontend && pip install -r requirements.txt")
    
    return backend_ok and frontend_ok


def main():
    """Run all tests."""
    print("=" * 60)
    print("🚀 Calendar Booking Agent Setup Tester")
    print("=" * 60)
    
    # Check current directory
    if not Path("README.md").exists():
        print("❌ Please run this script from the project root directory")
        sys.exit(1)
    
    results = {
        "Backend Setup": test_backend_setup(),
        "Frontend Setup": test_frontend_setup(),
        "Dependencies": test_dependencies()
    }
    
    print("\n" + "=" * 60)
    print("📊 Summary:")
    print("=" * 60)
    
    all_passed = True
    for test, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n🎉 All tests passed! Your setup looks good.")
        print("\nNext steps:")
        print("1. Start the backend: cd backend && python app.py")
        print("2. Start the frontend: cd frontend && streamlit run app.py")
        print("3. Open http://localhost:8501 in your browser")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above and try again.")
        print("Check docs/setup.md for detailed setup instructions.")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()