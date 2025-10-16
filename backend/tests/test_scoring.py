import pytest
from app.scoring import ScoringEngine

class TestScoringEngine:
    def setup_method(self):
        self.scoring_engine = ScoringEngine()

    def test_init(self):
        """Test scoring engine initialization"""
        assert self.scoring_engine is not None
        assert hasattr(self.scoring_engine, 'weights')
        assert hasattr(self.scoring_engine, 'critical_fields')
        
        # Check weights sum to 100
        total_weight = sum(self.scoring_engine.weights.values())
        assert total_weight == 100

    def test_calculate_financial_score_complete(self):
        """Test financial score calculation with complete data"""
        financial_details = {
            "total_contract_value": 50000,
            "line_items": [
                {"description": "Software License", "unit_price": 2000, "quantity": 10},
                {"description": "Support", "unit_price": 1000, "quantity": 5}
            ],
            "currency": "USD",
            "tax_amount": 5000,
            "additional_fees": 1000
        }
        
        score = self.scoring_engine._calculate_financial_score(financial_details)
        
        # Should get high score for complete data
        assert score >= 80
        assert score <= 100

    def test_calculate_financial_score_partial(self):
        """Test financial score calculation with partial data"""
        financial_details = {
            "total_contract_value": 50000,
            "currency": "USD"
        }
        
        score = self.scoring_engine._calculate_financial_score(financial_details)
        
        # Should get moderate score for partial data
        assert score >= 40
        assert score < 80

    def test_calculate_financial_score_empty(self):
        """Test financial score calculation with no data"""
        financial_details = {}
        
        score = self.scoring_engine._calculate_financial_score(financial_details)
        
        assert score == 0

    def test_calculate_party_score_complete(self):
        """Test party score calculation with complete data"""
        parties = [
            {
                "name": "ABC Company Inc.",
                "role": "customer",
                "email": "contact@abc.com",
                "phone": "(555) 123-4567",
                "address": "123 Main St",
                "legal_entity": "ABC Company Inc.",
                "registration_number": "REG123"
            },
            {
                "name": "XYZ Corporation",
                "role": "vendor",
                "email": "sales@xyz.com",
                "phone": "(555) 987-6543"
            }
        ]
        
        score = self.scoring_engine._calculate_party_score(parties)
        
        # Should get high score for complete data
        assert score >= 80
        assert score <= 100

    def test_calculate_party_score_partial(self):
        """Test party score calculation with partial data"""
        parties = [
            {
                "name": "ABC Company Inc.",
                "role": "customer"
            }
        ]
        
        score = self.scoring_engine._calculate_party_score(parties)
        
        # Should get moderate score for partial data
        assert score >= 20
        assert score < 80

    def test_calculate_party_score_empty(self):
        """Test party score calculation with no parties"""
        parties = []
        
        score = self.scoring_engine._calculate_party_score(parties)
        
        assert score == 0

    def test_calculate_payment_score_complete(self):
        """Test payment score calculation with complete data"""
        payment_terms = {
            "payment_terms": "Net 30",
            "payment_schedule": "Monthly",
            "due_dates": ["2023-01-15", "2023-02-15"],
            "payment_methods": ["Bank Transfer", "Check"],
            "banking_details": "Account: 123456789"
        }
        
        score = self.scoring_engine._calculate_payment_score(payment_terms)
        
        # Should get high score for complete data
        assert score >= 80
        assert score <= 100

    def test_calculate_payment_score_partial(self):
        """Test payment score calculation with partial data"""
        payment_terms = {
            "payment_terms": "Net 30"
        }
        
        score = self.scoring_engine._calculate_payment_score(payment_terms)
        
        # Should get moderate score for partial data
        assert score >= 40
        assert score < 80

    def test_calculate_sla_score_complete(self):
        """Test SLA score calculation with complete data"""
        sla = {
            "performance_metrics": ["99.9% uptime", "< 2s response time"],
            "penalty_clauses": ["$100 per hour downtime"],
            "support_terms": "24/7 support available",
            "maintenance_terms": "Monthly maintenance windows"
        }
        
        score = self.scoring_engine._calculate_sla_score(sla)
        
        # Should get high score for complete data
        assert score >= 80
        assert score <= 100

    def test_calculate_contact_score_complete(self):
        """Test contact score calculation with complete data"""
        account_info = {
            "contact_email": "billing@company.com",
            "contact_phone": "(555) 123-4567",
            "technical_support_contact": "support@company.com"
        }
        
        parties = [
            {
                "name": "ABC Company",
                "email": "contact@abc.com",
                "phone": "(555) 987-6543"
            }
        ]
        
        score = self.scoring_engine._calculate_contact_score(account_info, parties)
        
        # Should get high score for complete data
        assert score >= 80
        assert score <= 100

    def test_identify_gaps_complete_data(self):
        """Test gap identification with complete data"""
        parsed_data = {
            "parties": [
                {"name": "ABC Company", "role": "customer"}
            ],
            "financial_details": {
                "total_contract_value": 50000,
                "line_items": [{"description": "Service", "unit_price": 1000}]
            },
            "payment_terms": {
                "payment_terms": "Net 30"
            },
            "account_info": {
                "contact_email": "billing@company.com"
            },
            "revenue_classification": {
                "payment_type": "recurring"
            },
            "sla": {
                "performance_metrics": ["uptime"],
                "support_terms": "24/7 support"
            },
            "contract_start_date": "2023-01-01",
            "contract_end_date": "2023-12-31"
        }
        
        gaps = self.scoring_engine._identify_gaps(parsed_data)
        
        # Should have minimal gaps for complete data
        assert len(gaps) <= 2

    def test_identify_gaps_missing_data(self):
        """Test gap identification with missing data"""
        parsed_data = {
            "parties": [],
            "financial_details": None,
            "payment_terms": None,
            "account_info": None,
            "revenue_classification": None,
            "sla": None
        }
        
        gaps = self.scoring_engine._identify_gaps(parsed_data)
        
        # Should identify many gaps for missing data
        assert len(gaps) >= 5
        assert any("No contract parties" in gap for gap in gaps)
        assert any("No financial details" in gap for gap in gaps)
        assert any("No payment terms" in gap for gap in gaps)

    def test_calculate_score_integration(self):
        """Test full score calculation integration"""
        parsed_data = {
            "parties": [
                {"name": "ABC Company", "role": "customer", "email": "contact@abc.com"}
            ],
            "financial_details": {
                "total_contract_value": 50000,
                "line_items": [{"description": "Service", "unit_price": 1000, "quantity": 1}],
                "currency": "USD"
            },
            "payment_terms": {
                "payment_terms": "Net 30",
                "payment_schedule": "Monthly"
            },
            "account_info": {
                "contact_email": "billing@company.com",
                "contact_phone": "(555) 123-4567"
            },
            "revenue_classification": {
                "payment_type": "recurring",
                "billing_cycle": "Monthly"
            },
            "sla": {
                "performance_metrics": ["99.9% uptime"],
                "support_terms": "24/7 support"
            },
            "contract_start_date": "2023-01-01",
            "contract_end_date": "2023-12-31"
        }
        
        score, gaps = self.scoring_engine.calculate_score(parsed_data)
        
        # Should get a good overall score
        assert score >= 60
        assert score <= 100
        
        # Should have minimal gaps
        assert len(gaps) <= 3

    def test_get_score_breakdown(self):
        """Test detailed score breakdown"""
        parsed_data = {
            "parties": [{"name": "ABC Company", "role": "customer"}],
            "financial_details": {"total_contract_value": 50000},
            "payment_terms": {"payment_terms": "Net 30"},
            "account_info": {"contact_email": "billing@company.com"},
            "revenue_classification": {"payment_type": "recurring"},
            "sla": {"performance_metrics": ["uptime"]}
        }
        
        breakdown = self.scoring_engine.get_score_breakdown(parsed_data)
        
        assert "overall_score" in breakdown
        assert "component_scores" in breakdown
        assert "gaps" in breakdown
        assert "total_possible_score" in breakdown
        
        # Check component scores
        component_scores = breakdown["component_scores"]
        assert "financial_completeness" in component_scores
        assert "party_identification" in component_scores
        assert "payment_terms_clarity" in component_scores
        assert "sla_definition" in component_scores
        assert "contact_information" in component_scores
        
        # Each component should have score, weight, and max_points
        for component in component_scores.values():
            assert "score" in component
            assert "weight" in component
            assert "max_points" in component
            assert 0 <= component["score"] <= 100
