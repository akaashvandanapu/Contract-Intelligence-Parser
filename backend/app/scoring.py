from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)

class ScoringEngine:
    def __init__(self):
        # Weighted scoring system as per requirements
        self.weights = {
            "financial_completeness": 30,
            "party_identification": 25,
            "payment_terms_clarity": 20,
            "sla_definition": 15,
            "contact_information": 10
        }
        
        # Critical fields for gap analysis
        self.critical_fields = {
            "parties": ["name", "role"],
            "financial_details": ["total_contract_value"],
            "payment_terms": ["payment_terms"],
            "account_info": ["contact_email"],
            "revenue_classification": ["payment_type"]
        }

    def calculate_score(self, parsed_data: Dict[str, Any]) -> tuple[float, List[str]]:
        """Calculate overall contract score and identify gaps"""
        try:
            scores = {}
            gaps = []
            
            # Calculate individual component scores
            scores["financial_completeness"] = self._calculate_financial_score(parsed_data)
            scores["party_identification"] = self._calculate_party_score(parsed_data)
            scores["payment_terms_clarity"] = self._calculate_payment_score(parsed_data)
            scores["sla_definition"] = self._calculate_sla_score(parsed_data)
            scores["contact_information"] = self._calculate_contact_score(parsed_data)
            
            # Calculate weighted overall score
            overall_score = sum(scores[component] * self.weights[component] / 100 for component in scores)
            
            # Identify gaps
            gaps = self._identify_gaps(parsed_data)
            
            logger.info(f"Contract scoring completed. Overall score: {overall_score:.2f}, Gaps: {len(gaps)}")
            
            return round(overall_score, 2), gaps
        
        except Exception as e:
            logger.error(f"Error calculating contract score: {str(e)}")
            return 0.0, [f"Scoring error: {str(e)}"]

    def _calculate_financial_score(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate financial completeness score (0-100)"""
        score = 0
        financial_details = parsed_data.get("financial_details")
        
        if not financial_details:
            return 0
        
        # Total contract value (40 points)
        if financial_details.get("total_contract_value"):
            score += 40
        
        # Line items (30 points)
        line_items = financial_details.get("line_items", [])
        if line_items:
            score += 30
            # Bonus for detailed line items
            for item in line_items:
                if item.get("description") and item.get("unit_price"):
                    score += 2
            score = min(score, 30)  # Cap at 30
        
        # Currency (10 points)
        if financial_details.get("currency"):
            score += 10
        
        # Tax information (10 points)
        if financial_details.get("tax_amount"):
            score += 10
        
        # Additional fees (10 points)
        if financial_details.get("additional_fees"):
            score += 10
        
        return min(score, 100)

    def _calculate_party_score(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate party identification score (0-100)"""
        score = 0
        parties = parsed_data.get("parties", [])
        
        if not parties:
            return 0
        
        # Base score for having parties (20 points)
        score += 20
        
        # Score per party (up to 3 parties)
        for i, party in enumerate(parties[:3]):
            party_score = 0
            
            # Name (required - 20 points)
            if party.get("name"):
                party_score += 20
            
            # Role (15 points)
            if party.get("role"):
                party_score += 15
            
            # Legal entity (15 points)
            if party.get("legal_entity"):
                party_score += 15
            
            # Contact information (10 points each)
            if party.get("email"):
                party_score += 10
            if party.get("phone"):
                party_score += 10
            
            # Address (10 points)
            if party.get("address"):
                party_score += 10
            
            # Registration details (10 points)
            if party.get("registration_number"):
                party_score += 10
            
            score += min(party_score, 80)  # Cap per party
        
        return min(score, 100)

    def _calculate_payment_score(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate payment terms clarity score (0-100)"""
        score = 0
        payment_terms = parsed_data.get("payment_terms")
        
        if not payment_terms:
            return 0
        
        # Payment terms (40 points)
        if payment_terms.get("payment_terms"):
            score += 40
        
        # Payment schedule (25 points)
        if payment_terms.get("payment_schedule"):
            score += 25
        
        # Due dates (20 points)
        due_dates = payment_terms.get("due_dates", [])
        if due_dates:
            score += 20
        
        # Payment methods (10 points)
        payment_methods = payment_terms.get("payment_methods", [])
        if payment_methods:
            score += 10
        
        # Banking details (5 points)
        if payment_terms.get("banking_details"):
            score += 5
        
        return min(score, 100)

    def _calculate_sla_score(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate SLA definition score (0-100)"""
        score = 0
        sla = parsed_data.get("sla")
        
        if not sla:
            return 0
        
        # Performance metrics (30 points)
        performance_metrics = sla.get("performance_metrics", [])
        if performance_metrics:
            score += 30
        
        # Penalty clauses (25 points)
        penalty_clauses = sla.get("penalty_clauses", [])
        if penalty_clauses:
            score += 25
        
        # Support terms (25 points)
        if sla.get("support_terms"):
            score += 25
        
        # Maintenance terms (20 points)
        if sla.get("maintenance_terms"):
            score += 20
        
        return min(score, 100)

    def _calculate_contact_score(self, parsed_data: Dict[str, Any]) -> float:
        """Calculate contact information score (0-100)"""
        score = 0
        
        # Account info contact details (50 points)
        account_info = parsed_data.get("account_info")
        if account_info:
            if account_info.get("contact_email"):
                score += 25
            if account_info.get("contact_phone"):
                score += 15
            if account_info.get("technical_support_contact"):
                score += 10
        
        # Party contact details (50 points)
        parties = parsed_data.get("parties", [])
        contact_found = False
        for party in parties:
            if party.get("email") or party.get("phone"):
                contact_found = True
                break
        
        if contact_found:
            score += 50
        
        return min(score, 100)

    def _identify_gaps(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Identify missing critical fields"""
        gaps = []
        
        # Check parties
        parties = parsed_data.get("parties", [])
        if not parties:
            gaps.append("No contract parties identified")
        else:
            for i, party in enumerate(parties):
                if not party.get("name"):
                    gaps.append(f"Party {i+1}: Missing name")
                if not party.get("role"):
                    gaps.append(f"Party {i+1}: Missing role")
        
        # Check financial details
        financial_details = parsed_data.get("financial_details")
        if not financial_details:
            gaps.append("No financial details found")
        else:
            if not financial_details.get("total_contract_value"):
                gaps.append("Missing total contract value")
            if not financial_details.get("line_items"):
                gaps.append("No line items found")
        
        # Check payment terms
        payment_terms = parsed_data.get("payment_terms")
        if not payment_terms:
            gaps.append("No payment terms found")
        else:
            if not payment_terms.get("payment_terms"):
                gaps.append("Missing payment terms (Net 30, Net 60, etc.)")
        
        # Check account info
        account_info = parsed_data.get("account_info")
        if not account_info:
            gaps.append("No account information found")
        else:
            if not account_info.get("contact_email"):
                gaps.append("Missing contact email")
        
        # Check revenue classification
        revenue_classification = parsed_data.get("revenue_classification")
        if not revenue_classification:
            gaps.append("No revenue classification found")
        else:
            if not revenue_classification.get("payment_type"):
                gaps.append("Missing payment type (recurring/one-time)")
        
        # Check SLA
        sla = parsed_data.get("sla")
        if not sla:
            gaps.append("No SLA information found")
        else:
            if not sla.get("performance_metrics"):
                gaps.append("No performance metrics defined")
            if not sla.get("support_terms"):
                gaps.append("No support terms defined")
        
        # Check contract dates
        if not parsed_data.get("contract_start_date"):
            gaps.append("Missing contract start date")
        if not parsed_data.get("contract_end_date"):
            gaps.append("Missing contract end date")
        
        return gaps

    def get_score_breakdown(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Get detailed score breakdown for analysis"""
        scores = {}
        gaps = []
        
        # Calculate individual component scores
        scores["financial_completeness"] = {
            "score": self._calculate_financial_score(parsed_data),
            "weight": self.weights["financial_completeness"],
            "max_points": 100
        }
        
        scores["party_identification"] = {
            "score": self._calculate_party_score(parsed_data),
            "weight": self.weights["party_identification"],
            "max_points": 100
        }
        
        scores["payment_terms_clarity"] = {
            "score": self._calculate_payment_score(parsed_data),
            "weight": self.weights["payment_terms_clarity"],
            "max_points": 100
        }
        
        scores["sla_definition"] = {
            "score": self._calculate_sla_score(parsed_data),
            "weight": self.weights["sla_definition"],
            "max_points": 100
        }
        
        scores["contact_information"] = {
            "score": self._calculate_contact_score(parsed_data),
            "weight": self.weights["contact_information"],
            "max_points": 100
        }
        
        # Calculate weighted overall score
        overall_score = sum(
            scores[component]["score"] * scores[component]["weight"] / 100 
            for component in scores
        )
        
        # Identify gaps
        gaps = self._identify_gaps(parsed_data)
        
        return {
            "overall_score": round(overall_score, 2),
            "component_scores": scores,
            "gaps": gaps,
            "total_possible_score": 100
        }
