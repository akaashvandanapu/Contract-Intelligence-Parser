#!/usr/bin/env python3
"""
MongoDB Atlas Connection Test Runner
Quick test to verify Atlas connectivity and basic operations
"""

import asyncio
import os
import sys
from datetime import datetime

from models import (Contract, ContractData, ContractStatus, FinancialDetails,
                    Party)
from motor.motor_asyncio import AsyncIOMotorClient
from scoring_engine import ScoringEngine


async def test_atlas_connection():
    """Test MongoDB Atlas connection and basic operations"""
    print("🔗 Testing MongoDB Atlas Connection...")
    
    # Get connection string
    mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://admin:synchrone@synchrone-contract-inte.8otpltf.mongodb.net/contract_intelligence?retryWrites=true&w=majority&appName=synchrone-contract-intelligence")
    
    try:
        # Connect to Atlas
        client = AsyncIOMotorClient(mongodb_url)
        db = client.contract_intelligence
        
        # Test connection
        print("📡 Pinging MongoDB Atlas...")
        result = await client.admin.command('ping')
        print(f"✅ Connection successful: {result}")
        
        # Test database access
        print("📊 Checking database collections...")
        collections = await db.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Test write operation
        print("✍️ Testing write operation...")
        test_collection = db.test_connection
        test_doc = {
            "test": "atlas_connection",
            "timestamp": datetime.utcnow(),
            "message": "MongoDB Atlas connection test successful"
        }
        
        result = await test_collection.insert_one(test_doc)
        print(f"✅ Document inserted with ID: {result.inserted_id}")
        
        # Test read operation
        print("📖 Testing read operation...")
        retrieved_doc = await test_collection.find_one({"_id": result.inserted_id})
        assert retrieved_doc is not None
        assert retrieved_doc["test"] == "atlas_connection"
        print("✅ Document retrieved successfully")
        
        # Test contract insertion
        print("📄 Testing contract data insertion...")
        contracts_collection = db.contracts
        
        sample_contract = {
            "id": "test_contract_atlas",
            "filename": "test_contract.pdf",
            "file_path": "/uploads/test_contract.pdf",
            "status": ContractStatus.PENDING,
            "uploaded_at": datetime.utcnow(),
            "file_size": 1024000,
            "progress": 0,
            "score": None,
            "gaps": [],
            "error_message": None,
            "parsed_data": None
        }
        
        contract_result = await contracts_collection.insert_one(sample_contract)
        print(f"✅ Contract inserted with ID: {contract_result.inserted_id}")
        
        # Test parsed data storage
        print("🔍 Testing parsed data storage...")
        sample_parsed_data = ContractData(
            parties=[
                Party(
                    name="Test Company",
                    role="customer",
                    email="test@company.com",
                    phone="+1-555-0123",
                    address="123 Test St, Test City, TC 12345"
                )
            ],
            account_info={
                "contact_email": "billing@test.com",
                "account_number": "TEST-12345"
            },
            financial_details=FinancialDetails(
                total_contract_value=10000.0,
                currency="USD",
                line_items=[
                    {
                        "description": "Test Service",
                        "quantity": 1,
                        "unit_price": 10000.0,
                        "total_price": 10000.0
                    }
                ]
            ),
            payment_terms={
                "payment_terms": "Net 30",
                "payment_schedule": "Monthly"
            },
            revenue_classification={
                "payment_type": "recurring",
                "billing_cycle": "Monthly"
            },
            sla={
                "performance_metrics": ["99% uptime"],
                "support_terms": "Business hours support"
            },
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31",
            contract_type="Service Agreement",
            confidence_scores={
                "financial_completeness": 90,
                "party_identification": 85,
                "payment_terms_clarity": 80,
                "sla_definition": 75,
                "contact_information": 70
            }
        )
        
        # Update contract with parsed data
        await contracts_collection.update_one(
            {"_id": contract_result.inserted_id},
            {
                "$set": {
                    "parsed_data": sample_parsed_data.dict(),
                    "status": ContractStatus.COMPLETED,
                    "score": 85.0
                }
            }
        )
        
        # Verify the update
        updated_contract = await contracts_collection.find_one({"_id": contract_result.inserted_id})
        assert updated_contract["status"] == "completed"
        assert updated_contract["score"] == 85.0
        assert updated_contract["parsed_data"] is not None
        print("✅ Parsed data stored successfully")
        
        # Test scoring engine
        print("📊 Testing scoring engine...")
        scoring_engine = ScoringEngine()
        score, gaps = scoring_engine.calculate_score(sample_parsed_data.dict())
        print(f"✅ Calculated score: {score}, Gaps: {len(gaps)}")
        
        # Test queries
        print("🔍 Testing database queries...")
        
        # Query by status
        completed_contracts = await contracts_collection.find({"status": "completed"}).to_list(length=None)
        print(f"✅ Found {len(completed_contracts)} completed contracts")
        
        # Query by score
        high_score_contracts = await contracts_collection.find({"score": {"$gte": 80}}).to_list(length=None)
        print(f"✅ Found {len(high_score_contracts)} high-score contracts")
        
        # Test aggregation
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_counts = await contracts_collection.aggregate(pipeline).to_list(length=None)
        print(f"✅ Status aggregation: {status_counts}")
        
        # Clean up test data
        print("🧹 Cleaning up test data...")
        await test_collection.delete_one({"_id": result.inserted_id})
        await contracts_collection.delete_one({"_id": contract_result.inserted_id})
        print("✅ Test data cleaned up")
        
        # Close connection
        await client.close()
        
        print("\n🎉 All MongoDB Atlas tests passed successfully!")
        print("✅ Atlas connection is working properly")
        print("✅ Database operations are functional")
        print("✅ Contract data can be stored and retrieved")
        print("✅ Scoring engine is working")
        print("✅ Queries and aggregations are working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ MongoDB Atlas test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False


async def test_file_operations():
    """Test file path operations"""
    print("\n📁 Testing file operations...")
    
    mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://admin:synchrone@synchrone-contract-inte.8otpltf.mongodb.net/contract_intelligence?retryWrites=true&w=majority&appName=synchrone-contract-intelligence")
    
    try:
        client = AsyncIOMotorClient(mongodb_url)
        db = client.contract_intelligence
        contracts_collection = db.contracts
        
        # Test file path storage
        test_file_path = "/uploads/test_contract_123.pdf"
        test_contract = {
            "id": "file_test_123",
            "filename": "test_contract_123.pdf",
            "file_path": test_file_path,
            "status": ContractStatus.COMPLETED,
            "uploaded_at": datetime.utcnow(),
            "file_size": 2048000,
            "progress": 100,
            "score": 90.0,
            "gaps": [],
            "error_message": None,
            "parsed_data": {
                "parties": [{"name": "Test Company", "role": "customer"}],
                "financial_details": {"total_contract_value": 25000.0}
            }
        }
        
        # Insert contract
        result = await contracts_collection.insert_one(test_contract)
        print(f"✅ Contract with file path inserted: {result.inserted_id}")
        
        # Test file path retrieval
        contract_by_path = await contracts_collection.find_one({"file_path": test_file_path})
        assert contract_by_path is not None
        assert contract_by_path["file_path"] == test_file_path
        print("✅ File path retrieval successful")
        
        # Test file path update
        new_file_path = "/uploads/updated_test_contract_123.pdf"
        await contracts_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"file_path": new_file_path}}
        )
        
        updated_contract = await contracts_collection.find_one({"_id": result.inserted_id})
        assert updated_contract["file_path"] == new_file_path
        print("✅ File path update successful")
        
        # Clean up
        await contracts_collection.delete_one({"_id": result.inserted_id})
        print("✅ File operations test completed")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ File operations test failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("🚀 Starting MongoDB Atlas Integration Tests")
    print("=" * 50)
    
    # Test basic connection
    connection_success = await test_atlas_connection()
    
    if connection_success:
        # Test file operations
        file_success = await test_file_operations()
        
        if file_success:
            print("\n🎉 All tests passed! MongoDB Atlas is ready for use.")
            print("✅ Connection: Working")
            print("✅ Database Operations: Working")
            print("✅ File Path Storage: Working")
            print("✅ Scoring Engine: Working")
            print("✅ Queries: Working")
        else:
            print("\n⚠️ Basic connection works, but file operations failed.")
    else:
        print("\n❌ MongoDB Atlas connection failed. Please check your connection string.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
