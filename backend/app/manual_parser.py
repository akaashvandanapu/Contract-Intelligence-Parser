"""
Manual contract parser as fallback when AI is not available
Extracts data using regex patterns and text analysis
"""

import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

class ManualContractParser:
    """Manual contract parser using regex and text analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def parse_contract_text(self, text: str) -> Dict[str, Any]:
        """Parse contract text using manual extraction methods"""
        try:
            result = {
                "parties": self._extract_parties(text),
                "account_info": self._extract_account_info(text),
                "financial_details": self._extract_financial_details(text),
                "payment_terms": self._extract_payment_terms(text),
                "revenue_classification": self._extract_revenue_classification(text),
                "sla": self._extract_sla(text),
                "contract_start_date": self._extract_start_date(text),
                "contract_end_date": self._extract_end_date(text),
                "contract_type": self._extract_contract_type(text),
                "confidence_scores": self._calculate_confidence_scores(text),
                "key_terms": self._extract_key_terms(text),
                "obligations": self._extract_obligations(text),
                "risk_factors": self._extract_risk_factors(text),
                "compliance_issues": self._extract_compliance_issues(text),
                "summary": self._generate_summary(text)
            }
            
            self.logger.info("Manual contract parsing completed successfully")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in manual contract parsing: {str(e)}")
            return self._get_fallback_data()
    
    def _extract_parties(self, text: str) -> List[Dict[str, Any]]:
        """Extract parties from contract text"""
        parties = []
        
        # Look for service provider and customer sections
        service_provider_match = re.search(r'Service Provider:?\s*\n([^:]+?)(?=\n[A-Z]|\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        customer_match = re.search(r'Customer:?\s*\n([^:]+?)(?=\n[A-Z]|\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        
        if service_provider_match:
            provider_text = service_provider_match.group(1).strip()
            party = self._parse_party_info(provider_text, "vendor")
            if party:
                parties.append(party)
        
        if customer_match:
            customer_text = customer_match.group(1).strip()
            party = self._parse_party_info(customer_text, "customer")
            if party:
                parties.append(party)
        
        return parties
    
    def _parse_party_info(self, text: str, role: str) -> Optional[Dict[str, Any]]:
        """Parse individual party information"""
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        if not lines:
            return None
        
        party = {
            "name": lines[0] if lines else "",
            "role": role,
            "email": "",
            "phone": "",
            "address": "",
            "legal_entity": "",
            "registration_number": "",
            "tax_id": "",
            "website": "",
            "jurisdiction": ""
        }
        
        # Extract email
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        if email_match:
            party["email"] = email_match.group(1)
        
        # Extract phone
        phone_match = re.search(r'\(?(\d{3})\)?[-.\s]?(\d{3})[-.\s]?(\d{4})', text)
        if phone_match:
            party["phone"] = f"({phone_match.group(1)}) {phone_match.group(2)}-{phone_match.group(3)}"
        
        # Extract address (look for street address pattern)
        address_match = re.search(r'(\d+\s+[A-Za-z\s]+(?:Drive|Street|Avenue|Boulevard|Road|Lane|Way|Place|Court|Circle|Blvd|St|Ave|Rd|Ln|Dr|Pl|Ct|Cir))', text)
        if address_match:
            party["address"] = address_match.group(1)
        
        # Extract tax ID
        tax_id_match = re.search(r'Tax ID:?\s*([0-9-]+)', text, re.IGNORECASE)
        if tax_id_match:
            party["tax_id"] = tax_id_match.group(1)
        
        # Extract account number
        account_match = re.search(r'Account Number:?\s*([A-Z0-9-]+)', text, re.IGNORECASE)
        if account_match:
            party["registration_number"] = account_match.group(1)
        
        return party
    
    def _extract_account_info(self, text: str) -> Dict[str, Any]:
        """Extract account information"""
        account_info = {
            "contact_email": "",
            "account_number": "",
            "billing_address": "",
            "technical_contact": "",
            "account_manager": ""
        }
        
        # Extract billing contact
        billing_match = re.search(r'Billing Contact:?\s*\n([^:]+?)(?=\n[A-Z]|\n\n|$)', text, re.IGNORECASE | re.DOTALL)
        if billing_match:
            billing_text = billing_match.group(1)
            email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', billing_text)
            if email_match:
                account_info["contact_email"] = email_match.group(1)
        
        # Extract account number
        account_match = re.search(r'Account Number:?\s*([A-Z0-9-]+)', text, re.IGNORECASE)
        if account_match:
            account_info["account_number"] = account_match.group(1)
        
        return account_info
    
    def _extract_financial_details(self, text: str) -> Dict[str, Any]:
        """Extract financial details"""
        financial = {
            "total_contract_value": 0,
            "currency": "USD",
            "line_items": [],
            "tax_amount": 0,
            "additional_fees": 0
        }
        
        # Extract total contract value
        total_match = re.search(r'Total.*?(\$[\d,]+\.?\d*)', text, re.IGNORECASE)
        if total_match:
            value_str = total_match.group(1).replace('$', '').replace(',', '')
            try:
                financial["total_contract_value"] = float(value_str)
            except ValueError:
                pass
        
        # Extract annual contract value
        annual_match = re.search(r'Annual Contract Value:?\s*\$?([\d,]+\.?\d*)', text, re.IGNORECASE)
        if annual_match:
            value_str = annual_match.group(1).replace(',', '')
            try:
                financial["total_contract_value"] = float(value_str)
            except ValueError:
                pass
        
        # Extract line items
        line_items = self._extract_line_items(text)
        financial["line_items"] = line_items
        
        return financial
    
    def _extract_line_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from contract"""
        line_items = []
        
        # Look for service descriptions with quantities and prices
        service_pattern = r'(\d+)\s+(?:virtual servers?|user licenses?|hours?)\s*[×x]\s*\$?([\d,]+\.?\d*)'
        matches = re.findall(service_pattern, text, re.IGNORECASE)
        
        for quantity, price in matches:
            try:
                line_item = {
                    "description": f"Service item",
                    "quantity": int(quantity),
                    "unit_price": float(price.replace(',', '')),
                    "total_price": int(quantity) * float(price.replace(',', ''))
                }
                line_items.append(line_item)
            except ValueError:
                continue
        
        return line_items
    
    def _extract_payment_terms(self, text: str) -> Dict[str, Any]:
        """Extract payment terms"""
        payment_terms = {
            "payment_terms": "",
            "payment_schedule": "",
            "due_dates": [],
            "payment_methods": [],
            "banking_details": ""
        }
        
        # Extract payment terms
        net_match = re.search(r'Net\s+(\d+)', text, re.IGNORECASE)
        if net_match:
            payment_terms["payment_terms"] = f"Net {net_match.group(1)}"
        
        # Extract payment schedule
        if "monthly" in text.lower():
            payment_terms["payment_schedule"] = "Monthly"
        elif "quarterly" in text.lower():
            payment_terms["payment_schedule"] = "Quarterly"
        elif "annual" in text.lower():
            payment_terms["payment_schedule"] = "Annual"
        
        # Extract payment methods
        if "ACH" in text.upper():
            payment_terms["payment_methods"].append("ACH Transfer")
        if "bank transfer" in text.lower():
            payment_terms["payment_methods"].append("Bank Transfer")
        
        return payment_terms
    
    def _extract_revenue_classification(self, text: str) -> Dict[str, Any]:
        """Extract revenue classification"""
        revenue = {
            "payment_type": "recurring",
            "billing_cycle": "Monthly",
            "subscription_model": "Service",
            "renewal_terms": "",
            "auto_renewal": False
        }
        
        # Check for auto-renewal
        if "auto-renew" in text.lower() or "auto renew" in text.lower():
            revenue["auto_renewal"] = True
        
        # Determine payment type
        if "recurring" in text.lower() or "monthly" in text.lower():
            revenue["payment_type"] = "recurring"
        elif "one-time" in text.lower() or "setup" in text.lower():
            revenue["payment_type"] = "one-time"
        
        return revenue
    
    def _extract_sla(self, text: str) -> Dict[str, Any]:
        """Extract SLA information"""
        sla = {
            "performance_metrics": [],
            "benchmarks": [],
            "penalty_clauses": [],
            "remedies": [],
            "support_terms": "",
            "maintenance_terms": ""
        }
        
        # Extract uptime commitments
        uptime_match = re.search(r'(\d+\.?\d*)%', text)
        if uptime_match:
            sla["performance_metrics"].append(f"{uptime_match.group(1)}% uptime")
        
        # Extract response times
        response_match = re.search(r'(\d+)\s*hour', text, re.IGNORECASE)
        if response_match:
            sla["performance_metrics"].append(f"{response_match.group(1)} hour response time")
        
        return sla
    
    def _extract_start_date(self, text: str) -> str:
        """Extract contract start date"""
        date_match = re.search(r'Effective Date:?\s*([A-Za-z]+ \d+, \d{4})', text, re.IGNORECASE)
        if date_match:
            return date_match.group(1)
        return ""
    
    def _extract_end_date(self, text: str) -> str:
        """Extract contract end date"""
        # Look for contract term and calculate end date
        term_match = re.search(r'Contract Term:?\s*(\d+)\s*months?', text, re.IGNORECASE)
        if term_match:
            months = int(term_match.group(1))
            # This would need proper date calculation in a real implementation
            return f"{months} months from start date"
        return ""
    
    def _extract_contract_type(self, text: str) -> str:
        """Extract contract type"""
        if "service agreement" in text.lower():
            return "Service Agreement"
        elif "license" in text.lower():
            return "License Agreement"
        elif "subscription" in text.lower():
            return "Subscription Agreement"
        return "Service Agreement"
    
    def _calculate_confidence_scores(self, text: str) -> Dict[str, int]:
        """Calculate confidence scores based on extracted data"""
        scores = {
            "financial_completeness": 0,
            "party_identification": 0,
            "payment_terms_clarity": 0,
            "sla_definition": 0,
            "contact_information": 0
        }
        
        # Financial completeness
        if re.search(r'\$[\d,]+', text):
            scores["financial_completeness"] += 30
        if re.search(r'total.*?\$[\d,]+', text, re.IGNORECASE):
            scores["financial_completeness"] += 40
        if re.search(r'line items?|quantity|unit price', text, re.IGNORECASE):
            scores["financial_completeness"] += 30
        
        # Party identification
        if re.search(r'service provider|customer', text, re.IGNORECASE):
            scores["party_identification"] += 50
        if re.search(r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
            scores["party_identification"] += 30
        if re.search(r'phone|tel', text, re.IGNORECASE):
            scores["party_identification"] += 20
        
        # Payment terms clarity
        if re.search(r'net \d+|payment terms', text, re.IGNORECASE):
            scores["payment_terms_clarity"] += 50
        if re.search(r'payment schedule|billing', text, re.IGNORECASE):
            scores["payment_terms_clarity"] += 30
        if re.search(r'ACH|bank transfer', text, re.IGNORECASE):
            scores["payment_terms_clarity"] += 20
        
        # SLA definition
        if re.search(r'uptime|availability', text, re.IGNORECASE):
            scores["sla_definition"] += 40
        if re.search(r'response time|SLA', text, re.IGNORECASE):
            scores["sla_definition"] += 40
        if re.search(r'performance|metrics', text, re.IGNORECASE):
            scores["sla_definition"] += 20
        
        # Contact information
        if re.search(r'@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text):
            scores["contact_information"] += 50
        if re.search(r'phone|tel', text, re.IGNORECASE):
            scores["contact_information"] += 30
        if re.search(r'address|billing contact', text, re.IGNORECASE):
            scores["contact_information"] += 20
        
        return scores
    
    def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms from contract"""
        key_terms = []
        
        # Look for important terms
        if "payment terms" in text.lower():
            key_terms.append("Payment terms specified")
        if "termination" in text.lower():
            key_terms.append("Termination clause")
        if "confidentiality" in text.lower():
            key_terms.append("Confidentiality agreement")
        if "liability" in text.lower():
            key_terms.append("Liability terms")
        
        return key_terms
    
    def _extract_obligations(self, text: str) -> List[str]:
        """Extract main obligations"""
        obligations = []
        
        if "monitoring" in text.lower():
            obligations.append("System monitoring")
        if "support" in text.lower():
            obligations.append("Technical support")
        if "maintenance" in text.lower():
            obligations.append("System maintenance")
        if "backup" in text.lower():
            obligations.append("Data backup")
        
        return obligations
    
    def _extract_risk_factors(self, text: str) -> List[str]:
        """Extract risk factors"""
        risk_factors = []
        
        if "penalty" in text.lower():
            risk_factors.append("Penalty clauses present")
        if "liability" in text.lower():
            risk_factors.append("Liability limitations")
        if "termination" in text.lower():
            risk_factors.append("Termination risks")
        
        return risk_factors
    
    def _extract_compliance_issues(self, text: str) -> List[str]:
        """Extract compliance issues"""
        compliance_issues = []
        
        # This would need more sophisticated analysis in a real implementation
        return compliance_issues
    
    def _generate_summary(self, text: str) -> Dict[str, Any]:
        """Generate contract summary"""
        summary = {
            "overview": "Contract analysis completed using manual extraction methods",
            "parties_involved": [],
            "key_terms": [],
            "financial_summary": "Financial details extracted from contract",
            "contract_duration": "Duration extracted from contract terms",
            "main_obligations": [],
            "risk_level": "Medium",
            "compliance_status": "Good"
        }
        
        # Extract parties for summary
        if "service provider" in text.lower():
            summary["parties_involved"].append("Service Provider")
        if "customer" in text.lower():
            summary["parties_involved"].append("Customer")
        
        return summary
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Return fallback data when parsing fails"""
        return {
            "parties": [],
            "account_info": {},
            "financial_details": {},
            "payment_terms": {},
            "revenue_classification": {},
            "sla": {},
            "contract_start_date": "",
            "contract_end_date": "",
            "contract_type": "Unknown",
            "confidence_scores": {},
            "key_terms": [],
            "obligations": [],
            "risk_factors": [],
            "compliance_issues": [],
            "summary": {
                "overview": "Contract analysis could not be completed",
                "parties_involved": [],
                "key_terms": [],
                "financial_summary": "Financial details not available",
                "contract_duration": "Unknown",
                "main_obligations": [],
                "risk_level": "Unknown",
                "compliance_status": "Unknown"
            }
        }
