# Contract Intelligence Parser - Setup Guide

## Overview

This is a complete contract intelligence system that automatically processes PDF contracts, extracts critical financial and operational data, and provides confidence scores with gap analysis.

## Architecture

- **Backend**: Python FastAPI with MongoDB
- **Frontend**: React/Next.js web application
- **Database**: MongoDB
- **Deployment**: Docker containers
- **Processing**: Asynchronous contract parsing with status tracking

## Prerequisites

- Docker and Docker Compose
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd TechAssignment-main
```

### 2. Start the Application

```bash
docker-compose up --build
```

This will start:
- MongoDB on port 27017
- Backend API on port 8000
- Frontend on port 3000

### 3. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## Manual Setup (Development)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MongoDB**:
   - Install MongoDB locally or use Docker:
     ```bash
     docker run -d -p 27017:27017 --name mongodb mongo:7.0
     ```

5. **Set environment variables**:
   ```bash
   export MONGODB_URL=mongodb://localhost:27017
   export DEBUG=True
   ```

6. **Run the backend**:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set environment variables**:
   ```bash
   export NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
   ```

4. **Run the frontend**:
   ```bash
   npm run dev
   ```

## API Endpoints

### Contract Upload
- **POST** `/contracts/upload`
- Upload PDF contract files
- Returns contract ID for tracking

### Processing Status
- **GET** `/contracts/{contract_id}/status`
- Check parsing progress
- Returns status: `pending`, `processing`, `completed`, `failed`

### Contract Data
- **GET** `/contracts/{contract_id}`
- Get parsed contract data in JSON format
- Available only when processing is complete

### Contract List
- **GET** `/contracts`
- Get paginated list of all contracts
- Supports filtering by status, sorting, and pagination

### Contract Download
- **GET** `/contracts/{contract_id}/download`
- Download original contract file

### Health Check
- **GET** `/health`
- Check API health status

## Data Extraction

The system extracts the following information from contracts:

### 1. Party Identification
- Contract parties (customer, vendor, third parties)
- Legal entity names and registration details
- Authorized signatories and roles
- Contact information

### 2. Account Information
- Customer billing details
- Account numbers and references
- Contact information for billing/technical support

### 3. Financial Details
- Line items with descriptions, quantities, and unit prices
- Total contract value and currency
- Tax information and additional fees

### 4. Payment Structure
- Payment terms (Net 30, Net 60, etc.)
- Payment schedules and due dates
- Payment methods and banking details

### 5. Revenue Classification
- Identify recurring vs. one-time payments
- Subscription models and billing cycles
- Renewal terms and auto-renewal clauses

### 6. Service Level Agreements
- Performance metrics and benchmarks
- Penalty clauses and remedies
- Support and maintenance terms

## Scoring System

The system uses a weighted scoring algorithm (0-100 points):

- **Financial completeness**: 30 points
- **Party identification**: 25 points
- **Payment terms clarity**: 20 points
- **SLA definition**: 15 points
- **Contact information**: 10 points

### Gap Analysis

The system identifies missing critical fields and provides recommendations for improvement.

## Testing

### Run Backend Tests

```bash
cd backend
pytest
```

### Run Tests with Coverage

```bash
cd backend
pytest --cov=app --cov-report=html
```

Coverage report will be generated in `htmlcov/index.html`

## Configuration

### Environment Variables

#### Backend
- `MONGODB_URL`: MongoDB connection string (default: mongodb://localhost:27017)
- `DEBUG`: Enable debug mode (default: True)
- `LOG_LEVEL`: Logging level (default: INFO)
- `MAX_FILE_SIZE`: Maximum file size in bytes (default: 52428800 - 50MB)
- `UPLOAD_DIR`: Directory for uploaded files (default: uploads)

#### Frontend
- `NEXT_PUBLIC_API_BASE_URL`: Backend API URL (default: http://localhost:8000)

## File Structure

```
TechAssignment-main/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Pydantic models
│   │   ├── parser.py            # Contract parsing logic
│   │   ├── scoring.py           # Scoring algorithm
│   │   ├── database.py          # Database configuration
│   │   └── config.py            # Configuration settings
│   ├── tests/
│   │   ├── test_main.py         # API endpoint tests
│   │   ├── test_parser.py       # Parser tests
│   │   └── test_scoring.py      # Scoring tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── pytest.ini
├── frontend/
│   ├── app/
│   │   ├── components/
│   │   │   ├── ContractUpload.tsx
│   │   │   ├── ContractList.tsx
│   │   │   └── ContractDetail.tsx
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── package.json
│   ├── Dockerfile
│   └── next.config.js
├── docker-compose.yml
├── README.md
└── SETUP.md
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**:
   - Ensure MongoDB is running
   - Check connection string in environment variables

2. **File Upload Issues**:
   - Check file size (max 50MB)
   - Ensure file is PDF format
   - Check uploads directory permissions

3. **Frontend Not Loading**:
   - Verify backend is running on port 8000
   - Check NEXT_PUBLIC_API_BASE_URL environment variable

4. **Processing Stuck**:
   - Check backend logs for errors
   - Verify MongoDB is accessible
   - Restart the backend service

### Logs

View logs for each service:

```bash
# All services
docker-compose logs

# Specific service
docker-compose logs backend
docker-compose logs frontend
docker-compose logs mongodb
```

## Performance Considerations

- **File Size**: Maximum 50MB per contract
- **Concurrent Processing**: Supports multiple contracts processing simultaneously
- **Database**: MongoDB with proper indexing for fast queries
- **Caching**: Consider adding Redis for production use

## Security Considerations

- File upload validation
- Secure file storage
- Input sanitization
- Rate limiting (recommended for production)
- Authentication/authorization (not implemented in this version)

## Production Deployment

For production deployment:

1. **Use environment-specific configurations**
2. **Set up proper logging and monitoring**
3. **Implement authentication and authorization**
4. **Use HTTPS**
5. **Set up backup strategies for MongoDB**
6. **Configure proper resource limits in Docker**
7. **Use a reverse proxy (nginx)**
8. **Implement rate limiting**

## Support

For issues or questions:
1. Check the logs for error messages
2. Verify all services are running
3. Check environment variables
4. Review the API documentation at http://localhost:8000/docs
