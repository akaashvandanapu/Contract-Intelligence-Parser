import json
import logging
import os
from typing import Any, Dict, List, Optional

import google.generativeai as genai

logger = logging.getLogger(__name__)

class GeminiContractAnalyzer:
    """AI-powered contract analysis using Google Gemini"""
    
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("GEMINI_API_KEY not found. AI analysis will be disabled.")
            self.enabled = False
        else:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.enabled = True
    
    async def analyze_contract(self, pdf_text: str, filename: str = "contract.pdf") -> Dict[str, Any]:
        """Analyze contract using Gemini AI and return structured data"""
        if not self.enabled:
            return self._get_fallback_data()
        
        try:
            # Create comprehensive prompt for contract analysis
            prompt = self._create_analysis_prompt(pdf_text, filename)
            
            # Get AI response
            response = self.model.generate_content(prompt)
            
            # Parse the response
            analysis_result = self._parse_ai_response(response.text)
            
            logger.info("Gemini AI analysis completed successfully")
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error in Gemini AI analysis: {str(e)}")
            return self._get_fallback_data()
    
    def _create_analysis_prompt(self, pdf_text: str, filename: str) -> str:
        """Create a comprehensive prompt for contract analysis based on assignment requirements"""
        return f"""
You are an expert contract analyst for an accounts receivable SaaS platform. Your PRIMARY FOCUS is to extract data into the 6 specific assignment requirement categories. Only add extra information if it provides significant additional value.

Contract Filename: {filename}
Contract Text:
{pdf_text[:8000]}  # Limit text to avoid token limits

CRITICAL INSTRUCTIONS - PRIORITIZE ASSIGNMENT REQUIREMENTS:

EXTRACT DATA INTO THESE 6 CATEGORIES FIRST (Priority 1):

1. **PARTY IDENTIFICATION** - Extract ALL parties mentioned:
   - Contract parties (customer, vendor, third parties)
   - Legal entity names and registration details
   - Authorized signatories and roles
   - ALL contact information (emails, phones, addresses)

2. **ACCOUNT INFORMATION** - Extract billing and account details:
   - Customer billing details and addresses
   - Account numbers and references
   - Contact information for billing/technical support

3. **FINANCIAL DETAILS** - Extract all financial information:
   - Line items with descriptions, quantities, and unit prices
   - Total contract value and currency
   - Tax information and additional fees

4. **PAYMENT STRUCTURE** - Extract payment-related information:
   - Payment terms (Net 30, Net 60, etc.)
   - Payment schedules and due dates
   - Payment methods and banking details

5. **REVENUE CLASSIFICATION** - Identify payment patterns:
   - Identify recurring vs. one-time payments or both
   - Subscription models and billing cycles
   - Renewal terms and auto-renewal clauses

6. **SERVICE LEVEL AGREEMENTS** - Extract performance and support terms:
   - Performance metrics and benchmarks
   - Penalty clauses and remedies
   - Support and maintenance terms

ONLY AFTER extracting all required assignment data, add any additional valuable information.

Return a JSON object with this EXACT structure focusing on the 6 assignment requirement categories:

{{
  "parties": [
    {{
      "name": "Extract ALL party names mentioned in contract",
      "role": "customer/vendor/contractor/supplier/client/third_party",
      "email": "ALL email addresses found in contract",
      "phone": "ALL phone numbers found in contract", 
      "address": "ALL addresses found in contract",
      "legal_entity": "Corporation/LLC/Partnership/Individual",
      "registration_number": "business registration number if available",
      "tax_id": "tax identification number if available",
      "website": "company website if mentioned",
      "jurisdiction": "legal jurisdiction if specified"
    }}
  ],
  
  "account_info": {{
    "contact_email": "primary billing contact email",
    "account_number": "customer account number or reference",
    "billing_address": "complete billing address",
    "technical_contact": "technical support contact information",
    "account_manager": "account manager name if mentioned"
  }},
  
  "financial_details": {{
    "total_contract_value": "total contract value as number",
    "currency": "currency code (USD, EUR, GBP, etc)",
    "line_items": [
      {{
        "description": "detailed item description",
        "quantity": "quantity as number",
        "unit_price": "unit price as number",
        "total_price": "total price as number"
      }}
    ],
    "tax_amount": "tax amount as number if specified",
    "additional_fees": "additional fees as number if specified"
  }},
  
  "payment_terms": {{
    "payment_terms": "Net 30, Net 60, Due on receipt, etc",
    "payment_schedule": "monthly, quarterly, annual, milestone-based",
    "due_dates": ["specific due dates if mentioned"],
    "payment_methods": ["bank transfer", "check", "credit card", "ACH", "wire"],
    "banking_details": "bank account details, routing numbers, payment instructions"
  }},
  
  "revenue_classification": {{
    "payment_type": "recurring/one-time/mixed/hybrid",
    "billing_cycle": "monthly/quarterly/annual/custom",
    "subscription_model": "SaaS/subscription/license/perpetual",
    "renewal_terms": "automatic renewal, manual renewal, evergreen",
    "auto_renewal": "true/false/conditional"
  }},
  
  "sla": {{
    "performance_metrics": ["99.9% uptime", "response time < 2s", "availability targets"],
    "benchmarks": ["specific performance benchmarks and KPIs"],
    "penalty_clauses": ["penalty terms, liquidated damages"],
    "remedies": ["remedy clauses, cure periods, termination rights"],
    "support_terms": "support level, hours, escalation procedures",
    "maintenance_terms": "maintenance windows, updates, patches"
  }},
  "important_dates": {{
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "renewal_date": "2024-11-01",
    "termination_notice": "30 days"
  }},
  "key_terms": [
    "Payment terms: Net 30",
    "Termination: 30 days notice",
    "Confidentiality: 5 years",
    "Governing law: State of California"
  ],
  "main_obligations": [
    "Deliver software updates monthly",
    "Provide 24/7 technical support",
    "Maintain 99.9% uptime",
    "Comply with data protection regulations"
  ],
  "risk_factors": [
    "High contract value increases risk",
    "Long-term commitment",
    "Penalty clauses for non-performance"
  ],
  "compliance_issues": [
    "Missing data protection clauses",
    "Unclear termination terms"
  ],
  "contract_start_date": "contract effective/start date",
  "contract_end_date": "contract expiration/end date", 
  "contract_type": "service agreement, license, subscription, maintenance",
  "confidence_scores": {{
    "financial_completeness": "0-100 based on financial data completeness",
    "party_identification": "0-100 based on party information clarity", 
    "payment_terms_clarity": "0-100 based on payment terms specificity",
    "sla_definition": "0-100 based on SLA detail and measurability",
    "contact_information": "0-100 based on contact details availability"
  }},
  "summary": {{
    "overview": "This service contract involves ABC Company and XYZ Corp valued at USD 50,000. The contract establishes software licensing terms and support services.",
    "parties_involved": ["ABC Company Inc.", "XYZ Corporation"],
    "key_terms": ["Payment terms: Net 30", "Termination: 30 days notice"],
    "financial_summary": "Total contract value: USD 50,000; 5 line items identified",
    "contract_duration": "12 months",
    "main_obligations": ["Deliver software updates", "Provide technical support"],
    "risk_level": "Medium",
    "compliance_status": "Compliant"
  }}
}}

IMPORTANT: 
- Return ONLY valid JSON, no other text
- Use null for missing information
- Ensure all dates are in YYYY-MM-DD format
- Be as accurate as possible based on the contract text
- If information is not clearly stated, use null or reasonable defaults
"""
    
    def _parse_ai_response(self, response_text: str) -> Dict[str, Any]:
        """Parse the AI response and extract JSON data"""
        try:
            # Clean the response text
            cleaned_text = response_text.strip()
            
            # Remove any markdown formatting
            if cleaned_text.startswith("```json"):
                cleaned_text = cleaned_text[7:]
            if cleaned_text.endswith("```"):
                cleaned_text = cleaned_text[:-3]
            
            # Parse JSON
            result = json.loads(cleaned_text)
            
            # Validate and clean the result
            return self._validate_and_clean_result(result)
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {str(e)}")
            logger.error(f"Response text: {response_text[:500]}...")
            return self._get_fallback_data()
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._get_fallback_data()
    
    def _validate_and_clean_result(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and clean the AI response data"""
        try:
            # Ensure required fields exist
            required_fields = ["parties", "financial_details", "payment_terms", "summary"]
            for field in required_fields:
                if field not in data:
                    data[field] = {}
            
            # Clean and validate parties
            if isinstance(data.get("parties"), list):
                data["parties"] = [party for party in data["parties"] if isinstance(party, dict)]
            else:
                data["parties"] = []
            
            # Clean financial details
            if not isinstance(data.get("financial_details"), dict):
                data["financial_details"] = {}
            
            # Clean payment terms
            if not isinstance(data.get("payment_terms"), dict):
                data["payment_terms"] = {}
            
            # Clean summary
            if not isinstance(data.get("summary"), dict):
                data["summary"] = self._get_default_summary()
            
            return data
            
        except Exception as e:
            logger.error(f"Error validating AI response: {str(e)}")
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> Dict[str, Any]:
        """Return fallback data when AI analysis fails"""
        return {
            "overview": "Contract analysis could not be completed",
            "parties": [],
            "financial_details": {},
            "payment_terms": {},
            "revenue_classification": {},
            "sla": {},
            "important_dates": {},
            "key_terms": [],
            "main_obligations": [],
            "risk_factors": [],
            "compliance_issues": [],
            "contract_type": "Unknown",
            "confidence_scores": {},
            "summary": self._get_default_summary()
        }
    
    def _get_default_summary(self) -> Dict[str, Any]:
        """Get default summary when AI analysis fails"""
        return {
            "overview": "Contract summary could not be generated",
            "parties_involved": [],
            "key_terms": [],
            "financial_summary": "Financial details not available",
            "contract_duration": "Unknown",
            "main_obligations": [],
            "risk_level": "Unknown",
            "compliance_status": "Unknown"
        }
