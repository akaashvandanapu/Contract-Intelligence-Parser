import PyPDF2
import re
from typing import Dict, List, Optional, Any
from .models import ContractData, Party, AccountInfo, FinancialDetails, LineItem, PaymentTerms, RevenueClassification, SLA
from .enhanced_parser import EnhancedContractParser
import logging

logger = logging.getLogger(__name__)

class ContractParser:
    def __init__(self):
        self.enhanced_parser = EnhancedContractParser()
        self.patterns = {
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'(\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})',
            'currency': r'\$[\d,]+\.?\d*|\d+\.?\d*\s*(USD|EUR|GBP|CAD)',
            'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b\d{4}[/-]\d{1,2}[/-]\d{1,2}\b',
            'net_terms': r'net\s+(\d+)',
            'payment_terms': r'(net\s+\d+|due\s+upon\s+receipt|cod|cash\s+on\s+delivery)',
            'company_name': r'(?:inc|llc|ltd|corp|corporation|company|co\.?)\b',
            'address': r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Lane|Ln)',
        }

    async def parse_contract(self, file_path: str) -> ContractData:
        """Parse a contract PDF and extract structured data using enhanced parser"""
        try:
            # Use enhanced parser for better extraction
            return await self.enhanced_parser.parse_contract(file_path)
            
        except Exception as e:
            logger.error(f"Error parsing contract: {str(e)}")
            # Fallback to basic parsing
            return await self._parse_contract_basic(file_path)
    
    async def _parse_contract_basic(self, file_path: str) -> ContractData:
        """Basic contract parsing as fallback"""
        try:
            # Extract text from PDF
            text = await self._extract_text_from_pdf(file_path)
            
            # Parse different sections
            parties = self._extract_parties(text)
            account_info = self._extract_account_info(text)
            financial_details = self._extract_financial_details(text)
            payment_terms = self._extract_payment_terms(text)
            revenue_classification = self._extract_revenue_classification(text)
            sla = self._extract_sla(text)
            
            # Calculate confidence scores
            confidence_scores = self._calculate_confidence_scores(
                parties, account_info, financial_details, payment_terms, revenue_classification, sla
            )
            
            return ContractData(
                parties=parties,
                account_info=account_info,
                financial_details=financial_details,
                payment_terms=payment_terms,
                revenue_classification=revenue_classification,
                sla=sla,
                contract_start_date=self._extract_dates(text, "start"),
                contract_end_date=self._extract_dates(text, "end"),
                contract_type=self._extract_contract_type(text),
                confidence_scores=confidence_scores
            )
        
        except Exception as e:
            logger.error(f"Error in basic contract parsing: {str(e)}")
            raise

    async def _extract_text_from_pdf(self, file_path: str) -> str:
        """Extract text from PDF file"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {str(e)}")
            raise

    def _extract_parties(self, text: str) -> List[Party]:
        """Extract contract parties"""
        parties = []
        
        # Look for common party indicators
        party_indicators = [
            r'between\s+([^,]+(?:inc|llc|ltd|corp|corporation|company|co\.?)[^,]*),?\s*(?:a\s+)?([^,]+(?:inc|llc|ltd|corp|corporation|company|co\.?)[^,]*)',
            r'party\s+1[:\s]*([^,\n]+)',
            r'party\s+2[:\s]*([^,\n]+)',
            r'customer[:\s]*([^,\n]+)',
            r'vendor[:\s]*([^,\n]+)',
            r'client[:\s]*([^,\n]+)',
            r'supplier[:\s]*([^,\n]+)'
        ]
        
        for pattern in party_indicators:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 1:
                    party_name = match.group(1).strip()
                    if party_name and len(party_name) > 3:
                        # Determine role based on context
                        role = "vendor"
                        if any(keyword in match.group(0).lower() for keyword in ["customer", "client"]):
                            role = "customer"
                        elif "supplier" in match.group(0).lower():
                            role = "vendor"
                        
                        party = Party(
                            name=party_name,
                            role=role,
                            email=self._extract_email_from_context(text, party_name),
                            phone=self._extract_phone_from_context(text, party_name)
                        )
                        parties.append(party)
        
        # Remove duplicates
        unique_parties = []
        seen_names = set()
        for party in parties:
            if party.name.lower() not in seen_names:
                unique_parties.append(party)
                seen_names.add(party.name.lower())
        
        return unique_parties

    def _extract_account_info(self, text: str) -> Optional[AccountInfo]:
        """Extract account information"""
        account_number = None
        billing_address = None
        contact_email = None
        contact_phone = None
        
        # Look for account number patterns
        account_patterns = [
            r'account\s+number[:\s]*([A-Za-z0-9-]+)',
            r'account\s+no[:\s]*([A-Za-z0-9-]+)',
            r'acct[:\s]*([A-Za-z0-9-]+)'
        ]
        
        for pattern in account_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                account_number = match.group(1).strip()
                break
        
        # Look for billing address
        billing_patterns = [
            r'billing\s+address[:\s]*([^\n]+)',
            r'invoice\s+address[:\s]*([^\n]+)'
        ]
        
        for pattern in billing_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                billing_address = match.group(1).strip()
                break
        
        # Extract contact information
        emails = re.findall(self.patterns['email'], text)
        phones = re.findall(self.patterns['phone'], text)
        
        if emails:
            contact_email = emails[0]
        if phones:
            contact_phone = ''.join(phones[0])
        
        if account_number or billing_address or contact_email or contact_phone:
            return AccountInfo(
                account_number=account_number,
                billing_address=billing_address,
                contact_email=contact_email,
                contact_phone=contact_phone
            )
        
        return None

    def _extract_financial_details(self, text: str) -> Optional[FinancialDetails]:
        """Extract financial details"""
        line_items = []
        total_value = None
        currency = "USD"
        
        # Look for line items
        line_item_patterns = [
            r'(\d+)\s*x\s*([^$]+?)\s*@\s*\$?([\d,]+\.?\d*)',
            r'([^$]+?)\s*\$?([\d,]+\.?\d*)\s*each',
            r'item[:\s]*([^$]+?)\s*\$?([\d,]+\.?\d*)'
        ]
        
        for pattern in line_item_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 2:
                    description = match.group(1).strip()
                    if len(match.groups()) == 3:
                        quantity = float(match.group(1).replace(',', ''))
                        unit_price = float(match.group(3).replace(',', ''))
                        total_price = quantity * unit_price
                    else:
                        quantity = 1
                        unit_price = float(match.group(2).replace(',', ''))
                        total_price = unit_price
                    
                    line_item = LineItem(
                        description=description,
                        quantity=quantity,
                        unit_price=unit_price,
                        total_price=total_price,
                        currency=currency
                    )
                    line_items.append(line_item)
        
        # Look for total contract value
        total_patterns = [
            r'total\s+contract\s+value[:\s]*\$?([\d,]+\.?\d*)',
            r'total\s+amount[:\s]*\$?([\d,]+\.?\d*)',
            r'contract\s+value[:\s]*\$?([\d,]+\.?\d*)',
            r'total[:\s]*\$?([\d,]+\.?\d*)'
        ]
        
        for pattern in total_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                total_value = float(match.group(1).replace(',', ''))
                break
        
        if line_items or total_value:
            return FinancialDetails(
                line_items=line_items,
                total_contract_value=total_value,
                currency=currency
            )
        
        return None

    def _extract_payment_terms(self, text: str) -> Optional[PaymentTerms]:
        """Extract payment terms"""
        payment_terms = None
        payment_schedule = None
        due_dates = []
        payment_methods = []
        
        # Look for payment terms
        terms_match = re.search(self.patterns['payment_terms'], text, re.IGNORECASE)
        if terms_match:
            payment_terms = terms_match.group(0)
        
        # Look for payment schedule
        schedule_patterns = [
            r'payment\s+schedule[:\s]*([^\n]+)',
            r'billing\s+schedule[:\s]*([^\n]+)'
        ]
        
        for pattern in schedule_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                payment_schedule = match.group(1).strip()
                break
        
        # Look for due dates
        dates = re.findall(self.patterns['date'], text)
        due_dates = dates[:5]  # Limit to first 5 dates
        
        # Look for payment methods
        method_patterns = [
            r'payment\s+method[:\s]*([^\n]+)',
            r'payment\s+by[:\s]*([^\n]+)'
        ]
        
        for pattern in method_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                payment_methods.append(match.group(1).strip())
        
        if payment_terms or payment_schedule or due_dates or payment_methods:
            return PaymentTerms(
                payment_terms=payment_terms,
                payment_schedule=payment_schedule,
                due_dates=due_dates,
                payment_methods=payment_methods
            )
        
        return None

    def _extract_revenue_classification(self, text: str) -> Optional[RevenueClassification]:
        """Extract revenue classification"""
        payment_type = "one_time"
        billing_cycle = None
        subscription_model = None
        renewal_terms = None
        auto_renewal = None
        
        # Determine payment type
        if any(keyword in text.lower() for keyword in ["recurring", "monthly", "quarterly", "annually", "subscription"]):
            payment_type = "recurring"
        elif any(keyword in text.lower() for keyword in ["one-time", "one time", "single payment"]):
            payment_type = "one_time"
        elif any(keyword in text.lower() for keyword in ["recurring", "monthly", "quarterly", "annually"]) and any(keyword in text.lower() for keyword in ["one-time", "one time"]):
            payment_type = "mixed"
        
        # Look for billing cycle
        cycle_patterns = [
            r'billing\s+cycle[:\s]*([^\n]+)',
            r'payment\s+frequency[:\s]*([^\n]+)'
        ]
        
        for pattern in cycle_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                billing_cycle = match.group(1).strip()
                break
        
        # Look for subscription model
        if "subscription" in text.lower():
            subscription_model = "subscription"
        
        # Look for renewal terms
        renewal_patterns = [
            r'renewal\s+terms[:\s]*([^\n]+)',
            r'auto\s+renewal[:\s]*([^\n]+)'
        ]
        
        for pattern in renewal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                renewal_terms = match.group(1).strip()
                break
        
        # Check for auto-renewal
        if "auto renewal" in text.lower() or "automatic renewal" in text.lower():
            auto_renewal = True
        elif "no auto renewal" in text.lower() or "manual renewal" in text.lower():
            auto_renewal = False
        
        return RevenueClassification(
            payment_type=payment_type,
            billing_cycle=billing_cycle,
            subscription_model=subscription_model,
            renewal_terms=renewal_terms,
            auto_renewal=auto_renewal
        )

    def _extract_sla(self, text: str) -> Optional[SLA]:
        """Extract SLA information"""
        performance_metrics = []
        benchmarks = []
        penalty_clauses = []
        remedies = []
        support_terms = None
        maintenance_terms = None
        
        # Look for performance metrics
        metric_patterns = [
            r'uptime[:\s]*([^\n]+)',
            r'response\s+time[:\s]*([^\n]+)',
            r'performance\s+level[:\s]*([^\n]+)'
        ]
        
        for pattern in metric_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                performance_metrics.append(match.group(1).strip())
        
        # Look for penalty clauses
        penalty_patterns = [
            r'penalty[:\s]*([^\n]+)',
            r'penalty\s+clause[:\s]*([^\n]+)'
        ]
        
        for pattern in penalty_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                penalty_clauses.append(match.group(1).strip())
        
        # Look for support terms
        support_patterns = [
            r'support\s+terms[:\s]*([^\n]+)',
            r'technical\s+support[:\s]*([^\n]+)'
        ]
        
        for pattern in support_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                support_terms = match.group(1).strip()
                break
        
        # Look for maintenance terms
        maintenance_patterns = [
            r'maintenance\s+terms[:\s]*([^\n]+)',
            r'maintenance\s+agreement[:\s]*([^\n]+)'
        ]
        
        for pattern in maintenance_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                maintenance_terms = match.group(1).strip()
                break
        
        if performance_metrics or penalty_clauses or support_terms or maintenance_terms:
            return SLA(
                performance_metrics=performance_metrics,
                benchmarks=benchmarks,
                penalty_clauses=penalty_clauses,
                remedies=remedies,
                support_terms=support_terms,
                maintenance_terms=maintenance_terms
            )
        
        return None

    def _extract_dates(self, text: str, date_type: str) -> Optional[str]:
        """Extract contract start or end dates"""
        if date_type == "start":
            patterns = [
                r'contract\s+start[:\s]*([^\n]+)',
                r'effective\s+date[:\s]*([^\n]+)',
                r'commencement\s+date[:\s]*([^\n]+)'
            ]
        else:  # end
            patterns = [
                r'contract\s+end[:\s]*([^\n]+)',
                r'expiration\s+date[:\s]*([^\n]+)',
                r'termination\s+date[:\s]*([^\n]+)'
            ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        return None

    def _extract_contract_type(self, text: str) -> Optional[str]:
        """Extract contract type"""
        contract_types = [
            "service agreement", "purchase order", "license agreement",
            "maintenance contract", "consulting agreement", "supply agreement"
        ]
        
        text_lower = text.lower()
        for contract_type in contract_types:
            if contract_type in text_lower:
                return contract_type.title()
        
        return None

    def _extract_email_from_context(self, text: str, party_name: str) -> Optional[str]:
        """Extract email associated with a party"""
        # Look for email near the party name
        party_context = self._get_context_around_text(text, party_name, 200)
        emails = re.findall(self.patterns['email'], party_context)
        return emails[0] if emails else None

    def _extract_phone_from_context(self, text: str, party_name: str) -> Optional[str]:
        """Extract phone associated with a party"""
        # Look for phone near the party name
        party_context = self._get_context_around_text(text, party_name, 200)
        phones = re.findall(self.patterns['phone'], party_context)
        return ''.join(phones[0]) if phones else None

    def _get_context_around_text(self, text: str, search_text: str, context_length: int) -> str:
        """Get context around a specific text"""
        index = text.lower().find(search_text.lower())
        if index == -1:
            return ""
        
        start = max(0, index - context_length)
        end = min(len(text), index + len(search_text) + context_length)
        return text[start:end]

    def _calculate_confidence_scores(self, parties, account_info, financial_details, payment_terms, revenue_classification, sla) -> Dict[str, float]:
        """Calculate confidence scores for extracted data"""
        scores = {}
        
        # Party identification confidence
        party_score = min(100, len(parties) * 25) if parties else 0
        scores["party_identification"] = party_score
        
        # Account info confidence
        account_score = 0
        if account_info:
            if account_info.account_number:
                account_score += 30
            if account_info.billing_address:
                account_score += 25
            if account_info.contact_email:
                account_score += 25
            if account_info.contact_phone:
                account_score += 20
        scores["account_info"] = account_score
        
        # Financial details confidence
        financial_score = 0
        if financial_details:
            if financial_details.total_contract_value:
                financial_score += 40
            if financial_details.line_items:
                financial_score += 30
            if financial_details.currency:
                financial_score += 10
            if financial_details.tax_amount:
                financial_score += 20
        scores["financial_details"] = financial_score
        
        # Payment terms confidence
        payment_score = 0
        if payment_terms:
            if payment_terms.payment_terms:
                payment_score += 40
            if payment_terms.payment_schedule:
                payment_score += 30
            if payment_terms.due_dates:
                payment_score += 20
            if payment_terms.payment_methods:
                payment_score += 10
        scores["payment_terms"] = payment_score
        
        # Revenue classification confidence
        revenue_score = 0
        if revenue_classification:
            if revenue_classification.payment_type:
                revenue_score += 40
            if revenue_classification.billing_cycle:
                revenue_score += 30
            if revenue_classification.subscription_model:
                revenue_score += 20
            if revenue_classification.auto_renewal is not None:
                revenue_score += 10
        scores["revenue_classification"] = revenue_score
        
        # SLA confidence
        sla_score = 0
        if sla:
            if sla.performance_metrics:
                sla_score += 30
            if sla.penalty_clauses:
                sla_score += 25
            if sla.support_terms:
                sla_score += 25
            if sla.maintenance_terms:
                sla_score += 20
        scores["sla"] = sla_score
        
        return scores
