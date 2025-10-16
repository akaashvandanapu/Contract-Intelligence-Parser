import fitz  # PyMuPDF
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

try:
    import cv2
    import numpy as np
    from PIL import Image
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    cv2 = None
    np = None
    Image = None
import logging
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import dateparser
import pandas as pd
import phonenumbers
import spacy
from email_validator import EmailNotValidError, validate_email
from fuzzywuzzy import fuzz

from .gemini_analyzer import GeminiContractAnalyzer
from .manual_parser import ManualContractParser
from .models import (SLA, AccountInfo, ContractData, ContractSummary,
                     DocumentMetadata, FinancialDetails, KeyValuePair, Party,
                     PaymentTerms, RevenueClassification)

logger = logging.getLogger(__name__)

class EnhancedContractParser:
    def __init__(self):
        self.nlp = None
        self.gemini_analyzer = GeminiContractAnalyzer()
        self.manual_parser = ManualContractParser()
        self._load_nlp_model()
        self.patterns = self._initialize_patterns()
        
    def _load_nlp_model(self):
        """Load spaCy model for NLP processing"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
            self.nlp = None
        except Exception as e:
            logger.warning(f"spaCy initialization failed: {e}")
            self.nlp = None
    
    def _initialize_patterns(self):
        """Initialize regex patterns for enhanced extraction"""
        return {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'currency': r'\$[\d,]+\.?\d*|\d+\.?\d*\s*(USD|EUR|GBP|CAD|INR)',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            'percentage': r'\d+\.?\d*\s*%',
            'contract_number': r'(?:contract|agreement|order)\s*(?:no\.?|number|#)\s*:?\s*([A-Z0-9-]+)',
            'tax_id': r'(?:tax\s*id|ein|tin)\s*:?\s*([0-9-]+)',
            'address': r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln|Way|Circle|Cir|Court|Ct)',
            'company_name': r'(?:inc|llc|ltd|corp|corporation|company|co\.?|limited|group|holdings|enterprises)\b',
            'amount': r'\$[\d,]+\.?\d*|\d+\.?\d*\s*(?:thousand|million|billion|k|m|b)',
            'duration': r'\d+\s*(?:days?|weeks?|months?|years?|quarters?)',
            'termination': r'(?:terminate|termination|expire|expiry|end)\s+(?:date|on|after)\s*:?\s*([^\n]+)',
            'renewal': r'(?:renew|renewal|extend|extension)\s+(?:date|on|after)\s*:?\s*([^\n]+)',
            'penalty': r'(?:penalty|fine|charge)\s+(?:of|for)\s*:?\s*([^\n]+)',
            'warranty': r'(?:warranty|guarantee)\s+(?:period|term)\s*:?\s*([^\n]+)',
            'liability': r'(?:liability|liabilities)\s+(?:limit|cap|maximum)\s*:?\s*([^\n]+)',
            'force_majeure': r'(?:force\s+majeure|act\s+of\s+god|unforeseen\s+circumstances)',
            'confidentiality': r'(?:confidential|proprietary|non-disclosure|nda)',
            'governing_law': r'(?:governing\s+law|jurisdiction|venue)\s*:?\s*([^\n]+)',
            'dispute_resolution': r'(?:dispute|arbitration|mediation|litigation)\s+(?:resolution|procedure)',
            'key_personnel': r'(?:key\s+personnel|key\s+employees|key\s+staff)',
            'intellectual_property': r'(?:intellectual\s+property|ip|patent|copyright|trademark)',
            'data_protection': r'(?:data\s+protection|privacy|gdpr|personal\s+data)',
            'compliance': r'(?:compliance|regulatory|legal\s+requirements)',
        }
    
    async def parse_contract(self, file_path: str) -> ContractData:
        """Enhanced contract parsing with Gemini AI and advanced extraction"""
        try:
            # Extract text using multiple methods
            text_content = await self._extract_text_enhanced(file_path)
            
            # Use Gemini AI for comprehensive analysis
            try:
                ai_analysis = await self.gemini_analyzer.analyze_contract(text_content, file_path)
                
                # Convert AI analysis to our data models
                parties = self._convert_ai_parties(ai_analysis.get("parties", []))
                financial_details = self._convert_ai_financial(ai_analysis.get("financial_details", {}))
                payment_terms = self._convert_ai_payment_terms(ai_analysis.get("payment_terms", {}))
                revenue_classification = self._convert_ai_revenue(ai_analysis.get("revenue_classification", {}))
                sla = self._convert_ai_sla(ai_analysis.get("sla", {}))
                account_info = self._convert_ai_account_info(ai_analysis.get("parties", []))
                
            except Exception as e:
                logger.error(f"Gemini AI analysis failed: {str(e)}")
                # Fallback to improved manual parsing
                return self._parse_contract_manual_improved(text_content, file_path)
            
            # Extract additional data using traditional methods
            metadata = await self._extract_metadata(file_path)
            key_value_pairs = await self._extract_key_value_pairs(text_content)
            important_dates = await self._extract_important_dates(text_content)
            clauses = await self._extract_clauses(text_content)
            
            # Risk and compliance analysis from AI
            risk_factors = ai_analysis.get("risk_factors", [])
            compliance_issues = ai_analysis.get("compliance_issues", [])
            
            # Calculate confidence scores from AI
            confidence_scores = ai_analysis.get("confidence_scores", {})
            
            # Create processing notes
            processing_notes = [
                "AI-powered analysis completed using Gemini",
                f"Extracted {len(parties)} parties",
                f"Identified {len(key_value_pairs)} key-value pairs"
            ]
            
            # Generate contract summary from AI
            summary = self._convert_ai_summary(ai_analysis.get("summary", {}))
            
            return ContractData(
                parties=parties,
                account_info=account_info,
                financial_details=financial_details,
                payment_terms=payment_terms,
                revenue_classification=revenue_classification,
                sla=sla,
                contract_start_date=important_dates.get('start_date'),
                contract_end_date=important_dates.get('end_date'),
                contract_type=ai_analysis.get("contract_type", "Unknown"),
                confidence_scores=confidence_scores,
                key_value_pairs=key_value_pairs,
                document_metadata=metadata,
                extracted_text=text_content,
                processing_notes=processing_notes,
                risk_factors=risk_factors,
                compliance_issues=compliance_issues,
                important_dates=[{"date": k, "description": v} for k, v in important_dates.items()],
                clauses=clauses,
                summary=summary
            )
            
        except Exception as e:
            logger.error(f"Error in enhanced contract parsing: {str(e)}")
            raise
    
    def _parse_contract_manual_improved(self, text_content: str, file_path: str) -> ContractData:
        """Improved manual contract parsing using the new manual parser"""
        try:
            # Use the manual parser
            manual_result = self.manual_parser.parse_contract_text(text_content)
            
            # Convert manual result to our data models
            parties = self._convert_manual_parties(manual_result.get("parties", []))
            account_info = self._convert_manual_account_info(manual_result.get("account_info", {}))
            financial_details = self._convert_manual_financial(manual_result.get("financial_details", {}))
            payment_terms = self._convert_manual_payment_terms(manual_result.get("payment_terms", {}))
            revenue_classification = self._convert_manual_revenue(manual_result.get("revenue_classification", {}))
            sla = self._convert_manual_sla(manual_result.get("sla", {}))
            summary = self._convert_manual_summary(manual_result.get("summary", {}))
            
            # Create ContractData object
            contract_data = ContractData(
                parties=parties,
                account_info=account_info,
                financial_details=financial_details,
                payment_terms=payment_terms,
                revenue_classification=revenue_classification,
                sla=sla,
                contract_start_date=manual_result.get("contract_start_date", ""),
                contract_end_date=manual_result.get("contract_end_date", ""),
                contract_type=manual_result.get("contract_type", "Unknown"),
                confidence_scores=manual_result.get("confidence_scores", {}),
                key_value_pairs=[],
                risk_factors=manual_result.get("risk_factors", []),
                compliance_issues=manual_result.get("compliance_issues", []),
                important_dates=[],
                processing_notes=["Manual extraction completed"],
                clauses=[],
                document_metadata=DocumentMetadata(total_pages=0, file_size=0),
                summary=summary,
                extracted_text=text_content
            )
            
            logger.info("Manual contract parsing completed successfully")
            return contract_data
            
        except Exception as e:
            logger.error(f"Error in manual contract parsing: {str(e)}")
            # Return basic fallback
            return ContractData(
                parties=[],
                account_info={},
                financial_details=FinancialDetails(),
                payment_terms={},
                revenue_classification={},
                sla=SLA(),
                contract_start_date="",
                contract_end_date="",
                contract_type="Unknown",
                confidence_scores={},
                key_value_pairs=[],
                risk_factors=[],
                compliance_issues=[],
                important_dates=[],
                processing_notes=["Manual extraction failed"],
                clauses=[],
                document_metadata=DocumentMetadata(total_pages=0, file_size=0),
                summary=ContractSummary(),
                extracted_text=text_content
            )
    
    def _convert_manual_parties(self, parties_data: List[Dict]) -> List[Party]:
        """Convert manual parser parties to Party objects"""
        parties = []
        for party_data in parties_data:
            try:
                party = Party(
                    name=party_data.get("name", ""),
                    role=party_data.get("role", ""),
                    email=party_data.get("email", ""),
                    phone=party_data.get("phone", ""),
                    address=party_data.get("address", ""),
                    legal_entity=party_data.get("legal_entity", ""),
                    registration_number=party_data.get("registration_number", ""),
                    tax_id=party_data.get("tax_id", ""),
                    website=party_data.get("website", ""),
                    jurisdiction=party_data.get("jurisdiction", "")
                )
                parties.append(party)
            except Exception as e:
                logger.error(f"Error converting manual party: {e}")
                continue
        return parties
    
    def _convert_manual_account_info(self, account_data: Dict) -> Dict:
        """Convert manual parser account info"""
        return {
            "contact_email": account_data.get("contact_email", ""),
            "account_number": account_data.get("account_number", ""),
            "billing_address": account_data.get("billing_address", ""),
            "technical_contact": account_data.get("technical_contact", ""),
            "account_manager": account_data.get("account_manager", "")
        }
    
    def _convert_manual_financial(self, financial_data: Dict) -> FinancialDetails:
        """Convert manual parser financial details"""
        try:
            return FinancialDetails(
                total_contract_value=financial_data.get("total_contract_value", 0),
                currency=financial_data.get("currency", "USD"),
                line_items=financial_data.get("line_items", []),
                tax_amount=financial_data.get("tax_amount", 0),
                additional_fees=financial_data.get("additional_fees", 0)
            )
        except Exception as e:
            logger.error(f"Error converting manual financial details: {e}")
            return FinancialDetails()
    
    def _convert_manual_payment_terms(self, payment_data: Dict) -> Dict:
        """Convert manual parser payment terms"""
        return {
            "payment_terms": payment_data.get("payment_terms", ""),
            "payment_schedule": payment_data.get("payment_schedule", ""),
            "due_dates": payment_data.get("due_dates", []),
            "payment_methods": payment_data.get("payment_methods", []),
            "banking_details": payment_data.get("banking_details", "")
        }
    
    def _convert_manual_revenue(self, revenue_data: Dict) -> Dict:
        """Convert manual parser revenue classification"""
        return {
            "payment_type": revenue_data.get("payment_type", ""),
            "billing_cycle": revenue_data.get("billing_cycle", ""),
            "subscription_model": revenue_data.get("subscription_model", ""),
            "renewal_terms": revenue_data.get("renewal_terms", ""),
            "auto_renewal": revenue_data.get("auto_renewal", False)
        }
    
    def _convert_manual_sla(self, sla_data: Dict) -> SLA:
        """Convert manual parser SLA"""
        try:
            return SLA(
                performance_metrics=sla_data.get("performance_metrics", []),
                benchmarks=sla_data.get("benchmarks", []),
                penalty_clauses=sla_data.get("penalty_clauses", []),
                remedies=sla_data.get("remedies", []),
                support_terms=sla_data.get("support_terms", ""),
                maintenance_terms=sla_data.get("maintenance_terms", "")
            )
        except Exception as e:
            logger.error(f"Error converting manual SLA: {e}")
            return SLA()
    
    def _convert_manual_summary(self, summary_data: Dict) -> ContractSummary:
        """Convert manual parser summary"""
        try:
            return ContractSummary(
                overview=summary_data.get("overview", ""),
                parties_involved=summary_data.get("parties_involved", []),
                key_terms=summary_data.get("key_terms", []),
                financial_summary=summary_data.get("financial_summary", ""),
                contract_duration=summary_data.get("contract_duration", ""),
                main_obligations=summary_data.get("main_obligations", []),
                risk_level=summary_data.get("risk_level", ""),
                compliance_status=summary_data.get("compliance_status", "")
            )
        except Exception as e:
            logger.error(f"Error converting manual summary: {e}")
            return ContractSummary()
    
    async def _extract_text_enhanced(self, file_path: str) -> str:
        """Extract text using multiple methods for better coverage"""
        text_content = ""
        
        try:
            # Method 1: pdfplumber for better text extraction
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content += text + "\n"
            
            # Method 2: PyMuPDF for additional text extraction
            doc = fitz.open(file_path)
            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                text = page.get_text()
                if text:
                    text_content += text + "\n"
            doc.close()
            
            # Method 3: OCR for scanned documents if text extraction is poor
            if len(text_content.strip()) < 100:  # If very little text extracted
                text_content += await self._extract_text_with_ocr(file_path)
            
        except Exception as e:
            logger.error(f"Error in text extraction: {str(e)}")
            # Fallback to basic PyPDF2
            import PyPDF2
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
        
        return text_content.strip()
    
    async def _extract_text_with_ocr(self, file_path: str) -> str:
        """Extract text using OCR for scanned documents"""
        if not OPENCV_AVAILABLE:
            logger.warning("OpenCV not available, skipping OCR processing")
            return ""
            
        try:
            # Convert PDF to images
            images = convert_from_path(file_path, dpi=300)
            ocr_text = ""
            
            for image in images:
                # Preprocess image for better OCR
                img_array = np.array(image)
                processed_img = self._preprocess_image_for_ocr(img_array)
                
                # Perform OCR
                text = pytesseract.image_to_string(processed_img, config='--psm 6')
                ocr_text += text + "\n"
            
            return ocr_text
        except Exception as e:
            logger.error(f"Error in OCR extraction: {str(e)}")
            return ""
    
    def _preprocess_image_for_ocr(self, image):
        """Preprocess image for better OCR results"""
        if not OPENCV_AVAILABLE:
            return image  # Return original image if OpenCV not available
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply thresholding
        _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Apply morphological operations
        kernel = np.ones((1, 1), np.uint8)
        processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return processed
    
    async def _extract_metadata(self, file_path: str) -> DocumentMetadata:
        """Extract document metadata"""
        try:
            doc = fitz.open(file_path)
            metadata = doc.metadata
            doc.close()
            
            return DocumentMetadata(
                total_pages=len(doc),
                file_size=os.path.getsize(file_path),
                creation_date=metadata.get('creationDate'),
                modification_date=metadata.get('modDate'),
                author=metadata.get('author'),
                title=metadata.get('title'),
                subject=metadata.get('subject'),
                keywords=metadata.get('keywords'),
                producer=metadata.get('producer')
            )
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return DocumentMetadata(total_pages=0, file_size=0)
    
    async def _extract_key_value_pairs(self, text: str) -> List[KeyValuePair]:
        """Extract key-value pairs from contract text"""
        key_value_pairs = []
        
        # Common contract field patterns
        field_patterns = [
            (r'(?:contract\s+number|agreement\s+number)\s*:?\s*([^\n]+)', 'contract_number'),
            (r'(?:effective\s+date|commencement\s+date)\s*:?\s*([^\n]+)', 'effective_date'),
            (r'(?:expiration\s+date|end\s+date)\s*:?\s*([^\n]+)', 'expiration_date'),
            (r'(?:total\s+value|contract\s+value)\s*:?\s*([^\n]+)', 'total_value'),
            (r'(?:payment\s+terms)\s*:?\s*([^\n]+)', 'payment_terms'),
            (r'(?:governing\s+law)\s*:?\s*([^\n]+)', 'governing_law'),
            (r'(?:jurisdiction)\s*:?\s*([^\n]+)', 'jurisdiction'),
            (r'(?:termination\s+clause)\s*:?\s*([^\n]+)', 'termination_clause'),
            (r'(?:force\s+majeure)\s*:?\s*([^\n]+)', 'force_majeure'),
            (r'(?:confidentiality)\s*:?\s*([^\n]+)', 'confidentiality'),
        ]
        
        for pattern, field_type in field_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                key = match.group(0).split(':')[0].strip()
                value = match.group(1).strip()
                confidence = self._calculate_field_confidence(value, field_type)
                
                key_value_pairs.append(KeyValuePair(
                    key=key,
                    value=value,
                    confidence=confidence,
                    field_type=field_type
                ))
        
        return key_value_pairs
    
    async def _extract_parties_enhanced(self, text: str) -> List[Party]:
        """Enhanced party extraction with better accuracy"""
        parties = []
        
        # Use NLP for better entity recognition
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ == "PERSON" or ent.label_ == "ORG":
                    # Extract surrounding context
                    context = self._extract_context_around_entity(text, ent.text, 100)
                    
                    # Extract contact information
                    email = self._extract_email_from_context(context)
                    phone = self._extract_phone_from_context(context)
                    address = self._extract_address_from_context(context)
                    
                    # Determine role
                    role = self._determine_party_role(context, ent.text)
                    
                    # Calculate confidence
                    confidence = self._calculate_party_confidence(ent.text, context, email, phone)
                    
                    parties.append(Party(
                        name=ent.text,
                        email=email,
                        phone=phone,
                        address=address,
                        role=role,
                        confidence_score=confidence
                    ))
        
        # Fallback to regex-based extraction
        if not parties:
            parties = await self._extract_parties_regex(text)
        
        return parties
    
    async def _extract_parties_regex(self, text: str) -> List[Party]:
        """Extract parties using regex patterns"""
        parties = []
        
        # Common party patterns
        party_patterns = [
            r'(?:between|by and between)\s+([A-Z][a-zA-Z\s&,.-]+?)(?:\s+and\s+|\s+&\s+|\s*,|\s+$)',
            r'(?:client|customer|buyer|purchaser):\s*([A-Z][a-zA-Z\s&,.-]+?)(?:\s*$|\s*,|\s+and)',
            r'(?:vendor|supplier|seller|provider):\s*([A-Z][a-zA-Z\s&,.-]+?)(?:\s*$|\s*,|\s+and)',
            r'([A-Z][a-zA-Z\s&,.-]+?)\s+(?:Inc\.|LLC|Corp\.|Corporation|Company|Ltd\.)',
        ]
        
        for pattern in party_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                name = match.group(1).strip()
                if len(name) > 3 and name not in ['The', 'This', 'That']:
                    # Try to extract email and phone for this party
                    email = self._extract_email_for_party(text, name)
                    phone = self._extract_phone_for_party(text, name)
                    
                    party = Party(
                        name=name,
                        role="customer",  # Default role
                        email=email,
                        phone=phone,
                        confidence_score=0.7
                    )
                    parties.append(party)
        
        return parties
    
    def _extract_email_for_party(self, text: str, party_name: str) -> Optional[str]:
        """Extract email associated with a specific party"""
        try:
            # Look for email patterns near the party name
            context = self._extract_context_around_entity(text, party_name, 200)
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            matches = re.findall(email_pattern, context)
            return matches[0] if matches else None
        except:
            return None
    
    def _extract_phone_for_party(self, text: str, party_name: str) -> Optional[str]:
        """Extract phone associated with a specific party"""
        try:
            # Look for phone patterns near the party name
            context = self._extract_context_around_entity(text, party_name, 200)
            phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
            matches = re.findall(phone_pattern, context)
            if matches:
                return f"({matches[0][0]}) {matches[0][1]}-{matches[0][2]}"
            return None
        except:
            return None
    
    def _extract_context_around_entity(self, text: str, entity: str, window: int) -> str:
        """Extract context around an entity"""
        try:
            start = text.find(entity)
            if start == -1:
                return ""
            
            context_start = max(0, start - window)
            context_end = min(len(text), start + len(entity) + window)
            return text[context_start:context_end]
        except:
            return ""
    
    def _extract_email_from_context(self, context: str) -> Optional[str]:
        """Extract email from context"""
        email_match = re.search(self.patterns['email'], context)
        if email_match:
            try:
                validate_email(email_match.group())
                return email_match.group()
            except EmailNotValidError:
                return None
        return None
    
    def _extract_phone_from_context(self, context: str) -> Optional[str]:
        """Extract phone from context"""
        phone_match = re.search(self.patterns['phone'], context)
        if phone_match:
            return phone_match.group()
        return None
    
    def _extract_address_from_context(self, context: str) -> Optional[str]:
        """Extract address from context"""
        address_match = re.search(self.patterns['address'], context)
        if address_match:
            return address_match.group()
        return None
    
    def _determine_party_role(self, context: str, entity: str) -> str:
        """Determine party role based on context"""
        context_lower = context.lower()
        
        if any(word in context_lower for word in ['customer', 'client', 'buyer', 'purchaser']):
            return 'customer'
        elif any(word in context_lower for word in ['vendor', 'supplier', 'seller', 'provider']):
            return 'vendor'
        elif any(word in context_lower for word in ['third party', 'third-party', 'subcontractor']):
            return 'third_party'
        else:
            return 'unknown'
    
    def _calculate_party_confidence(self, name: str, context: str, email: str, phone: str) -> float:
        """Calculate confidence score for party extraction"""
        confidence = 0.0
        
        # Base confidence from name quality
        if len(name.split()) >= 2:
            confidence += 0.3
        
        # Boost confidence with contact info
        if email:
            confidence += 0.3
        if phone:
            confidence += 0.2
        
        # Boost confidence with context quality
        if len(context) > 50:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    async def _extract_financial_details_enhanced(self, text: str) -> FinancialDetails:
        """Enhanced financial details extraction"""
        # Extract currency amounts with better patterns
        currency_patterns = [
            r'\$[\d,]+\.?\d*',
            r'\d+\.?\d*\s*(?:thousand|million|billion|k|m|b)',
            r'\d+\.?\d*\s*(?:USD|EUR|GBP|CAD|INR)'
        ]
        
        amounts = []
        for pattern in currency_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            amounts.extend(matches)
        
        # Extract line items from tables
        line_items = await self._extract_line_items_from_tables(text)
        
        # Calculate total contract value
        total_value = await self._calculate_total_contract_value(amounts, line_items)
        
        return FinancialDetails(
            total_contract_value=total_value,
            currency="USD",  # Default, could be enhanced to detect
            line_items=line_items
        )
    
    async def _extract_line_items_from_tables(self, text: str) -> List[Dict[str, Any]]:
        """Extract line items from tables in the document"""
        line_items = []
        
        # Look for table-like structures
        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Look for lines that might be table headers
            if any(word in line.lower() for word in ['item', 'description', 'quantity', 'price', 'amount']):
                # Try to extract following lines as table data
                for j in range(i+1, min(i+10, len(lines))):
                    next_line = lines[j].strip()
                    if next_line and not next_line.startswith(('page', 'section', 'article')):
                        # Parse line item
                        parts = next_line.split()
                        if len(parts) >= 3:
                            line_items.append({
                                'description': ' '.join(parts[:-2]),
                                'quantity': self._extract_number(parts[-2]),
                                'unit_price': self._extract_number(parts[-1]),
                                'total_price': self._extract_number(parts[-1]) * self._extract_number(parts[-2])
                            })
        
        return line_items
    
    def _extract_number(self, text: str) -> float:
        """Extract number from text"""
        try:
            # Remove currency symbols and commas
            cleaned = re.sub(r'[^\d.-]', '', text)
            return float(cleaned) if cleaned else 0.0
        except:
            return 0.0
    
    async def _calculate_total_contract_value(self, amounts: List[str], line_items: List[Dict]) -> float:
        """Calculate total contract value"""
        total = 0.0
        
        # Sum line items
        for item in line_items:
            if 'total_price' in item:
                total += item['total_price']
        
        # Add standalone amounts
        for amount in amounts:
            try:
                cleaned = re.sub(r'[^\d.-]', '', amount)
                if cleaned:
                    total += float(cleaned)
            except:
                continue
        
        return total
    
    async def _extract_payment_terms_enhanced(self, text: str) -> PaymentTerms:
        """Enhanced payment terms extraction"""
        # Look for payment terms patterns
        payment_patterns = [
            r'(?:net\s+(\d+))',
            r'(?:due\s+upon\s+receipt)',
            r'(?:cod|cash\s+on\s+delivery)',
            r'(?:advance\s+payment)',
            r'(?:installment|monthly|quarterly|annual)',
        ]
        
        terms = []
        for pattern in payment_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            terms.extend(matches)
        
        # Extract due dates
        due_dates = re.findall(self.patterns['date'], text)
        
        return PaymentTerms(
            payment_terms='; '.join(terms) if terms else None,
            payment_schedule=await self._extract_payment_schedule(text),
            due_dates=due_dates
        )
    
    async def _extract_payment_schedule(self, text: str) -> Optional[str]:
        """Extract payment schedule information"""
        schedule_patterns = [
            r'(?:payment\s+schedule|billing\s+schedule)\s*:?\s*([^\n]+)',
            r'(?:installments?)\s*:?\s*([^\n]+)',
            r'(?:milestone\s+payments?)\s*:?\s*([^\n]+)',
        ]
        
        for pattern in schedule_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None
    
    async def _extract_revenue_classification_enhanced(self, text: str) -> RevenueClassification:
        """Enhanced revenue classification"""
        # Look for revenue-related terms
        revenue_terms = [
            'recurring', 'subscription', 'license', 'maintenance', 'support',
            'one-time', 'setup', 'implementation', 'consulting', 'professional services'
        ]
        
        payment_type = 'unknown'
        for term in revenue_terms:
            if term in text.lower():
                payment_type = term
                break
        
        return RevenueClassification(
            payment_type=payment_type,
            revenue_stream=await self._classify_revenue_stream(text)
        )
    
    async def _classify_revenue_stream(self, text: str) -> str:
        """Classify revenue stream"""
        if any(word in text.lower() for word in ['recurring', 'subscription', 'monthly', 'annual']):
            return 'recurring'
        elif any(word in text.lower() for word in ['one-time', 'setup', 'implementation']):
            return 'one-time'
        else:
            return 'mixed'
    
    async def _extract_sla_enhanced(self, text: str) -> SLA:
        """Enhanced SLA extraction"""
        # Look for SLA-related terms
        sla_terms = [
            'service level agreement', 'sla', 'uptime', 'availability',
            'response time', 'resolution time', 'performance', 'benchmarks'
        ]
        
        sla_info = {}
        for term in sla_terms:
            pattern = f'{term}\\s*:?\\s*([^\\n]+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                sla_info[term] = match.group(1).strip()
        
        return SLA(
            response_time=sla_info.get('response time'),
            resolution_time=sla_info.get('resolution time'),
            uptime_guarantee=sla_info.get('uptime'),
            performance_metrics=list(sla_info.values())
        )
    
    async def _extract_account_info_enhanced(self, text: str) -> AccountInfo:
        """Enhanced account information extraction"""
        # Extract account number
        account_patterns = [
            r'(?:account\s+number|account\s+no)\s*:?\s*([^\n]+)',
            r'(?:billing\s+account)\s*:?\s*([^\n]+)',
        ]
        
        account_number = None
        for pattern in account_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                account_number = match.group(1).strip()
                break
        
        # Extract contact information
        email = self._extract_email_from_context(text)
        phone = self._extract_phone_from_context(text)
        
        return AccountInfo(
            account_number=account_number,
            contact_email=email,
            contact_phone=phone
        )
    
    async def _extract_important_dates(self, text: str) -> Dict[str, str]:
        """Extract important dates from contract"""
        dates = {}
        
        date_patterns = [
            (r'(?:effective\s+date|commencement\s+date)\s*:?\s*([^\n]+)', 'start_date'),
            (r'(?:expiration\s+date|end\s+date)\s*:?\s*([^\n]+)', 'end_date'),
            (r'(?:renewal\s+date)\s*:?\s*([^\n]+)', 'renewal_date'),
            (r'(?:termination\s+date)\s*:?\s*([^\n]+)', 'termination_date'),
        ]
        
        for pattern, date_type in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                dates[date_type] = match.group(1).strip()
        
        return dates
    
    async def _extract_clauses(self, text: str) -> List[Dict[str, Any]]:
        """Extract important clauses from contract"""
        clauses = []
        
        clause_patterns = [
            'termination', 'renewal', 'force majeure', 'confidentiality',
            'intellectual property', 'liability', 'warranty', 'governing law',
            'dispute resolution', 'data protection', 'compliance'
        ]
        
        for clause_type in clause_patterns:
            pattern = f'{clause_type}\\s*:?\\s*([^\\n]+)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                clauses.append({
                    'type': clause_type,
                    'content': match.group(1).strip(),
                    'confidence': 0.8
                })
        
        return clauses
    
    async def _analyze_risk_factors(self, text: str) -> List[str]:
        """Analyze contract for risk factors"""
        risk_factors = []
        
        risk_patterns = [
            'penalty', 'fine', 'breach', 'default', 'termination',
            'liability', 'indemnification', 'force majeure'
        ]
        
        for pattern in risk_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                risk_factors.append(pattern)
        
        return risk_factors
    
    async def _analyze_compliance_issues(self, text: str) -> List[str]:
        """Analyze contract for compliance issues"""
        compliance_issues = []
        
        compliance_patterns = [
            'gdpr', 'data protection', 'privacy', 'confidentiality',
            'intellectual property', 'export control', 'regulatory'
        ]
        
        for pattern in compliance_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                compliance_issues.append(pattern)
        
        return compliance_issues
    
    async def _classify_contract_type(self, text: str) -> str:
        """Classify contract type"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['service', 'consulting', 'support']):
            return 'service_agreement'
        elif any(word in text_lower for word in ['license', 'software', 'technology']):
            return 'license_agreement'
        elif any(word in text_lower for word in ['purchase', 'sale', 'supply']):
            return 'purchase_agreement'
        elif any(word in text_lower for word in ['employment', 'work', 'staff']):
            return 'employment_agreement'
        else:
            return 'general_contract'
    
    async def _calculate_enhanced_confidence_scores(self, parties, financial_details, payment_terms, revenue_classification, sla, account_info) -> Dict[str, float]:
        """Calculate enhanced confidence scores"""
        scores = {}
        
        # Party identification confidence
        if parties:
            avg_party_confidence = sum(p.confidence_score for p in parties) / len(parties)
            scores['party_identification'] = avg_party_confidence * 100
        else:
            scores['party_identification'] = 0.0
        
        # Financial details confidence
        if financial_details and financial_details.total_contract_value:
            scores['financial_details'] = 80.0
        else:
            scores['financial_details'] = 0.0
        
        # Payment terms confidence
        if payment_terms and payment_terms.payment_terms:
            scores['payment_terms'] = 75.0
        else:
            scores['payment_terms'] = 0.0
        
        # Revenue classification confidence
        if revenue_classification and revenue_classification.payment_type != 'unknown':
            scores['revenue_classification'] = 70.0
        else:
            scores['revenue_classification'] = 0.0
        
        # SLA confidence
        if sla and (sla.response_time or sla.resolution_time):
            scores['sla'] = 65.0
        else:
            scores['sla'] = 0.0
        
        # Account info confidence
        if account_info and (account_info.contact_email or account_info.contact_phone):
            scores['contact_information'] = 60.0
        else:
            scores['contact_information'] = 0.0
        
        return scores
    
    def _calculate_field_confidence(self, value: str, field_type: str) -> float:
        """Calculate confidence for a field value"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on field type validation
        if field_type == 'email' and '@' in value:
            confidence += 0.3
        elif field_type == 'date' and re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}', value):
            confidence += 0.3
        elif field_type == 'contract_number' and len(value) > 3:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    async def _generate_processing_notes(self, text: str, metadata: DocumentMetadata, key_value_pairs: List[KeyValuePair]) -> List[str]:
        """Generate processing notes"""
        notes = []
        
        # Document quality notes
        if metadata.total_pages > 10:
            notes.append(f"Large document with {metadata.total_pages} pages")
        
        if len(text) < 1000:
            notes.append("Short document - limited text content")
        
        # Extraction quality notes
        if len(key_value_pairs) > 10:
            notes.append("Rich structured data extracted")
        
        if any(kvp.confidence > 0.8 for kvp in key_value_pairs):
            notes.append("High confidence data extraction")
        
        return notes
    
    async def _generate_contract_summary(
        self, 
        text: str, 
        parties: List[Dict], 
        financial_details: Optional[Dict], 
        payment_terms: Optional[Dict],
        revenue_classification: Optional[Dict],
        sla: Optional[Dict],
        risk_factors: List[str],
        compliance_issues: List[str],
        important_dates: Dict[str, str]
    ) -> 'ContractSummary':
        """Generate a comprehensive contract summary"""
        try:
            # Extract party names
            party_names = [party.get('name', 'Unknown') for party in parties if party.get('name')]
            
            # Generate overview
            overview = await self._generate_overview(text, party_names, financial_details)
            
            # Extract key terms
            key_terms = await self._extract_key_terms(text)
            
            # Generate financial summary
            financial_summary = await self._generate_financial_summary(financial_details)
            
            # Calculate contract duration
            contract_duration = await self._calculate_contract_duration(important_dates)
            
            # Extract main obligations
            main_obligations = await self._extract_main_obligations(text, parties)
            
            # Assess risk level
            risk_level = await self._assess_risk_level(risk_factors, compliance_issues)
            
            # Assess compliance status
            compliance_status = await self._assess_compliance_status(compliance_issues)
            
            return ContractSummary(
                overview=overview,
                parties_involved=party_names,
                key_terms=key_terms,
                financial_summary=financial_summary,
                contract_duration=contract_duration,
                main_obligations=main_obligations,
                risk_level=risk_level,
                compliance_status=compliance_status
            )
            
        except Exception as e:
            logger.error(f"Error generating contract summary: {str(e)}")
            return ContractSummary(
                overview="Summary generation failed",
                parties_involved=[],
                key_terms=[],
                financial_summary="Unable to generate financial summary",
                contract_duration="Unknown",
                main_obligations=[],
                risk_level="Unknown",
                compliance_status="Unknown"
            )
    
    async def _generate_overview(self, text: str, party_names: List[str], financial_details: Optional[Dict]) -> str:
        """Generate a high-level overview of the contract"""
        try:
            # Extract contract type and purpose
            contract_type = await self._classify_contract_type(text)
            
            # Get financial value if available
            financial_value = ""
            if financial_details and financial_details.get('total_contract_value'):
                currency = financial_details.get('currency', 'USD')
                value = financial_details.get('total_contract_value', 0)
                financial_value = f" valued at {currency} {value:,}"
            
            # Create overview
            parties_text = ", ".join(party_names[:2])  # Limit to first 2 parties
            if len(party_names) > 2:
                parties_text += f" and {len(party_names) - 2} other parties"
            
            overview = f"This {contract_type} contract involves {parties_text}{financial_value}. "
            
            # Add purpose based on contract type
            if "service" in contract_type.lower():
                overview += "The contract establishes service delivery terms and performance standards."
            elif "supply" in contract_type.lower():
                overview += "The contract governs the supply of goods and delivery terms."
            elif "license" in contract_type.lower():
                overview += "The contract grants licensing rights and usage terms."
            else:
                overview += "The contract defines the business relationship and terms of engagement."
            
            return overview
            
        except Exception as e:
            logger.error(f"Error generating overview: {str(e)}")
            return "Contract overview could not be generated."
    
    async def _extract_key_terms(self, text: str) -> List[str]:
        """Extract key terms and conditions from the contract"""
        try:
            key_terms = []
            
            # Common contract terms to look for
            term_patterns = [
                r'(?:payment terms?|payment conditions?)[:\s]*([^.\n]+)',
                r'(?:termination|cancellation)[:\s]*([^.\n]+)',
                r'(?:liability|indemnification)[:\s]*([^.\n]+)',
                r'(?:confidentiality|non-disclosure)[:\s]*([^.\n]+)',
                r'(?:warranty|guarantee)[:\s]*([^.\n]+)',
                r'(?:force majeure|act of god)[:\s]*([^.\n]+)',
                r'(?:governing law|jurisdiction)[:\s]*([^.\n]+)',
                r'(?:dispute resolution|arbitration)[:\s]*([^.\n]+)'
            ]
            
            for pattern in term_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    term = match.strip()
                    if len(term) > 10 and len(term) < 200:  # Reasonable length
                        key_terms.append(term)
            
            # Remove duplicates and limit to top 8
            key_terms = list(dict.fromkeys(key_terms))[:8]
            
            return key_terms
            
        except Exception as e:
            logger.error(f"Error extracting key terms: {str(e)}")
            return []
    
    async def _generate_financial_summary(self, financial_details: Optional[Dict]) -> str:
        """Generate a summary of financial aspects"""
        try:
            if not financial_details:
                return "Financial details not available"
            
            summary_parts = []
            
            # Total value
            if financial_details.get('total_contract_value'):
                currency = financial_details.get('currency', 'USD')
                value = financial_details.get('total_contract_value', 0)
                summary_parts.append(f"Total contract value: {currency} {value:,}")
            
            # Payment type
            if financial_details.get('line_items'):
                line_items = financial_details.get('line_items', [])
                if line_items:
                    summary_parts.append(f"{len(line_items)} line items identified")
            
            # Tax information
            if financial_details.get('tax_amount'):
                tax = financial_details.get('tax_amount', 0)
                summary_parts.append(f"Tax amount: {tax}")
            
            return "; ".join(summary_parts) if summary_parts else "Basic financial information available"
            
        except Exception as e:
            logger.error(f"Error generating financial summary: {str(e)}")
            return "Financial summary unavailable"
    
    async def _calculate_contract_duration(self, important_dates: Dict[str, str]) -> str:
        """Calculate contract duration"""
        try:
            start_date = important_dates.get('start_date')
            end_date = important_dates.get('end_date')
            
            if start_date and end_date:
                try:
                    from datetime import datetime
                    start = datetime.strptime(start_date, '%Y-%m-%d')
                    end = datetime.strptime(end_date, '%Y-%m-%d')
                    duration = (end - start).days
                    
                    if duration < 30:
                        return f"{duration} days"
                    elif duration < 365:
                        months = duration // 30
                        return f"{months} months"
                    else:
                        years = duration // 365
                        return f"{years} years"
                except:
                    return f"From {start_date} to {end_date}"
            elif start_date:
                return f"Starting {start_date}"
            elif end_date:
                return f"Ending {end_date}"
            else:
                return "Duration not specified"
                
        except Exception as e:
            logger.error(f"Error calculating contract duration: {str(e)}")
            return "Duration unknown"
    
    async def _extract_main_obligations(self, text: str, parties: List[Dict]) -> List[str]:
        """Extract main obligations from the contract"""
        try:
            obligations = []
            
            # Look for obligation patterns
            obligation_patterns = [
                r'(?:shall|must|will|agrees to|undertakes to)[:\s]*([^.\n]+)',
                r'(?:obligation|responsibility|duty)[:\s]*([^.\n]+)',
                r'(?:deliver|provide|supply|perform)[:\s]*([^.\n]+)',
                r'(?:maintain|ensure|guarantee)[:\s]*([^.\n]+)'
            ]
            
            for pattern in obligation_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    obligation = match.strip()
                    if len(obligation) > 15 and len(obligation) < 150:
                        obligations.append(obligation)
            
            # Remove duplicates and limit to top 5
            obligations = list(dict.fromkeys(obligations))[:5]
            
            return obligations
            
        except Exception as e:
            logger.error(f"Error extracting main obligations: {str(e)}")
            return []
    
    async def _assess_risk_level(self, risk_factors: List[str], compliance_issues: List[str]) -> str:
        """Assess the overall risk level of the contract"""
        try:
            total_issues = len(risk_factors) + len(compliance_issues)
            
            if total_issues == 0:
                return "Low"
            elif total_issues <= 3:
                return "Medium"
            elif total_issues <= 6:
                return "High"
            else:
                return "Very High"
                
        except Exception as e:
            logger.error(f"Error assessing risk level: {str(e)}")
            return "Unknown"
    
    async def _assess_compliance_status(self, compliance_issues: List[str]) -> str:
        """Assess compliance status"""
        try:
            if not compliance_issues:
                return "Compliant"
            elif len(compliance_issues) <= 2:
                return "Minor Issues"
            elif len(compliance_issues) <= 5:
                return "Moderate Issues"
            else:
                return "Significant Issues"
                
        except Exception as e:
            logger.error(f"Error assessing compliance status: {str(e)}")
            return "Unknown"
    
    def _convert_ai_parties(self, ai_parties: List[Dict]) -> List[Party]:
        """Convert AI party data to Party objects"""
        parties = []
        for party_data in ai_parties:
            try:
                party = Party(
                    name=party_data.get("name", "Unknown"),
                    role=party_data.get("role", "unknown"),
                    email=party_data.get("email"),
                    phone=party_data.get("phone"),
                    address=party_data.get("address"),
                    legal_entity=party_data.get("legal_entity"),
                    registration_number=party_data.get("registration_number")
                )
                parties.append(party)
            except Exception as e:
                logger.error(f"Error converting AI party data: {str(e)}")
                continue
        return parties
    
    def _convert_ai_financial(self, ai_financial: Dict) -> Optional[FinancialDetails]:
        """Convert AI financial data to FinancialDetails object"""
        try:
            if not ai_financial:
                return None
            
            return FinancialDetails(
                total_contract_value=ai_financial.get("total_contract_value", 0),
                currency=ai_financial.get("currency", "USD"),
                line_items=ai_financial.get("line_items", []),
                tax_amount=ai_financial.get("tax_amount", 0),
                additional_fees=ai_financial.get("additional_fees", 0)
            )
        except Exception as e:
            logger.error(f"Error converting AI financial data: {str(e)}")
            return None
    
    def _convert_ai_payment_terms(self, ai_payment: Dict) -> Optional[PaymentTerms]:
        """Convert AI payment terms data to PaymentTerms object"""
        try:
            if not ai_payment:
                return None
            
            return PaymentTerms(
                payment_terms=ai_payment.get("payment_terms"),
                payment_schedule=ai_payment.get("payment_schedule"),
                due_dates=ai_payment.get("due_dates", []),
                payment_methods=ai_payment.get("payment_methods", []),
                banking_details=ai_payment.get("banking_details")
            )
        except Exception as e:
            logger.error(f"Error converting AI payment terms: {str(e)}")
            return None
    
    def _convert_ai_revenue(self, ai_revenue: Dict) -> Optional[RevenueClassification]:
        """Convert AI revenue data to RevenueClassification object"""
        try:
            if not ai_revenue:
                return None
            
            return RevenueClassification(
                payment_type=ai_revenue.get("payment_type", "unknown"),
                billing_cycle=ai_revenue.get("billing_cycle"),
                subscription_model=ai_revenue.get("subscription_model"),
                auto_renewal=ai_revenue.get("auto_renewal", False)
            )
        except Exception as e:
            logger.error(f"Error converting AI revenue data: {str(e)}")
            return None
    
    def _convert_ai_sla(self, ai_sla: Dict) -> Optional[SLA]:
        """Convert AI SLA data to SLA object"""
        try:
            if not ai_sla:
                return None
            
            return SLA(
                performance_metrics=ai_sla.get("performance_metrics", []),
                penalty_clauses=ai_sla.get("penalty_clauses", []),
                support_terms=ai_sla.get("support_terms"),
                maintenance_terms=ai_sla.get("maintenance_terms")
            )
        except Exception as e:
            logger.error(f"Error converting AI SLA data: {str(e)}")
            return None
    
    def _convert_ai_account_info(self, ai_parties: List[Dict]) -> Optional[AccountInfo]:
        """Convert AI party data to AccountInfo object"""
        try:
            if not ai_parties:
                return None
            
            # Use the first party as primary contact
            primary_party = ai_parties[0] if ai_parties else {}
            
            return AccountInfo(
                account_number=primary_party.get("registration_number"),
                billing_address=primary_party.get("address"),
                contact_email=primary_party.get("email"),
                contact_phone=primary_party.get("phone"),
                technical_support_contact=primary_party.get("email")
            )
        except Exception as e:
            logger.error(f"Error converting AI account info: {str(e)}")
            return None
    
    def _convert_ai_summary(self, ai_summary: Dict) -> Optional[ContractSummary]:
        """Convert AI summary data to ContractSummary object"""
        try:
            if not ai_summary:
                return None
            
            return ContractSummary(
                overview=ai_summary.get("overview", "Summary not available"),
                parties_involved=ai_summary.get("parties_involved", []),
                key_terms=ai_summary.get("key_terms", []),
                financial_summary=ai_summary.get("financial_summary", "Financial details not available"),
                contract_duration=ai_summary.get("contract_duration", "Unknown"),
                main_obligations=ai_summary.get("main_obligations", []),
                risk_level=ai_summary.get("risk_level", "Unknown"),
                compliance_status=ai_summary.get("compliance_status", "Unknown")
            )
        except Exception as e:
            logger.error(f"Error converting AI summary: {str(e)}")
            return None
