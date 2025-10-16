# Contract Intelligence Parser API Documentation

## Overview

The Contract Intelligence Parser API is a comprehensive system for automated contract analysis and data extraction. It processes PDF contracts using advanced RAG (Retrieval-Augmented Generation) techniques, Gemini AI integration, and intelligent scoring systems to extract critical financial and operational data with high accuracy.

## Base URL

```
http://localhost:8000
```

## Key Features

- **RAG-Based Parsing** - Advanced Retrieval-Augmented Generation for flexible contract analysis
- **Gemini AI Integration** - Google's advanced language model for intelligent data extraction
- **Weighted Scoring System** - Multi-factor confidence scoring with gap analysis
- **MongoDB Atlas Integration** - Cloud-hosted database with SSL security
- **Asynchronous Processing** - Non-blocking contract analysis with real-time status updates

## Authentication

Currently, no authentication is required. In production, implement proper API key or JWT authentication.

## Endpoints

### 1. Upload Contract

**POST** `/contracts/upload`

Upload a PDF contract for processing.

**Request:**

- **Content-Type:** `multipart/form-data`
- **Body:** PDF file (max 50MB)

**Response:**

```json
{
  "contract_id": "uuid-string",
  "status": "uploaded",
  "message": "Contract uploaded successfully"
}
```

**Error Responses:**

- `400 Bad Request`: Invalid file type, size, or format
- `500 Internal Server Error`: Server processing error

### 2. Get Contract Status

**GET** `/contracts/{contract_id}/status`

Check the processing status of a contract.

**Response:**

```json
{
  "contract_id": "uuid-string",
  "status": "completed|processing|pending|failed",
  "progress": 85,
  "gaps": ["Missing payment terms", "Incomplete party information"],
  "updated_at": "2023-01-01T00:00:00Z"
}
```

### 3. Get Contract Data

**GET** `/contracts/{contract_id}`

Retrieve parsed contract data (only available when processing is complete).

**Response:**

```json
{
  "parties": [
    {
      "name": "Company Name",
      "role": "customer",
      "email": "contact@company.com",
      "phone": "(555) 123-4567",
      "confidence_score": 0.95
    }
  ],
  "financial_details": {
    "total_contract_value": 50000,
    "currency": "USD",
    "line_items": [
      {
        "description": "Software License",
        "quantity": 10,
        "unit_price": 2000,
        "total_price": 20000
      }
    ]
  },
  "payment_terms": {
    "payment_terms": "Net 30",
    "payment_schedule": "Monthly",
    "due_dates": ["2023-01-15", "2023-02-15"]
  },
  "confidence_scores": {
    "party_identification": 85,
    "financial_details": 90,
    "payment_terms": 75
  }
}
```

### 4. List Contracts

**GET** `/contracts`

Get a paginated list of all contracts with filtering and sorting.

**Query Parameters:**

- `skip` (int, default: 0): Number of records to skip
- `limit` (int, default: 10, max: 100): Number of records to return
- `status` (string, optional): Filter by status (pending, processing, completed, failed)
- `sort_by` (string, default: "uploaded_at"): Sort field
- `sort_order` (string, default: "desc"): Sort order (asc, desc)

**Response:**

```json
{
  "contracts": [
    {
      "id": "uuid-string",
      "filename": "contract.pdf",
      "status": "completed",
      "uploaded_at": "2023-01-01T00:00:00Z",
      "file_size": 1024000,
      "score": 85,
      "progress": 100
    }
  ],
  "total": 25,
  "skip": 0,
  "limit": 10
}
```

### 5. Download Contract

**GET** `/contracts/{contract_id}/download`

Download the original contract file.

**Response:**

- **Content-Type:** `application/pdf`
- **Body:** Binary PDF file

### 6. Health Check

**GET** `/health`

Check API health status.

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2023-01-01T00:00:00Z"
}
```

## Data Models

### Contract Status

- `pending`: Contract uploaded, waiting for processing
- `processing`: Contract is being analyzed
- `completed`: Processing finished successfully
- `failed`: Processing failed with error

### Confidence Scores

Scores range from 0-100, indicating extraction confidence:

- `90-100`: High confidence
- `70-89`: Good confidence
- `50-69`: Moderate confidence
- `0-49`: Low confidence

### Extracted Data Fields

#### Parties

- `name`: Company or individual name
- `role`: customer, vendor, third_party
- `email`: Contact email address
- `phone`: Contact phone number
- `legal_entity`: Legal entity type
- `registration_number`: Business registration number
- `address`: Physical address
- `contact_person`: Authorized signatory

#### Financial Details

- `total_contract_value`: Total contract value
- `currency`: Currency code (USD, EUR, etc.)
- `line_items`: Array of line items with descriptions, quantities, and prices
- `tax_amount`: Tax amount
- `additional_fees`: Additional fees or charges

#### Payment Terms

- `payment_terms`: Payment terms (Net 30, Net 60, etc.)
- `payment_schedule`: Payment frequency
- `due_dates`: Array of payment due dates
- `payment_methods`: Accepted payment methods
- `banking_details`: Banking information

#### Service Level Agreements

- `performance_metrics`: Performance benchmarks
- `penalty_clauses`: Penalty terms
- `support_terms`: Support and maintenance terms
- `response_time`: Response time requirements
- `resolution_time`: Issue resolution timeframes

## Error Handling

### Common Error Codes

- `400 Bad Request`: Invalid request data
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server processing error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, implement appropriate rate limiting based on usage patterns.

## Security Considerations

- File uploads are validated for PDF format and size
- Malicious content patterns are detected and rejected
- File headers are validated to ensure genuine PDF files
- Upload directory is secured and isolated

## Performance

- Supports concurrent processing of multiple contracts
- Asynchronous processing with status tracking
- Retry mechanisms for failed processing
- Optimized database queries with proper indexing

## Monitoring

- Comprehensive logging for debugging and monitoring
- Health check endpoint for system status
- Progress tracking for long-running operations
- Error reporting with detailed context
