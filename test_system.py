#!/usr/bin/env python3
"""
Test script to verify the Contract Intelligence Parser system
"""

import requests
import time
import os
import sys

API_BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test if the API is running"""
    try:
        response = requests.get(f"{API_BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check passed - API is running")
            return True
        else:
            print(f"❌ Health check failed - Status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Health check failed - Cannot connect to API")
        return False

def test_contract_upload():
    """Test contract upload functionality"""
    # Use the sample contract if it exists
    sample_contract_path = "sample_contract.pdf"
    
    if not os.path.exists(sample_contract_path):
        print("❌ Sample contract not found - skipping upload test")
        return None
    
    try:
        with open(sample_contract_path, 'rb') as f:
            files = {'file': (sample_contract_path, f, 'application/pdf')}
            response = requests.post(f"{API_BASE_URL}/contracts/upload", files=files)
        
        if response.status_code == 200:
            data = response.json()
            contract_id = data.get('contract_id')
            print(f"✅ Contract uploaded successfully - ID: {contract_id}")
            return contract_id
        else:
            print(f"❌ Contract upload failed - Status: {response.status_code}")
            print(f"Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Contract upload failed - Error: {str(e)}")
        return None

def test_contract_status(contract_id):
    """Test contract status checking"""
    try:
        response = requests.get(f"{API_BASE_URL}/contracts/{contract_id}/status")
        if response.status_code == 200:
            data = response.json()
            status = data.get('status')
            progress = data.get('progress', 0)
            print(f"✅ Contract status retrieved - Status: {status}, Progress: {progress}%")
            return status
        else:
            print(f"❌ Status check failed - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Status check failed - Error: {str(e)}")
        return None

def test_contract_list():
    """Test contract listing"""
    try:
        response = requests.get(f"{API_BASE_URL}/contracts")
        if response.status_code == 200:
            data = response.json()
            contracts = data.get('contracts', [])
            total = data.get('total', 0)
            print(f"✅ Contract list retrieved - {len(contracts)} contracts, Total: {total}")
            return contracts
        else:
            print(f"❌ Contract list failed - Status: {response.status_code}")
            return []
    except Exception as e:
        print(f"❌ Contract list failed - Error: {str(e)}")
        return []

def wait_for_processing(contract_id, max_wait=60):
    """Wait for contract processing to complete"""
    print(f"⏳ Waiting for contract {contract_id} to process...")
    
    start_time = time.time()
    while time.time() - start_time < max_wait:
        status = test_contract_status(contract_id)
        if status == "completed":
            print("✅ Contract processing completed!")
            return True
        elif status == "failed":
            print("❌ Contract processing failed!")
            return False
        elif status in ["pending", "processing"]:
            time.sleep(3)
        else:
            print(f"❌ Unknown status: {status}")
            return False
    
    print("⏰ Timeout waiting for processing to complete")
    return False

def test_contract_data(contract_id):
    """Test contract data retrieval"""
    try:
        response = requests.get(f"{API_BASE_URL}/contracts/{contract_id}")
        if response.status_code == 200:
            data = response.json()
            print("✅ Contract data retrieved successfully")
            
            # Print some key information
            if 'parties' in data and data['parties']:
                print(f"   - Parties found: {len(data['parties'])}")
            if 'financial_details' in data and data['financial_details']:
                total_value = data['financial_details'].get('total_contract_value')
                if total_value:
                    print(f"   - Contract value: ${total_value:,.2f}")
            if 'confidence_scores' in data:
                scores = data['confidence_scores']
                print(f"   - Confidence scores: {scores}")
            
            return data
        else:
            print(f"❌ Contract data retrieval failed - Status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Contract data retrieval failed - Error: {str(e)}")
        return None

def test_contract_download(contract_id):
    """Test contract download"""
    try:
        response = requests.get(f"{API_BASE_URL}/contracts/{contract_id}/download")
        if response.status_code == 200:
            print("✅ Contract download successful")
            return True
        else:
            print(f"❌ Contract download failed - Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Contract download failed - Error: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Contract Intelligence Parser System Tests")
    print("=" * 60)
    
    # Test 1: Health check
    print("\n1. Testing API Health Check...")
    if not test_health_check():
        print("❌ System not ready. Please start the services first.")
        print("Run: docker-compose up --build")
        sys.exit(1)
    
    # Test 2: Contract upload
    print("\n2. Testing Contract Upload...")
    contract_id = test_contract_upload()
    if not contract_id:
        print("❌ Upload test failed. Skipping remaining tests.")
        sys.exit(1)
    
    # Test 3: Contract status
    print("\n3. Testing Contract Status...")
    test_contract_status(contract_id)
    
    # Test 4: Wait for processing
    print("\n4. Waiting for Processing...")
    if not wait_for_processing(contract_id):
        print("❌ Processing did not complete. Some tests may fail.")
    
    # Test 5: Contract data
    print("\n5. Testing Contract Data Retrieval...")
    test_contract_data(contract_id)
    
    # Test 6: Contract download
    print("\n6. Testing Contract Download...")
    test_contract_download(contract_id)
    
    # Test 7: Contract list
    print("\n7. Testing Contract List...")
    test_contract_list()
    
    print("\n" + "=" * 60)
    print("🎉 All tests completed!")
    print("\nTo view the web interface, visit: http://localhost:3000")
    print("To view API documentation, visit: http://localhost:8000/docs")

if __name__ == "__main__":
    main()
