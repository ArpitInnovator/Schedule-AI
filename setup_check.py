#!/usr/bin/env python3
"""
Setup verification script for ScheduleAI
Checks dependencies, configuration, and basic functionality
"""

import sys
import os
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} - OK")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} - Requires Python 3.8+")
        return False

def check_dependencies():
    """Check if required packages are installed."""
    required_packages = [
        'fastapi', 'uvicorn', 'streamlit', 'langchain', 
        'langchain_google_genai', 'google-api-python-client',
        'google-auth', 'pydantic', 'requests', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} - Installed")
        except ImportError:
            print(f"❌ {package} - Missing")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    return True

def check_environment_variables():
    """Check if required environment variables are set."""
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = {
        'GOOGLE_API_KEY': 'Gemini API key',
        'GOOGLE_SERVICE_ACCOUNT_JSON': 'Service account JSON',
        'GOOGLE_CALENDAR_ID': 'Calendar ID'
    }
    
    missing_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f'your_{var.lower()}_here':
            print(f"✅ {var} - Configured")
            
            # Additional validation for JSON
            if var == 'GOOGLE_SERVICE_ACCOUNT_JSON':
                try:
                    json.loads(value)
                    print(f"  └─ Valid JSON format")
                except json.JSONDecodeError:
                    print(f"  └─ ⚠️  Invalid JSON format")
        else:
            print(f"❌ {var} - Not configured ({description})")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚙️  Configure missing variables in .env file")
        return False
    return True

def check_file_structure():
    """Check if all required files exist."""
    required_files = [
        'requirements.txt',
        '.env.example',
        'backend/main.py',
        'backend/calendar_client.py',
        'backend/agent_tools.py',
        'backend/booking_agent.py',
        'frontend/app.py'
    ]
    
    missing_files = []
    
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} - Exists")
        else:
            print(f"❌ {file_path} - Missing")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_basic_imports():
    """Test if basic imports work."""
    try:
        print("\n🧪 Testing basic imports...")
        
        # Test FastAPI
        from fastapi import FastAPI
        print("✅ FastAPI import - OK")
        
        # Test Streamlit
        import streamlit
        print("✅ Streamlit import - OK")
        
        # Test LangChain
        from langchain.tools import tool
        print("✅ LangChain import - OK")
        
        # Test Google packages
        from google.auth import service_account
        print("✅ Google Auth import - OK")
        
        from googleapiclient.discovery import build
        print("✅ Google API Client import - OK")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def main():
    """Run all checks."""
    print("🔍 ScheduleAI Setup Verification\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies), 
        ("File Structure", check_file_structure),
        ("Environment Variables", check_environment_variables),
        ("Basic Imports", test_basic_imports)
    ]
    
    results = []
    
    for check_name, check_func in checks:
        print(f"\n📋 Checking {check_name}...")
        result = check_func()
        results.append(result)
    
    print("\n" + "="*50)
    print("📊 SETUP SUMMARY")
    print("="*50)
    
    for i, (check_name, _) in enumerate(checks):
        status = "✅ PASS" if results[i] else "❌ FAIL"
        print(f"{check_name:.<30} {status}")
    
    all_passed = all(results)
    
    if all_passed:
        print("\n🎉 All checks passed! You're ready to run ScheduleAI.")
        print("\nNext steps:")
        print("1. Start backend: ./start_backend.sh")
        print("2. Start frontend: ./start_frontend.sh")
        print("3. Open http://localhost:8501")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above before running the application.")
        print("\nFor help, see the README.md file or the troubleshooting section.")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)