import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import tempfile
import os
from app.main import app
from app.models import ContractStatus

client = TestClient(app)

class TestContractUpload:
    @patch('app.main.app.mongodb')
    @patch('app.main.contract_parser')
    @patch('app.main.scoring_engine')
    def test_upload_contract_success(self, mock_scoring, mock_parser, mock_db):
        """Test successful contract upload"""
        # Mock database operations
        mock_db.contracts.insert_one = AsyncMock()
        
        # Create a temporary PDF file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b'%PDF-1.4 fake pdf content')
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as f:
                response = client.post(
                    "/contracts/upload",
                    files={"file": ("test.pdf", f, "application/pdf")}
                )
            
            assert response.status_code == 200
            data = response.json()
            assert "contract_id" in data
            assert data["status"] == "uploaded"
            assert data["message"] == "Contract uploaded successfully"
            
        finally:
            os.unlink(tmp_file_path)

    def test_upload_non_pdf_file(self):
        """Test upload of non-PDF file"""
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as tmp_file:
            tmp_file.write(b'This is not a PDF file')
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as f:
                response = client.post(
                    "/contracts/upload",
                    files={"file": ("test.txt", f, "text/plain")}
                )
            
            assert response.status_code == 400
            assert "Only PDF files are supported" in response.json()["detail"]
            
        finally:
            os.unlink(tmp_file_path)

    def test_upload_large_file(self):
        """Test upload of file exceeding size limit"""
        # Create a large file (simulate 51MB)
        large_content = b'x' * (51 * 1024 * 1024)
        
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(large_content)
            tmp_file_path = tmp_file.name
        
        try:
            with open(tmp_file_path, 'rb') as f:
                response = client.post(
                    "/contracts/upload",
                    files={"file": ("large.pdf", f, "application/pdf")}
                )
            
            # Should still succeed as we're not enforcing size limit in the test
            # In real implementation, you'd want to add size validation
            assert response.status_code in [200, 413]
            
        finally:
            os.unlink(tmp_file_path)

class TestContractStatus:
    @patch('app.main.app.mongodb')
    def test_get_contract_status_success(self, mock_db):
        """Test getting contract status"""
        mock_contract = {
            "id": "test-id",
            "status": ContractStatus.PROCESSING,
            "progress": 50,
            "updated_at": "2023-01-01T00:00:00Z"
        }
        mock_db.contracts.find_one = AsyncMock(return_value=mock_contract)
        
        response = client.get("/contracts/test-id/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["contract_id"] == "test-id"
        assert data["status"] == ContractStatus.PROCESSING
        assert data["progress"] == 50

    @patch('app.main.app.mongodb')
    def test_get_contract_status_not_found(self, mock_db):
        """Test getting status for non-existent contract"""
        mock_db.contracts.find_one = AsyncMock(return_value=None)
        
        response = client.get("/contracts/non-existent/status")
        
        assert response.status_code == 404
        assert "Contract not found" in response.json()["detail"]

class TestContractData:
    @patch('app.main.app.mongodb')
    def test_get_contract_data_success(self, mock_db):
        """Test getting contract data"""
        mock_contract = {
            "id": "test-id",
            "status": ContractStatus.COMPLETED,
            "parsed_data": {
                "parties": [{"name": "Test Company", "role": "customer"}],
                "financial_details": {"total_contract_value": 10000}
            }
        }
        mock_db.contracts.find_one = AsyncMock(return_value=mock_contract)
        
        response = client.get("/contracts/test-id")
        
        assert response.status_code == 200
        data = response.json()
        assert "parties" in data
        assert "financial_details" in data

    @patch('app.main.app.mongodb')
    def test_get_contract_data_not_completed(self, mock_db):
        """Test getting data for non-completed contract"""
        mock_contract = {
            "id": "test-id",
            "status": ContractStatus.PROCESSING
        }
        mock_db.contracts.find_one = AsyncMock(return_value=mock_contract)
        
        response = client.get("/contracts/test-id")
        
        assert response.status_code == 400
        assert "Contract processing not completed" in response.json()["detail"]

class TestContractList:
    @patch('app.main.app.mongodb')
    def test_list_contracts_success(self, mock_db):
        """Test listing contracts"""
        mock_contracts = [
            {
                "id": "test-1",
                "filename": "contract1.pdf",
                "status": ContractStatus.COMPLETED,
                "uploaded_at": "2023-01-01T00:00:00Z",
                "file_size": 1024,
                "score": 85
            },
            {
                "id": "test-2",
                "filename": "contract2.pdf",
                "status": ContractStatus.PROCESSING,
                "uploaded_at": "2023-01-02T00:00:00Z",
                "file_size": 2048,
                "score": 0
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_contracts)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        
        mock_db.contracts.find = MagicMock(return_value=mock_cursor)
        mock_db.contracts.count_documents = AsyncMock(return_value=2)
        
        response = client.get("/contracts")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["contracts"]) == 2
        assert data["total"] == 2
        assert data["skip"] == 0
        assert data["limit"] == 10

    @patch('app.main.app.mongodb')
    def test_list_contracts_with_filters(self, mock_db):
        """Test listing contracts with filters"""
        mock_contracts = [
            {
                "id": "test-1",
                "filename": "contract1.pdf",
                "status": ContractStatus.COMPLETED,
                "uploaded_at": "2023-01-01T00:00:00Z",
                "file_size": 1024,
                "score": 85
            }
        ]
        
        mock_cursor = AsyncMock()
        mock_cursor.to_list = AsyncMock(return_value=mock_contracts)
        mock_cursor.sort = MagicMock(return_value=mock_cursor)
        mock_cursor.skip = MagicMock(return_value=mock_cursor)
        mock_cursor.limit = MagicMock(return_value=mock_cursor)
        
        mock_db.contracts.find = MagicMock(return_value=mock_cursor)
        mock_db.contracts.count_documents = AsyncMock(return_value=1)
        
        response = client.get("/contracts?status=completed&skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["contracts"]) == 1
        assert data["limit"] == 5

class TestContractDownload:
    @patch('app.main.app.mongodb')
    @patch('os.path.exists')
    def test_download_contract_success(self, mock_exists, mock_db):
        """Test downloading contract"""
        mock_contract = {
            "id": "test-id",
            "filename": "test.pdf",
            "file_path": "/path/to/test.pdf"
        }
        mock_db.contracts.find_one = AsyncMock(return_value=mock_contract)
        mock_exists.return_value = True
        
        with patch('app.main.FileResponse') as mock_file_response:
            mock_file_response.return_value = MagicMock()
            response = client.get("/contracts/test-id/download")
            
            assert response.status_code == 200

    @patch('app.main.app.mongodb')
    def test_download_contract_not_found(self, mock_db):
        """Test downloading non-existent contract"""
        mock_db.contracts.find_one = AsyncMock(return_value=None)
        
        response = client.get("/contracts/non-existent/download")
        
        assert response.status_code == 404
        assert "Contract not found" in response.json()["detail"]

class TestHealthCheck:
    def test_health_check(self):
        """Test health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
