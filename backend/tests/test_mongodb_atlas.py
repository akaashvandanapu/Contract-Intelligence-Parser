"""
Comprehensive MongoDB Atlas Integration Tests
Tests for database operations, data persistence, and Atlas connectivity
"""

import asyncio
import os
from datetime import datetime

import pytest
from app.models import (Contract, ContractData, ContractStatus,
                        FinancialDetails, Party)
from app.scoring_engine import ScoringEngine
from motor.motor_asyncio import AsyncIOMotorClient


class TestMongoDBAtlas:
    """Test MongoDB Atlas connectivity and operations"""
    
    @pytest.fixture
    async def db_client(self):
        """Create MongoDB Atlas client for testing"""
        mongodb_url = os.getenv("MONGODB_URL", "mongodb+srv://admin:synchrone@synchrone-contract-inte.8otpltf.mongodb.net/contract_intelligence?retryWrites=true&w=majority&appName=synchrone-contract-intelligence")
        
        client = AsyncIOMotorClient(mongodb_url)
        db = client.contract_intelligence
        
        # Test connection
        try:
            await client.admin.command('ping')
            print("✅ MongoDB Atlas connection successful")
        except Exception as e:
            pytest.fail(f"Failed to connect to MongoDB Atlas: {e}")
        
        yield db
        await client.close()
    
    @pytest.fixture
    def sample_contract_data(self):
        """Sample contract data for testing"""
        return {
            "id": "test_contract_123",
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
    
    @pytest.fixture
    def sample_parsed_data(self):
        """Sample parsed contract data"""
        return ContractData(
            parties=[
                Party(
                    name="Acme Corporation",
                    role="customer",
                    email="contact@acme.com",
                    phone="+1-555-0123",
                    address="123 Business St, City, State 12345",
                    legal_entity="Corporation",
                    registration_number="123456789"
                ),
                Party(
                    name="Tech Solutions Inc",
                    role="vendor",
                    email="sales@techsolutions.com",
                    phone="+1-555-0456",
                    address="456 Tech Ave, Tech City, TC 54321",
                    legal_entity="LLC",
                    registration_number="987654321"
                )
            ],
            account_info={
                "contact_email": "billing@acme.com",
                "account_number": "ACC-12345",
                "billing_address": "123 Business St, City, State 12345"
            },
            financial_details=FinancialDetails(
                total_contract_value=50000.0,
                currency="USD",
                line_items=[
                    {
                        "description": "Software License",
                        "quantity": 1,
                        "unit_price": 25000.0,
                        "total_price": 25000.0
                    },
                    {
                        "description": "Support Services",
                        "quantity": 12,
                        "unit_price": 2000.0,
                        "total_price": 24000.0
                    }
                ],
                tax_amount=5000.0,
                additional_fees=1000.0
            ),
            payment_terms={
                "payment_terms": "Net 30",
                "payment_schedule": "Monthly",
                "due_dates": ["2024-01-15", "2024-02-15"],
                "payment_methods": ["Bank Transfer", "Check"]
            },
            revenue_classification={
                "payment_type": "recurring",
                "billing_cycle": "Monthly",
                "subscription_model": "SaaS",
                "auto_renewal": True
            },
            sla={
                "performance_metrics": ["99.9% uptime", "< 2s response time"],
                "support_terms": "24/7 support available",
                "maintenance_terms": "Monthly maintenance windows"
            },
            contract_start_date="2024-01-01",
            contract_end_date="2024-12-31",
            contract_type="Service Agreement",
            confidence_scores={
                "financial_completeness": 95,
                "party_identification": 90,
                "payment_terms_clarity": 85,
                "sla_definition": 80,
                "contact_information": 75
            },
            key_value_pairs=[
                {
                    "key": "Contract Duration",
                    "value": "12 months",
                    "confidence": 95,
                    "field_type": "duration"
                },
                {
                    "key": "Renewal Terms",
                    "value": "Automatic renewal",
                    "confidence": 90,
                    "field_type": "terms"
                }
            ],
            risk_factors=[
                "High contract value",
                "Long-term commitment",
                "Auto-renewal clause"
            ],
            compliance_issues=[
                "Missing termination clause",
                "Unclear penalty terms"
            ],
            important_dates=[
                {"date": "2024-01-01", "description": "Contract start"},
                {"date": "2024-12-31", "description": "Contract end"},
                {"date": "2024-11-01", "description": "Renewal notice deadline"}
            ],
            processing_notes=[
                "Successfully extracted all parties",
                "Financial data complete",
                "SLA terms identified"
            ],
            clauses=[
                "Service Level Agreement",
                "Payment Terms",
                "Termination Clause",
                "Confidentiality Agreement"
            ],
            document_metadata={
                "total_pages": 15,
                "file_size": 1024000
            },
            summary={
                "overview": "Software licensing and support agreement between Acme Corporation and Tech Solutions Inc",
                "parties_involved": ["Acme Corporation", "Tech Solutions Inc"],
                "key_terms": ["12-month term", "Monthly billing", "99.9% uptime SLA"],
                "financial_summary": "Total contract value: $50,000 with monthly payments of $4,167",
                "contract_duration": "12 months",
                "main_obligations": ["Software delivery", "Support services", "SLA compliance"],
                "risk_level": "Medium",
                "compliance_status": "Good"
            }
        )
    
    @pytest.mark.asyncio
    async def test_atlas_connection(self, db_client):
        """Test MongoDB Atlas connection"""
        # Test basic connection
        result = await db_client.command("ping")
        assert result["ok"] == 1
        
        # Test database access
        collections = await db_client.list_collection_names()
        print(f"Available collections: {collections}")
        
        # Test write operation
        test_collection = db_client.test_connection
        result = await test_collection.insert_one({"test": "connection", "timestamp": datetime.utcnow()})
        assert result.inserted_id is not None
        
        # Clean up
        await test_collection.delete_one({"_id": result.inserted_id})
        print("✅ MongoDB Atlas connection test passed")
    
    @pytest.mark.asyncio
    async def test_contract_insertion(self, db_client, sample_contract_data):
        """Test inserting contract data into Atlas"""
        contracts_collection = db_client.contracts
        
        # Insert contract
        result = await contracts_collection.insert_one(sample_contract_data)
        assert result.inserted_id is not None
        print(f"✅ Contract inserted with ID: {result.inserted_id}")
        
        # Verify insertion
        inserted_contract = await contracts_collection.find_one({"_id": result.inserted_id})
        assert inserted_contract is not None
        assert inserted_contract["id"] == sample_contract_data["id"]
        assert inserted_contract["filename"] == sample_contract_data["filename"]
        assert inserted_contract["file_path"] == sample_contract_data["file_path"]
        
        # Clean up
        await contracts_collection.delete_one({"_id": result.inserted_id})
        print("✅ Contract insertion test passed")
    
    @pytest.mark.asyncio
    async def test_parsed_data_storage(self, db_client, sample_contract_data, sample_parsed_data):
        """Test storing parsed contract data in Atlas"""
        contracts_collection = db_client.contracts
        
        # Insert contract with parsed data
        sample_contract_data["parsed_data"] = sample_parsed_data.dict()
        sample_contract_data["status"] = ContractStatus.COMPLETED
        sample_contract_data["score"] = 85.5
        
        result = await contracts_collection.insert_one(sample_contract_data)
        assert result.inserted_id is not None
        
        # Verify parsed data storage
        stored_contract = await contracts_collection.find_one({"_id": result.inserted_id})
        assert stored_contract is not None
        assert stored_contract["parsed_data"] is not None
        assert stored_contract["status"] == "completed"
        assert stored_contract["score"] == 85.5
        
        # Verify specific parsed data fields
        parsed_data = stored_contract["parsed_data"]
        assert len(parsed_data["parties"]) == 2
        assert parsed_data["financial_details"]["total_contract_value"] == 50000.0
        assert len(parsed_data["key_value_pairs"]) == 2
        assert len(parsed_data["risk_factors"]) == 3
        
        # Clean up
        await contracts_collection.delete_one({"_id": result.inserted_id})
        print("✅ Parsed data storage test passed")
    
    @pytest.mark.asyncio
    async def test_contract_queries(self, db_client, sample_contract_data):
        """Test various contract queries on Atlas"""
        contracts_collection = db_client.contracts
        
        # Insert multiple test contracts
        test_contracts = []
        for i in range(3):
            contract = sample_contract_data.copy()
            contract["id"] = f"test_contract_{i}"
            contract["filename"] = f"test_contract_{i}.pdf"
            contract["score"] = 70 + (i * 10)
            contract["status"] = ContractStatus.COMPLETED if i < 2 else ContractStatus.PROCESSING
            
            result = await contracts_collection.insert_one(contract)
            test_contracts.append(result.inserted_id)
        
        # Test query by status
        completed_contracts = await contracts_collection.find({"status": "completed"}).to_list(length=None)
        assert len(completed_contracts) == 2
        
        # Test query by score range
        high_score_contracts = await contracts_collection.find({"score": {"$gte": 80}}).to_list(length=None)
        assert len(high_score_contracts) == 1
        
        # Test sorting by score
        sorted_contracts = await contracts_collection.find({}).sort("score", -1).to_list(length=None)
        assert sorted_contracts[0]["score"] == 90
        
        # Test aggregation
        pipeline = [
            {"$group": {"_id": "$status", "count": {"$sum": 1}}}
        ]
        status_counts = await contracts_collection.aggregate(pipeline).to_list(length=None)
        assert len(status_counts) == 2
        
        # Clean up
        for contract_id in test_contracts:
            await contracts_collection.delete_one({"_id": contract_id})
        print("✅ Contract queries test passed")
    
    @pytest.mark.asyncio
    async def test_scoring_integration(self, db_client, sample_contract_data, sample_parsed_data):
        """Test scoring engine integration with Atlas"""
        contracts_collection = db_client.contracts
        
        # Insert contract with parsed data
        sample_contract_data["parsed_data"] = sample_parsed_data.dict()
        result = await contracts_collection.insert_one(sample_contract_data)
        
        # Test scoring engine
        scoring_engine = ScoringEngine()
        score, gaps = scoring_engine.calculate_score(sample_parsed_data.dict())
        
        assert score > 0
        assert isinstance(gaps, list)
        print(f"✅ Calculated score: {score}, Gaps: {len(gaps)}")
        
        # Update contract with score
        await contracts_collection.update_one(
            {"_id": result.inserted_id},
            {"$set": {"score": score, "gaps": gaps}}
        )
        
        # Verify score storage
        updated_contract = await contracts_collection.find_one({"_id": result.inserted_id})
        assert updated_contract["score"] == score
        assert len(updated_contract["gaps"]) == len(gaps)
        
        # Clean up
        await contracts_collection.delete_one({"_id": result.inserted_id})
        print("✅ Scoring integration test passed")
    
    @pytest.mark.asyncio
    async def test_file_path_storage(self, db_client, sample_contract_data):
        """Test PDF file path storage in Atlas"""
        contracts_collection = db_client.contracts
        
        # Test file path storage
        file_path = "/uploads/contract_123.pdf"
        sample_contract_data["file_path"] = file_path
        
        result = await contracts_collection.insert_one(sample_contract_data)
        
        # Verify file path storage
        stored_contract = await contracts_collection.find_one({"_id": result.inserted_id})
        assert stored_contract["file_path"] == file_path
        
        # Test file path retrieval
        contract_by_path = await contracts_collection.find_one({"file_path": file_path})
        assert contract_by_path is not None
        assert contract_by_path["id"] == sample_contract_data["id"]
        
        # Clean up
        await contracts_collection.delete_one({"_id": result.inserted_id})
        print("✅ File path storage test passed")
    
    @pytest.mark.asyncio
    async def test_bulk_operations(self, db_client):
        """Test bulk operations on Atlas"""
        contracts_collection = db_client.contracts
        
        # Prepare bulk data
        bulk_contracts = []
        for i in range(5):
            contract = {
                "id": f"bulk_contract_{i}",
                "filename": f"bulk_contract_{i}.pdf",
                "file_path": f"/uploads/bulk_contract_{i}.pdf",
                "status": ContractStatus.PENDING,
                "uploaded_at": datetime.utcnow(),
                "file_size": 1000000 + (i * 100000),
                "progress": 0,
                "score": None,
                "gaps": [],
                "error_message": None,
                "parsed_data": None
            }
            bulk_contracts.append(contract)
        
        # Test bulk insert
        result = await contracts_collection.insert_many(bulk_contracts)
        assert len(result.inserted_ids) == 5
        
        # Test bulk update
        update_result = await contracts_collection.update_many(
            {"id": {"$regex": "bulk_contract_"}},
            {"$set": {"status": ContractStatus.COMPLETED}}
        )
        assert update_result.modified_count == 5
        
        # Test bulk query
        bulk_contracts_found = await contracts_collection.find(
            {"id": {"$regex": "bulk_contract_"}}
        ).to_list(length=None)
        assert len(bulk_contracts_found) == 5
        
        # Test bulk delete
        delete_result = await contracts_collection.delete_many(
            {"id": {"$regex": "bulk_contract_"}}
        )
        assert delete_result.deleted_count == 5
        
        print("✅ Bulk operations test passed")
    
    @pytest.mark.asyncio
    async def test_index_creation(self, db_client):
        """Test index creation for performance optimization"""
        contracts_collection = db_client.contracts
        
        # Create indexes for common queries
        indexes = [
            ("id", 1),  # Unique index on contract ID
            ("status", 1),  # Index on status for filtering
            ("score", -1),  # Index on score for sorting
            ("uploaded_at", -1),  # Index on upload date for sorting
            ("filename", 1),  # Index on filename for searching
        ]
        
        for field, direction in indexes:
            if field == "id":
                await contracts_collection.create_index(field, unique=True)
            else:
                await contracts_collection.create_index(field)
        
        # Verify indexes
        index_list = await contracts_collection.list_indexes().to_list(length=None)
        index_names = [idx["name"] for idx in index_list]
        
        for field, _ in indexes:
            assert f"{field}_1" in index_names or f"{field}_-1" in index_names
        
        print("✅ Index creation test passed")
    
    @pytest.mark.asyncio
    async def test_data_consistency(self, db_client, sample_contract_data, sample_parsed_data):
        """Test data consistency and integrity"""
        contracts_collection = db_client.contracts
        
        # Insert contract with complete data
        sample_contract_data["parsed_data"] = sample_parsed_data.dict()
        sample_contract_data["status"] = ContractStatus.COMPLETED
        sample_contract_data["score"] = 85.5
        
        result = await contracts_collection.insert_one(sample_contract_data)
        
        # Test data consistency
        stored_contract = await contracts_collection.find_one({"_id": result.inserted_id})
        
        # Verify all required fields are present
        required_fields = ["id", "filename", "file_path", "status", "uploaded_at", "parsed_data"]
        for field in required_fields:
            assert field in stored_contract, f"Missing required field: {field}"
        
        # Verify data types
        assert isinstance(stored_contract["id"], str)
        assert isinstance(stored_contract["filename"], str)
        assert isinstance(stored_contract["file_path"], str)
        assert stored_contract["status"] in ["pending", "processing", "completed", "failed"]
        assert isinstance(stored_contract["uploaded_at"], datetime)
        assert isinstance(stored_contract["parsed_data"], dict)
        
        # Verify parsed data structure
        parsed_data = stored_contract["parsed_data"]
        assert "parties" in parsed_data
        assert "financial_details" in parsed_data
        assert "confidence_scores" in parsed_data
        
        # Clean up
        await contracts_collection.delete_one({"_id": result.inserted_id})
        print("✅ Data consistency test passed")


if __name__ == "__main__":
    # Run tests directly
    import sys
    sys.path.append('.')
    
    async def run_tests():
        test_instance = TestMongoDBAtlas()
        
        # Create fixtures
        db_client = await test_instance.db_client().__anext__()
        sample_contract_data = test_instance.sample_contract_data()
        sample_parsed_data = test_instance.sample_parsed_data()
        
        try:
            # Run all tests
            await test_instance.test_atlas_connection(db_client)
            await test_instance.test_contract_insertion(db_client, sample_contract_data)
            await test_instance.test_parsed_data_storage(db_client, sample_contract_data, sample_parsed_data)
            await test_instance.test_contract_queries(db_client, sample_contract_data)
            await test_instance.test_scoring_integration(db_client, sample_contract_data, sample_parsed_data)
            await test_instance.test_file_path_storage(db_client, sample_contract_data)
            await test_instance.test_bulk_operations(db_client)
            await test_instance.test_index_creation(db_client)
            await test_instance.test_data_consistency(db_client, sample_contract_data, sample_parsed_data)
            
            print("\n🎉 All MongoDB Atlas tests passed successfully!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            raise
        finally:
            # Close connection
            await db_client.client.close()
    
    # Run the tests
    asyncio.run(run_tests())
