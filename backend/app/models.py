from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from enum import Enum
import re

class ContractStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class Party(BaseModel):
    name: str
    legal_entity: Optional[str] = None
    registration_number: Optional[str] = None
    address: Optional[str] = None
    contact_person: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str  # customer, vendor, third_party
    confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    tax_id: Optional[str] = None
    website: Optional[str] = None
    jurisdiction: Optional[str] = None
    
    @validator('email')
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            return None
        return v

class AccountInfo(BaseModel):
    account_number: Optional[str] = None
    billing_address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    technical_support_contact: Optional[str] = None

class LineItem(BaseModel):
    description: str
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total_price: Optional[float] = None
    currency: Optional[str] = None

class FinancialDetails(BaseModel):
    line_items: List[LineItem] = []
    total_contract_value: Optional[float] = None
    currency: Optional[str] = None
    tax_amount: Optional[float] = None
    additional_fees: Optional[float] = None

class PaymentTerms(BaseModel):
    payment_terms: Optional[str] = None  # Net 30, Net 60, etc.
    payment_schedule: Optional[str] = None
    due_dates: List[str] = []
    payment_methods: List[str] = []
    banking_details: Optional[str] = None

class RevenueClassification(BaseModel):
    payment_type: str  # recurring, one_time, mixed
    billing_cycle: Optional[str] = None  # monthly, quarterly, annually
    subscription_model: Optional[str] = None
    renewal_terms: Optional[str] = None
    auto_renewal: Optional[bool] = None

class SLA(BaseModel):
    performance_metrics: List[str] = []
    benchmarks: List[str] = []
    penalty_clauses: List[str] = []
    remedies: List[str] = []
    support_terms: Optional[str] = None
    maintenance_terms: Optional[str] = None

class KeyValuePair(BaseModel):
    key: str
    value: str
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    field_type: str  # text, number, date, email, phone, etc.

class DocumentMetadata(BaseModel):
    total_pages: int
    file_size: int
    creation_date: Optional[str] = None
    modification_date: Optional[str] = None
    author: Optional[str] = None
    title: Optional[str] = None
    subject: Optional[str] = None
    keywords: Optional[str] = None
    producer: Optional[str] = None

class ContractData(BaseModel):
    parties: List[Party] = []
    account_info: Optional[AccountInfo] = None
    financial_details: Optional[FinancialDetails] = None
    payment_terms: Optional[PaymentTerms] = None
    revenue_classification: Optional[RevenueClassification] = None
    sla: Optional[SLA] = None
    contract_start_date: Optional[str] = None
    contract_end_date: Optional[str] = None
    contract_type: Optional[str] = None
    confidence_scores: Dict[str, float] = {}
    
    # Enhanced fields
    key_value_pairs: List[KeyValuePair] = []
    document_metadata: Optional[DocumentMetadata] = None
    extracted_text: Optional[str] = None
    processing_notes: List[str] = []
    risk_factors: List[str] = []
    compliance_issues: List[str] = []
    important_dates: List[Dict[str, str]] = []
    clauses: List[Dict[str, Any]] = []

class Contract(BaseModel):
    id: str
    filename: str
    file_path: str
    status: ContractStatus
    uploaded_at: datetime
    updated_at: Optional[datetime] = None
    file_size: Optional[int] = None
    parsed_data: Optional[ContractData] = None
    score: Optional[float] = None
    gaps: List[str] = []
    progress: int = 0
    error: Optional[str] = None

class ContractListResponse(BaseModel):
    contracts: List[Dict[str, Any]]
    total: int
    skip: int
    limit: int

class ContractUploadResponse(BaseModel):
    contract_id: str
    status: str
    message: str

class ContractStatusResponse(BaseModel):
    contract_id: str
    status: ContractStatus
    progress: int
    error: Optional[str] = None
    updated_at: Optional[datetime] = None
