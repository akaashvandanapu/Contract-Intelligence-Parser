import pytest
from unittest.mock import patch, MagicMock
from app.parser import ContractParser

class TestContractParser:
    def setup_method(self):
        self.parser = ContractParser()

    def test_init(self):
        """Test parser initialization"""
        assert self.parser is not None
        assert hasattr(self.parser, 'patterns')
        assert 'email' in self.parser.patterns
        assert 'phone' in self.parser.patterns
        assert 'currency' in self.parser.patterns

    @patch('app.parser.PyPDF2.PdfReader')
    async def test_extract_text_from_pdf(self, mock_pdf_reader):
        """Test PDF text extraction"""
        # Mock PDF reader
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Sample contract text"
        mock_reader = MagicMock()
        mock_reader.pages = [mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b'%PDF-1.4 fake pdf content')
            tmp_file_path = tmp_file.name
        
        try:
            text = await self.parser._extract_text_from_pdf(tmp_file_path)
            assert text == "Sample contract text\n"
        finally:
            import os
            os.unlink(tmp_file_path)

    def test_extract_parties(self):
        """Test party extraction"""
        text = """
        This agreement is between ABC Company Inc. and XYZ Corporation.
        Party 1: ABC Company Inc.
        Party 2: XYZ Corporation
        Customer: ABC Company Inc.
        Vendor: XYZ Corporation
        """
        
        parties = self.parser._extract_parties(text)
        
        assert len(parties) > 0
        # Should extract at least some parties
        party_names = [party.name for party in parties]
        assert any("ABC Company" in name for name in party_names)
        assert any("XYZ Corporation" in name for name in party_names)

    def test_extract_account_info(self):
        """Test account information extraction"""
        text = """
        Account Number: ACC123456
        Billing Address: 123 Main St, City, State 12345
        Contact Email: billing@company.com
        Contact Phone: (555) 123-4567
        """
        
        account_info = self.parser._extract_account_info(text)
        
        assert account_info is not None
        assert account_info.account_number == "ACC123456"
        assert "123 Main St" in account_info.billing_address
        assert account_info.contact_email == "billing@company.com"
        assert account_info.contact_phone == "(555) 123-4567"

    def test_extract_financial_details(self):
        """Test financial details extraction"""
        text = """
        Total Contract Value: $50,000
        Line Items:
        - Software License: 10 x $2,000 = $20,000
        - Support Services: $5,000 each
        - Implementation: $25,000
        """
        
        financial_details = self.parser._extract_financial_details(text)
        
        assert financial_details is not None
        assert financial_details.total_contract_value == 50000
        assert len(financial_details.line_items) > 0
        
        # Check line items
        line_item_descriptions = [item.description for item in financial_details.line_items]
        assert any("Software License" in desc for desc in line_item_descriptions)

    def test_extract_payment_terms(self):
        """Test payment terms extraction"""
        text = """
        Payment Terms: Net 30
        Payment Schedule: Monthly
        Due Dates: 2023-01-15, 2023-02-15
        Payment Method: Bank Transfer
        """
        
        payment_terms = self.parser._extract_payment_terms(text)
        
        assert payment_terms is not None
        assert "Net 30" in payment_terms.payment_terms
        assert payment_terms.payment_schedule == "Monthly"
        assert len(payment_terms.due_dates) > 0
        assert len(payment_terms.payment_methods) > 0

    def test_extract_revenue_classification(self):
        """Test revenue classification extraction"""
        text = """
        This is a recurring subscription service.
        Billing Cycle: Monthly
        Subscription Model: SaaS
        Auto Renewal: Yes
        """
        
        revenue_classification = self.parser._extract_revenue_classification(text)
        
        assert revenue_classification is not None
        assert revenue_classification.payment_type == "recurring"
        assert revenue_classification.billing_cycle == "Monthly"
        assert revenue_classification.subscription_model == "SaaS"
        assert revenue_classification.auto_renewal is True

    def test_extract_sla(self):
        """Test SLA extraction"""
        text = """
        Service Level Agreement:
        Uptime: 99.9%
        Response Time: < 2 seconds
        Support Terms: 24/7 support available
        Maintenance Terms: Monthly maintenance windows
        Penalty: $100 per hour of downtime
        """
        
        sla = self.parser._extract_sla(text)
        
        assert sla is not None
        assert len(sla.performance_metrics) > 0
        assert sla.support_terms is not None
        assert sla.maintenance_terms is not None
        assert len(sla.penalty_clauses) > 0

    def test_extract_dates(self):
        """Test date extraction"""
        text = """
        Contract Start Date: 2023-01-01
        Effective Date: 01/01/2023
        Contract End Date: 2023-12-31
        Expiration Date: 12/31/2023
        """
        
        start_date = self.parser._extract_dates(text, "start")
        end_date = self.parser._extract_dates(text, "end")
        
        assert start_date is not None
        assert end_date is not None
        assert "2023-01-01" in start_date or "01/01/2023" in start_date
        assert "2023-12-31" in end_date or "12/31/2023" in end_date

    def test_extract_contract_type(self):
        """Test contract type extraction"""
        text = "This is a service agreement between the parties."
        
        contract_type = self.parser._extract_contract_type(text)
        
        assert contract_type == "Service Agreement"

    def test_calculate_confidence_scores(self):
        """Test confidence score calculation"""
        # Mock data
        parties = [MagicMock(name="Test Company", role="customer")]
        account_info = MagicMock(account_number="123", contact_email="test@test.com")
        financial_details = MagicMock(total_contract_value=10000, line_items=[MagicMock()])
        payment_terms = MagicMock(payment_terms="Net 30")
        revenue_classification = MagicMock(payment_type="recurring")
        sla = MagicMock(performance_metrics=["uptime"], support_terms="24/7")
        
        scores = self.parser._calculate_confidence_scores(
            parties, account_info, financial_details, 
            payment_terms, revenue_classification, sla
        )
        
        assert "party_identification" in scores
        assert "account_info" in scores
        assert "financial_details" in scores
        assert "payment_terms" in scores
        assert "revenue_classification" in scores
        assert "sla" in scores
        
        # All scores should be between 0 and 100
        for score in scores.values():
            assert 0 <= score <= 100

    @patch('app.parser.ContractParser._extract_text_from_pdf')
    async def test_parse_contract_integration(self, mock_extract_text):
        """Test full contract parsing integration"""
        # Mock text extraction
        mock_extract_text.return_value = """
        This agreement is between ABC Company Inc. and XYZ Corporation.
        Total Contract Value: $50,000
        Payment Terms: Net 30
        Contact Email: billing@company.com
        """
        
        # Create temporary file
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(b'%PDF-1.4 fake pdf content')
            tmp_file_path = tmp_file.name
        
        try:
            result = await self.parser.parse_contract(tmp_file_path)
            
            assert "parties" in result
            assert "financial_details" in result
            assert "payment_terms" in result
            assert "confidence_scores" in result
            
            # Check that confidence scores are calculated
            assert len(result["confidence_scores"]) > 0
            
        finally:
            import os
            os.unlink(tmp_file_path)
