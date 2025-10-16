"""
Direct Gemini Contract Extractor
Send extracted text directly to Gemini AI for maximum accuracy
Handles long PDFs with smart chunking
"""

import asyncio
import logging
import re
from typing import Any, Dict, List, Optional

import fitz  # PyMuPDF
import pdfplumber

from .gemini_analyzer import GeminiContractAnalyzer
from .models import (SLA, ContractData, ContractSummary, DocumentMetadata,
                     FinancialDetails, Party, PaymentTerms,
                     RevenueClassification)

logger = logging.getLogger(__name__)

class DirectGeminiExtractor:
    """Direct Gemini AI extractor for maximum accuracy"""
    
    def __init__(self):
        self.gemini_analyzer = GeminiContractAnalyzer()
        self.max_tokens = 30000  # Safe limit for Gemini
        self.chunk_size = 8000   # Chunk size for processing
        self.overlap = 1000      # Overlap between chunks
    
    async def extract_contract_data(self, file_path: str) -> ContractData:
        """Extract contract data using direct Gemini AI"""
        try:
            # Step 1: Extract all text
            text_content = await self._extract_text_simple(file_path)
            logger.info(f"Extracted {len(text_content)} characters from PDF")
            
            if not text_content:
                logger.warning("No text extracted from PDF")
                return self._get_fallback_data()
            
            # Step 2: Check if text is too long for direct processing
            if len(text_content) > self.max_tokens * 4:  # Rough character to token ratio
                logger.info("Text is long, using chunked processing")
                return await self._process_long_text(text_content)
            else:
                logger.info("Text is manageable, using direct processing")
                return await self._process_direct_text(text_content)
            
        except Exception as e:
            logger.error(f"Error in direct Gemini extraction: {str(e)}")
            return self._get_fallback_data()
    
    async def _extract_text_simple(self, file_path: str) -> str:
        """Extract text using simple, reliable methods"""
        text_content = ""
        
        # Try pdfplumber first (most reliable)
        try:
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")
        
        # Fallback to PyMuPDF
        if not text_content:
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    text_content += page.get_text()
                doc.close()
            except Exception as e:
                logger.warning(f"PyMuPDF extraction failed: {e}")
        
        return text_content.strip()
    
    async def _process_direct_text(self, text: str) -> ContractData:
        """Process text directly with Gemini AI"""
        try:
            # Create comprehensive prompt for Gemini
            prompt = f"""
            Analyze this contract and extract ALL relevant information in JSON format.
            
            Contract Text:
            {text}
            
            Extract and return JSON with:
            1. parties: List of all parties with names, roles, emails, phones, addresses
            2. financial_details: Contract value, currency, line items, taxes, fees
            3. payment_terms: Payment terms, schedule, methods, banking details
            4. sla: Service level agreements, uptime, response times, penalties
            5. contract_dates: Start date, end date, renewal date
            6. confidence_scores: Overall confidence (0.0-1.0)
            7. key_terms: Important contract terms and clauses
            8. risk_factors: Potential risks identified
            9. compliance_issues: Compliance and regulatory issues
            
            Be thorough and extract ALL available information.
            Return only valid JSON.
            """
            
            # Use Gemini to analyze
            ai_analysis = await self.gemini_analyzer.analyze_contract(text, "contract.pdf")
            
            # Convert to ContractData
            return await self._convert_to_contract_data(text, ai_analysis)
            
        except Exception as e:
            logger.error(f"Direct processing failed: {e}")
            return self._get_fallback_data()
    
    async def _process_long_text(self, text: str) -> ContractData:
        """Process long text using chunked approach"""
        try:
            # Split text into chunks
            chunks = self._split_text_into_chunks(text)
            logger.info(f"Split text into {len(chunks)} chunks")
            
            # Process each chunk
            all_analyses = []
            for i, chunk in enumerate(chunks):
                logger.info(f"Processing chunk {i+1}/{len(chunks)}")
                try:
                    analysis = await self._analyze_chunk(chunk, i+1, len(chunks))
                    if analysis:
                        all_analyses.append(analysis)
                except Exception as e:
                    logger.warning(f"Chunk {i+1} analysis failed: {e}")
            
            # Combine all analyses
            combined_analysis = self._combine_analyses(all_analyses)
            
            # Convert to ContractData
            return await self._convert_to_contract_data(text, combined_analysis)
            
        except Exception as e:
            logger.error(f"Chunked processing failed: {e}")
            return self._get_fallback_data()
    
    def _split_text_into_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks"""
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + self.chunk_size
            
            # Try to break at sentence boundary
            if end < len(text):
                # Look for sentence endings
                for i in range(end, max(start + self.chunk_size - 200, start), -1):
                    if text[i] in '.!?':
                        end = i + 1
                        break
            
            chunk = text[start:end]
            chunks.append(chunk)
            
            # Move start with overlap
            start = end - self.overlap
            if start >= len(text):
                break
        
        return chunks
    
    async def _analyze_chunk(self, chunk: str, chunk_num: int, total_chunks: int) -> Dict[str, Any]:
        """Analyze a single chunk with Gemini"""
        try:
            prompt = f"""
            Analyze this contract section (part {chunk_num} of {total_chunks}) and extract relevant information in JSON format.
            
            Contract Section:
            {chunk}
            
            Extract and return JSON with:
            1. parties: Any parties mentioned
            2. financial_details: Any financial information
            3. payment_terms: Any payment information
            4. sla: Any service level information
            5. contract_dates: Any dates mentioned
            6. key_terms: Important terms in this section
            7. risk_factors: Any risks mentioned
            8. compliance_issues: Any compliance issues
            
            Return only valid JSON. If no relevant information, return empty objects.
            """
            
            # Use Gemini to analyze chunk
            analysis = await self.gemini_analyzer.analyze_contract(chunk, f"contract_chunk_{chunk_num}.pdf")
            return analysis
            
        except Exception as e:
            logger.warning(f"Chunk {chunk_num} analysis failed: {e}")
            return {}
    
    def _combine_analyses(self, analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Combine multiple analyses into one comprehensive analysis"""
        combined = {
            'parties': [],
            'financial_details': {},
            'payment_terms': {},
            'sla': {},
            'contract_dates': {},
            'key_terms': [],
            'risk_factors': [],
            'compliance_issues': [],
            'confidence_scores': {}
        }
        
        # Combine parties (deduplicate)
        seen_parties = set()
        for analysis in analyses:
            if 'parties' in analysis:
                for party in analysis['parties']:
                    party_key = party.get('name', '').lower()
                    if party_key and party_key not in seen_parties:
                        combined['parties'].append(party)
                        seen_parties.add(party_key)
        
        # Combine financial details (merge)
        for analysis in analyses:
            if 'financial_details' in analysis:
                financial = analysis['financial_details']
                for key, value in financial.items():
                    if value and (key not in combined['financial_details'] or not combined['financial_details'][key]):
                        combined['financial_details'][key] = value
        
        # Combine payment terms (merge)
        for analysis in analyses:
            if 'payment_terms' in analysis:
                payment = analysis['payment_terms']
                for key, value in payment.items():
                    if value and (key not in combined['payment_terms'] or not combined['payment_terms'][key]):
                        combined['payment_terms'][key] = value
        
        # Combine SLA (merge)
        for analysis in analyses:
            if 'sla' in analysis:
                sla = analysis['sla']
                for key, value in sla.items():
                    if value and (key not in combined['sla'] or not combined['sla'][key]):
                        combined['sla'][key] = value
        
        # Combine dates (merge)
        for analysis in analyses:
            if 'contract_dates' in analysis:
                dates = analysis['contract_dates']
                for key, value in dates.items():
                    if value and (key not in combined['contract_dates'] or not combined['contract_dates'][key]):
                        combined['contract_dates'][key] = value
        
        # Combine lists (deduplicate)
        for analysis in analyses:
            for key in ['key_terms', 'risk_factors', 'compliance_issues']:
                if key in analysis:
                    for item in analysis[key]:
                        if item and item not in combined[key]:
                            combined[key].append(item)
        
        # Calculate combined confidence
        confidences = []
        for analysis in analyses:
            if 'confidence_scores' in analysis and 'overall' in analysis['confidence_scores']:
                confidences.append(analysis['confidence_scores']['overall'])
        
        if confidences:
            combined['confidence_scores']['overall'] = sum(confidences) / len(confidences)
        else:
            combined['confidence_scores']['overall'] = 0.8  # Default high confidence
        
        return combined
    
    async def _convert_to_contract_data(self, text: str, ai_analysis: Dict[str, Any]) -> ContractData:
        """Convert AI analysis to ContractData format"""
        try:
            # Extract parties
            parties = []
            for party_data in ai_analysis.get('parties', []):
                parties.append(Party(
                    name=party_data.get('name', ''),
                    role=party_data.get('role') or 'unknown',
                    email=party_data.get('email', ''),
                    phone=party_data.get('phone', ''),
                    address=party_data.get('address', ''),
                    legal_entity=party_data.get('legal_entity', ''),
                    jurisdiction=party_data.get('jurisdiction', ''),
                    tax_id=party_data.get('tax_id', ''),
                    website=party_data.get('website', ''),
                    authorized_signatory=party_data.get('authorized_signatory', ''),
                    signatory_title=party_data.get('signatory_title', '')
                ))
            
            # Extract financial details
            financial_data = ai_analysis.get('financial_details', {})
            financial_details = FinancialDetails(
                total_contract_value=financial_data.get('total_contract_value') or 0,
                currency=financial_data.get('currency') or 'USD',
                line_items=financial_data.get('line_items') or [],
                tax_amount=financial_data.get('tax_amount') or 0,
                additional_fees=financial_data.get('additional_fees') or 0
            )
            
            # Extract payment terms
            payment_data = ai_analysis.get('payment_terms', {})
            payment_terms = PaymentTerms(
                payment_terms=payment_data.get('payment_terms') or '',
                payment_schedule=payment_data.get('payment_schedule') or '',
                due_dates=payment_data.get('due_dates') or [],
                payment_methods=payment_data.get('payment_methods') or [],
                banking_details=str(payment_data.get('banking_details') or '')
            )
            
            # Extract SLA
            sla_data = ai_analysis.get('sla', {})
            sla = SLA(
                performance_metrics=sla_data.get('performance_metrics') or [],
                benchmarks=[],
                penalty_clauses=[],
                remedies=[],
                support_terms=sla_data.get('support_terms') or '',
                maintenance_terms=sla_data.get('maintenance_terms') or ''
            )
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(ai_analysis, text)
            
            # Create summary
            summary = ContractSummary(
                overview=f"Contract analysis completed. Found {len(parties)} parties, contract value: {financial_details.currency} {financial_details.total_contract_value}",
                parties_involved=[p.name for p in parties],
                key_terms=ai_analysis.get('key_terms', []),
                financial_summary=f"Total value: {financial_details.currency} {financial_details.total_contract_value}",
                contract_duration="To be determined",
                main_obligations=[],
                risk_level="Medium",
                compliance_status="Under review"
            )
            
            return ContractData(
                parties=parties,
                account_info={},
                financial_details=financial_details,
                payment_terms=payment_terms,
                revenue_classification=RevenueClassification(payment_type="unknown"),
                sla=sla,
                contract_start_date=ai_analysis.get('contract_dates', {}).get('start_date', ''),
                contract_end_date=ai_analysis.get('contract_dates', {}).get('end_date', ''),
                contract_type="Service Agreement",
                confidence_scores=confidence_scores,
                key_value_pairs=[],
                risk_factors=ai_analysis.get('risk_factors', []),
                compliance_issues=ai_analysis.get('compliance_issues', []),
                important_dates=[],
                processing_notes=["Direct Gemini AI extraction completed"],
                clauses=[],
                document_metadata=DocumentMetadata(total_pages=0, file_size=0),
                summary=summary,
                extracted_text=text
            )
            
        except Exception as e:
            logger.error(f"Error converting to ContractData: {e}")
            return self._get_fallback_data()
    
    def _calculate_confidence_scores(self, ai_analysis: Dict[str, Any], text: str) -> Dict[str, float]:
        """Calculate confidence scores based on AI analysis"""
        scores = {}
        
        # Financial completeness
        financial_score = 0.0
        if ai_analysis.get('financial_details', {}).get('total_contract_value'):
            financial_score += 0.4
        if ai_analysis.get('financial_details', {}).get('currency'):
            financial_score += 0.3
        if ai_analysis.get('financial_details', {}).get('line_items'):
            financial_score += 0.3
        scores['financial_completeness'] = min(financial_score, 1.0)
        
        # Party identification
        party_score = 0.0
        parties = ai_analysis.get('parties', [])
        if len(parties) >= 2:
            party_score += 0.4
        elif len(parties) >= 1:
            party_score += 0.3
        if any(party.get('email') for party in parties):
            party_score += 0.3
        if any(party.get('phone') for party in parties):
            party_score += 0.3
        scores['party_identification'] = min(party_score, 1.0)
        
        # Payment terms clarity
        payment_score = 0.0
        if ai_analysis.get('payment_terms', {}).get('payment_terms'):
            payment_score += 0.4
        if ai_analysis.get('payment_terms', {}).get('payment_methods'):
            payment_score += 0.3
        if ai_analysis.get('payment_terms', {}).get('banking_details'):
            payment_score += 0.3
        scores['payment_terms_clarity'] = min(payment_score, 1.0)
        
        # SLA definition
        sla_score = 0.0
        if ai_analysis.get('sla', {}).get('support_terms'):
            sla_score += 0.5
        if ai_analysis.get('sla', {}).get('performance_metrics'):
            sla_score += 0.3
        if ai_analysis.get('sla', {}).get('maintenance_terms'):
            sla_score += 0.2
        scores['sla_definition'] = min(sla_score, 1.0)
        
        # Contact information
        contact_score = 0.0
        if any(party.get('email') for party in parties):
            contact_score += 0.4
        if any(party.get('phone') for party in parties):
            contact_score += 0.3
        if any(party.get('address') for party in parties):
            contact_score += 0.3
        scores['contact_information'] = min(contact_score, 1.0)
        
        # Overall score with AI boost
        weights = {
            'financial_completeness': 0.25,
            'party_identification': 0.25,
            'payment_terms_clarity': 0.20,
            'sla_definition': 0.15,
            'contact_information': 0.15
        }
        
        weighted_score = sum(scores[key] * weights[key] for key in weights.keys())
        
        # AI analysis boost
        ai_confidence = ai_analysis.get('confidence_scores', {}).get('overall', 0.8)
        boost = 0.0
        if ai_confidence > 0.7:
            boost += 0.2
        if len(parties) > 0:
            boost += 0.1
        if ai_analysis.get('financial_details'):
            boost += 0.1
        
        scores['overall'] = min(weighted_score + boost, 1.0)
        
        return scores
    
    def _get_fallback_data(self) -> ContractData:
        """Return fallback data when extraction fails"""
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
            processing_notes=["Direct Gemini extraction failed, using fallback data"],
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
