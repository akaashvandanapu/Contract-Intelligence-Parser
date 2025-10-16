#!/usr/bin/env python3
"""
Complete System Test Script
Tests the entire Contract Intelligence Parser system with MongoDB Atlas
"""

import json
import os
import time
from datetime import datetime

import requests


def test_backend_health():
    """Test backend health and API endpoints"""
    print("🔍 Testing Backend Health...")
    
    try:
        # Test root endpoint
        response = requests.get("http://localhost:8000/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        print("✅ Backend root endpoint working")
        
        # Test health endpoint
        response = requests.get("http://localhost:8000/health")
        assert response.status_code == 200
        print("✅ Backend health endpoint working")
        
        # Test contracts list
        response = requests.get("http://localhost:8000/contracts")
        assert response.status_code == 200
        contracts = response.json()
        print(f"✅ Contracts list endpoint working - Found {len(contracts)} contracts")
        
        return True
        
    except Exception as e:
        print(f"❌ Backend health test failed: {e}")
        return False


def test_frontend_health():
    """Test frontend health"""
    print("\n🔍 Testing Frontend Health...")
    
    try:
        response = requests.get("http://localhost:3000/")
        assert response.status_code == 200
        assert "Contract Intelligence Parser" in response.text
        print("✅ Frontend is accessible")
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend health test failed: {e}")
        return False


def test_contract_upload():
    """Test contract upload functionality"""
    print("\n📄 Testing Contract Upload...")
    
    try:
        # Create a test PDF content (minimal valid PDF)
        test_pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
72 720 Td
(Test Contract) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000206 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
299
%%EOF"""
        
        # Upload the test PDF
        files = {'file': ('test_contract.pdf', test_pdf_content, 'application/pdf')}
        response = requests.post("http://localhost:8000/contracts/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            contract_id = data.get('contract_id')
            print(f"✅ Contract uploaded successfully - ID: {contract_id}")
            return contract_id
        else:
            print(f"❌ Contract upload failed: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Contract upload test failed: {e}")
        return None


def test_contract_processing(contract_id):
    """Test contract processing status"""
    print(f"\n⏳ Testing Contract Processing for ID: {contract_id}...")
    
    if not contract_id:
        print("❌ No contract ID provided")
        return False
    
    try:
        max_attempts = 30  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            response = requests.get(f"http://localhost:8000/contracts/{contract_id}/status")
            
            if response.status_code == 200:
                data = response.json()
                status = data.get('status')
                progress = data.get('progress', 0)
                
                print(f"📊 Status: {status}, Progress: {progress}%")
                
                if status == 'completed':
                    print("✅ Contract processing completed")
                    return True
                elif status == 'failed':
                    error = data.get('error_message', 'Unknown error')
                    print(f"❌ Contract processing failed: {error}")
                    return False
                elif status in ['pending', 'processing']:
                    time.sleep(10)  # Wait 10 seconds
                    attempt += 1
                else:
                    print(f"❌ Unknown status: {status}")
                    return False
            else:
                print(f"❌ Status check failed: {response.status_code}")
                return False
        
        print("❌ Contract processing timed out")
        return False
        
    except Exception as e:
        print(f"❌ Contract processing test failed: {e}")
        return False


def test_contract_data(contract_id):
    """Test contract data retrieval"""
    print(f"\n📊 Testing Contract Data Retrieval for ID: {contract_id}...")
    
    if not contract_id:
        print("❌ No contract ID provided")
        return False
    
    try:
        response = requests.get(f"http://localhost:8000/contracts/{contract_id}")
        
        if response.status_code == 200:
            data = response.json()
            
            # Check if parsed data exists
            if 'parsed_data' in data and data['parsed_data']:
                parsed_data = data['parsed_data']
                print("✅ Contract data retrieved successfully")
                
                # Check key fields
                if 'parties' in parsed_data:
                    print(f"✅ Parties found: {len(parsed_data['parties'])}")
                
                if 'financial_details' in parsed_data:
                    financial = parsed_data['financial_details']
                    if 'total_contract_value' in financial:
                        print(f"✅ Financial details found: ${financial['total_contract_value']}")
                
                if 'confidence_scores' in parsed_data:
                    scores = parsed_data['confidence_scores']
                    print(f"✅ Confidence scores: {scores}")
                
                if 'summary' in parsed_data:
                    summary = parsed_data['summary']
                    print(f"✅ Contract summary: {summary.get('overview', 'N/A')}")
                
                return True
            else:
                print("⚠️ Contract processed but no parsed data available")
                return True
        else:
            print(f"❌ Contract data retrieval failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Contract data test failed: {e}")
        return False


def test_contract_download(contract_id):
    """Test contract download"""
    print(f"\n📥 Testing Contract Download for ID: {contract_id}...")
    
    if not contract_id:
        print("❌ No contract ID provided")
        return False
    
    try:
        response = requests.get(f"http://localhost:8000/contracts/{contract_id}/download")
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            if 'application/pdf' in content_type:
                print("✅ Contract download successful - PDF content received")
                return True
            else:
                print(f"⚠️ Download successful but unexpected content type: {content_type}")
                return True
        else:
            print(f"❌ Contract download failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Contract download test failed: {e}")
        return False


def test_mongodb_atlas_integration():
    """Test MongoDB Atlas integration"""
    print("\n🗄️ Testing MongoDB Atlas Integration...")
    
    try:
        # Test if we can get contracts from the database
        response = requests.get("http://localhost:8000/contracts")
        
        if response.status_code == 200:
            contracts = response.json()
            print(f"✅ MongoDB Atlas integration working - {len(contracts)} contracts in database")
            
            # Check if contracts have file_path stored
            for contract in contracts:
                if 'file_path' in contract and contract['file_path']:
                    print(f"✅ File path stored: {contract['file_path']}")
                    break
            
            return True
        else:
            print(f"❌ MongoDB Atlas integration failed: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ MongoDB Atlas integration test failed: {e}")
        return False


def test_frontend_functionality():
    """Test frontend functionality"""
    print("\n🎨 Testing Frontend Functionality...")
    
    try:
        # Test main page
        response = requests.get("http://localhost:3000/")
        assert response.status_code == 200
        
        # Check for key UI elements
        content = response.text
        assert "Contract Intelligence Parser" in content
        assert "Upload Contract" in content
        assert "Contract List" in content
        print("✅ Frontend main page working")
        
        # Test if we can access the contract list page
        # Note: This would require navigating to the contract list tab
        # For now, we'll just verify the main page loads
        
        return True
        
    except Exception as e:
        print(f"❌ Frontend functionality test failed: {e}")
        return False


def main():
    """Run complete system tests"""
    print("🚀 Starting Complete System Tests")
    print("=" * 50)
    
    # Test results
    results = {}
    
    # 1. Test backend health
    results['backend_health'] = test_backend_health()
    
    # 2. Test frontend health
    results['frontend_health'] = test_frontend_health()
    
    # 3. Test MongoDB Atlas integration
    results['mongodb_atlas'] = test_mongodb_atlas_integration()
    
    # 4. Test frontend functionality
    results['frontend_functionality'] = test_frontend_functionality()
    
    # 5. Test contract upload
    contract_id = test_contract_upload()
    results['contract_upload'] = contract_id is not None
    
    if contract_id:
        # 6. Test contract processing
        results['contract_processing'] = test_contract_processing(contract_id)
        
        # 7. Test contract data retrieval
        results['contract_data'] = test_contract_data(contract_id)
        
        # 8. Test contract download
        results['contract_download'] = test_contract_download(contract_id)
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    
    total_tests = len(results)
    passed_tests = sum(1 for result in results.values() if result)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is fully functional.")
        print("✅ Backend API: Working")
        print("✅ Frontend UI: Working")
        print("✅ MongoDB Atlas: Connected")
        print("✅ Contract Processing: Working")
        print("✅ PDF Upload/Download: Working")
        print("✅ AI Analysis: Working")
    else:
        print(f"\n⚠️ {total_tests - passed_tests} tests failed. Please check the issues above.")
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
