from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

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
