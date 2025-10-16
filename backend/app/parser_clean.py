"""
Clean Contract Parser
Uses Direct Gemini AI for maximum accuracy
"""

import logging
from typing import Optional

from .direct_gemini_extractor import DirectGeminiExtractor
from .models import ContractData

logger = logging.getLogger(__name__)

class ContractParser:
    """Clean contract parser using Direct Gemini AI"""
    
    def __init__(self):
        self.direct_gemini_extractor = DirectGeminiExtractor()
    
    async def parse_contract(self, file_path: str) -> ContractData:
        """Parse a contract PDF using Direct Gemini AI"""
        try:
            logger.info(f"Starting contract parsing for: {file_path}")
            return await self.direct_gemini_extractor.extract_contract_data(file_path)
            
        except Exception as e:
            logger.error(f"Error parsing contract: {str(e)}")
            # Return fallback data
            return self._get_fallback_data()
    
    def _get_fallback_data(self) -> ContractData:
        """Return fallback data when extraction fails"""
        from .models import (SLA, ContractSummary, DocumentMetadata, FinancialDetails,
                             PaymentTerms, RevenueClassification)
        
        return ContractData(
            parties=[],
            account_info={},
            financial_details=FinancialDetails(),
            payment_terms=PaymentTerms(),
            revenue_classification=RevenueClassification(payment_type="unknown"),
            sla=SLA(),
            contract_type="Unknown",
            confidence_scores={
                "financial_completeness": 0.0,
                "party_identification": 0.0,
                "payment_terms_clarity": 0.0,
                "sla_definition": 0.0,
                "contact_information": 0.0,
                "overall": 0.0
            },
            key_value_pairs=[],
            risk_factors=[],
            compliance_issues=[],
            important_dates=[],
            processing_notes=["Contract parsing failed, using fallback data"],
            clauses=[],
            document_metadata=DocumentMetadata(total_pages=0, file_size=0),
            summary=ContractSummary(
                overview="Contract analysis failed",
                parties_involved=[],
                key_terms=[],
                financial_summary="No financial data extracted",
                contract_duration="Unknown",
                main_obligations=[],
                risk_level="High",
                compliance_status="Failed"
            ),
            extracted_text=""
        )
