import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from pdf2image import convert_from_path
import cv2
import numpy as np
from PIL import Image
import re
import spacy
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import dateparser
import phonenumbers
from email_validator import validate_email, EmailNotValidError
from fuzzywuzzy import fuzz
import logging
from .models import ContractData, Party, KeyValuePair, DocumentMetadata, FinancialDetails, PaymentTerms, RevenueClassification, SLA, AccountInfo

logger = logging.getLogger(__name__)

class EnhancedContractParser:
    def __init__(self):
        self.nlp = None
        self._load_nlp_model()
        self.patterns = self._initialize_patterns()
        
    def _load_nlp_model(self):
        """Load spaCy model for NLP processing"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
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
        """Enhanced contract parsing with OCR and advanced extraction"""
        try:
            # Extract text using multiple methods
            text_content = await self._extract_text_enhanced(file_path)
            
            # Extract metadata
            metadata = await self._extract_metadata(file_path)
            
            # Extract key-value pairs
            key_value_pairs = await self._extract_key_value_pairs(text_content)
            
            # Extract structured data
            parties = await self._extract_parties_enhanced(text_content)
            financial_details = await self._extract_financial_details_enhanced(text_content)
            payment_terms = await self._extract_payment_terms_enhanced(text_content)
            revenue_classification = await self._extract_revenue_classification_enhanced(text_content)
            sla = await self._extract_sla_enhanced(text_content)
            account_info = await self._extract_account_info_enhanced(text_content)
            
            # Extract dates and clauses
            important_dates = await self._extract_important_dates(text_content)
            clauses = await self._extract_clauses(text_content)
            
            # Risk and compliance analysis
            risk_factors = await self._analyze_risk_factors(text_content)
            compliance_issues = await self._analyze_compliance_issues(text_content)
            
            # Calculate confidence scores
            confidence_scores = await self._calculate_enhanced_confidence_scores(
                parties, financial_details, payment_terms, revenue_classification, sla, account_info
            )
            
            # Processing notes
            processing_notes = await self._generate_processing_notes(
                text_content, metadata, key_value_pairs
            )
            
            return ContractData(
                parties=parties,
                account_info=account_info,
                financial_details=financial_details,
                payment_terms=payment_terms,
                revenue_classification=revenue_classification,
                sla=sla,
                contract_start_date=important_dates.get('start_date'),
                contract_end_date=important_dates.get('end_date'),
                contract_type=await self._classify_contract_type(text_content),
                confidence_scores=confidence_scores,
                key_value_pairs=key_value_pairs,
                document_metadata=metadata,
                extracted_text=text_content,
                processing_notes=processing_notes,
                risk_factors=risk_factors,
                compliance_issues=compliance_issues,
                important_dates=[{"date": k, "description": v} for k, v in important_dates.items()],
                clauses=clauses
            )
            
        except Exception as e:
            logger.error(f"Error in enhanced contract parsing: {str(e)}")
            raise
    
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
    
    def _preprocess_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
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
