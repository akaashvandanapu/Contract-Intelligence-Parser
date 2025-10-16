#!/usr/bin/env python3
"""
Verification script to check if the Contract Intelligence Parser system is properly set up
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a file exists"""
    if os.path.exists(file_path):
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description}: {file_path} - MISSING")
        return False

def check_directory_exists(dir_path, description):
    """Check if a directory exists"""
    if os.path.isdir(dir_path):
        print(f"✅ {description}: {dir_path}")
        return True
    else:
        print(f"❌ {description}: {dir_path} - MISSING")
        return False

def check_docker_available():
    """Check if Docker is available"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker: Not available")
            return False
    except FileNotFoundError:
        print("❌ Docker: Not installed")
        return False

def check_docker_compose_available():
    """Check if Docker Compose is available"""
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker Compose: Not available")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose: Not installed")
        return False

def check_python_packages():
    """Check if required Python packages can be imported"""
    required_packages = [
        'fastapi', 'uvicorn', 'motor', 'pymongo', 'PyPDF2', 
        'pydantic', 'aiofiles', 'pytest'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
            print(f"✅ Python package: {package}")
        except ImportError:
            print(f"❌ Python package: {package} - MISSING")
            missing_packages.append(package)
    
    return len(missing_packages) == 0

def check_json_file(file_path, description):
    """Check if a JSON file is valid"""
    if not os.path.exists(file_path):
        print(f"❌ {description}: {file_path} - MISSING")
        return False
    
    try:
        with open(file_path, 'r') as f:
            json.load(f)
        print(f"✅ {description}: {file_path} - Valid JSON")
        return True
    except json.JSONDecodeError as e:
        print(f"❌ {description}: {file_path} - Invalid JSON: {e}")
        return False

def main():
    """Run all verification checks"""
    print("🔍 Contract Intelligence Parser - Setup Verification")
    print("=" * 60)
    
    all_good = True
    
    # Check Docker availability
    print("\n📦 Docker Environment:")
    if not check_docker_available():
        all_good = False
    if not check_docker_compose_available():
        all_good = False
    
    # Check project structure
    print("\n📁 Project Structure:")
    required_files = [
        ("README.md", "Project README"),
        ("SETUP.md", "Setup documentation"),
        ("docker-compose.yml", "Docker Compose configuration"),
        ("sample_contract.pdf", "Sample contract file"),
        ("test_system.py", "System test script"),
        ("start.sh", "Linux startup script"),
        ("start.bat", "Windows startup script"),
    ]
    
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check backend structure
    print("\n🐍 Backend Structure:")
    backend_files = [
        ("backend/requirements.txt", "Backend dependencies"),
        ("backend/Dockerfile", "Backend Dockerfile"),
        ("backend/app/main.py", "Main FastAPI application"),
        ("backend/app/models.py", "Data models"),
        ("backend/app/parser.py", "Contract parser"),
        ("backend/app/scoring.py", "Scoring engine"),
        ("backend/app/database.py", "Database configuration"),
        ("backend/config.py", "Configuration settings"),
        ("backend/pytest.ini", "Test configuration"),
    ]
    
    for file_path, description in backend_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check backend tests
    print("\n🧪 Backend Tests:")
    test_files = [
        ("backend/tests/test_main.py", "Main API tests"),
        ("backend/tests/test_parser.py", "Parser tests"),
        ("backend/tests/test_scoring.py", "Scoring tests"),
    ]
    
    for file_path, description in test_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check frontend structure
    print("\n⚛️ Frontend Structure:")
    frontend_files = [
        ("frontend/package.json", "Frontend dependencies"),
        ("frontend/Dockerfile", "Frontend Dockerfile"),
        ("frontend/next.config.js", "Next.js configuration"),
        ("frontend/tsconfig.json", "TypeScript configuration"),
        ("frontend/tailwind.config.js", "Tailwind CSS configuration"),
        ("frontend/postcss.config.js", "PostCSS configuration"),
        ("frontend/.eslintrc.json", "ESLint configuration"),
    ]
    
    for file_path, description in frontend_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check frontend components
    print("\n🎨 Frontend Components:")
    component_files = [
        ("frontend/app/layout.tsx", "App layout"),
        ("frontend/app/page.tsx", "Main page"),
        ("frontend/app/globals.css", "Global styles"),
        ("frontend/app/components/ContractUpload.tsx", "Upload component"),
        ("frontend/app/components/ContractList.tsx", "List component"),
        ("frontend/app/components/ContractDetail.tsx", "Detail component"),
    ]
    
    for file_path, description in component_files:
        if not check_file_exists(file_path, description):
            all_good = False
    
    # Check JSON files
    print("\n📄 Configuration Files:")
    json_files = [
        ("frontend/package.json", "Package configuration"),
        ("frontend/tsconfig.json", "TypeScript configuration"),
        ("frontend/.eslintrc.json", "ESLint configuration"),
    ]
    
    for file_path, description in json_files:
        if not check_json_file(file_path, description):
            all_good = False
    
    # Check Python packages (optional - only if running locally)
    print("\n🐍 Python Environment (Optional):")
    if sys.executable:
        print(f"✅ Python executable: {sys.executable}")
        print(f"✅ Python version: {sys.version}")
        check_python_packages()
    
    # Summary
    print("\n" + "=" * 60)
    if all_good:
        print("🎉 All checks passed! The system is ready to run.")
        print("\nTo start the system:")
        print("  Windows: start.bat")
        print("  Linux/Mac: ./start.sh")
        print("  Manual: docker-compose up --build")
        print("\nTo test the system:")
        print("  python test_system.py")
    else:
        print("❌ Some checks failed. Please review the missing components above.")
        print("\nThe system may still work, but some features might be missing.")
    
    return all_good

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
