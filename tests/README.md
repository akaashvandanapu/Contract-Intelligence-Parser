# Test Suite Documentation

## 📋 **Test Structure Overview**

This test suite provides comprehensive coverage for the Contract Intelligence Parser system, organized by component and functionality. The system includes advanced RAG (Retrieval-Augmented Generation) parsing, Gemini AI integration, and intelligent scoring systems.

## 🧪 **Test Files**

### **Core Application Tests**

- **`test_main.py`** - Main FastAPI application tests
  - Contract upload functionality
  - Status checking
  - Data retrieval
  - File download
  - Health checks
  - Error handling

### **Parser Tests**

- **`test_rag_parser.py`** - RAG (Retrieval-Augmented Generation) parser tests

  - Text chunking
  - Section identification
  - Confidence scoring
  - Chunk combination
  - Performance metrics

- **`test_manual_parser.py`** - Manual parser fallback tests
  - Party extraction
  - Financial details parsing
  - Payment terms extraction
  - SLA parsing
  - Confidence calculation

### **AI Integration Tests**

- **`test_gemini_analyzer.py`** - Gemini AI analyzer tests
  - Prompt generation
  - Response parsing
  - Data validation
  - Error handling
  - Fallback mechanisms

### **Data Model Tests**

- **`test_models.py`** - Pydantic model tests
  - Party model validation
  - Financial details structure
  - Payment terms validation
  - SLA model testing
  - Contract data integrity

### **Scoring System Tests**

- **`test_scoring_engine.py`** - Scoring engine tests
  - Score calculation
  - Gap identification
  - Confidence scoring
  - Data completeness assessment

### **Performance Tests**

- **`test_rag_performance.py`** - RAG parser performance tests
  - Text extraction speed
  - Chunking efficiency
  - Section identification
  - Confidence scoring
  - Overall performance metrics

### **Integration Tests**

- **`test_integration.py`** - End-to-end integration tests
  - System health checks
  - Component integration
  - Error handling
  - Performance benchmarks
  - Data consistency

### **API Tests**

- **`test_backend_api.py`** - Backend API endpoint tests
  - Root endpoint
  - Health endpoint
  - Contract endpoints
  - Upload validation
  - Error responses

## 🚀 **Running Tests**

### **Run All Tests**

```bash
python tests/run_tests.py
```

### **Run Specific Test Categories**

```bash
python tests/run_tests.py "rag"
python tests/run_tests.py "api"
python tests/run_tests.py "integration"
```

### **Run Individual Test Files**

```bash
pytest tests/test_rag_parser.py -v
pytest tests/test_models.py -v
pytest tests/test_integration.py -v
```

### **Run with Coverage**

```bash
pytest tests/ --cov=app --cov-report=html
```

## 📊 **Test Coverage Areas**

### **Functional Coverage**

- ✅ API endpoint functionality
- ✅ File upload and validation
- ✅ Contract processing pipeline
- ✅ Data extraction accuracy
- ✅ Error handling and recovery
- ✅ Performance benchmarks

### **Component Coverage**

- ✅ FastAPI application
- ✅ RAG parser engine
- ✅ Manual parser fallback
- ✅ Gemini AI integration
- ✅ Scoring engine
- ✅ Data models
- ✅ Database operations

### **Integration Coverage**

- ✅ End-to-end workflows
- ✅ Component interactions
- ✅ Error propagation
- ✅ Data consistency
- ✅ Performance metrics

## 🔧 **Test Configuration**

### **Environment Setup**

- Tests use mock data and services
- No external API calls during testing
- Isolated test environments
- Comprehensive error simulation

### **Test Data**

- Sample contract texts
- Mock database responses
- Simulated API responses
- Performance benchmarks

### **Assertions**

- Response status codes
- Data structure validation
- Performance thresholds
- Error message verification
- Business logic validation

## 📈 **Performance Benchmarks**

### **Expected Performance**

- Text extraction: < 2 seconds
- Chunking: < 0.1 seconds
- Section identification: < 0.1 seconds
- Full parsing: < 5 seconds
- API responses: < 1 second

### **Quality Metrics**

- Confidence scores: 90-100%
- Extraction accuracy: 95%+
- Error rate: < 5%
- Success rate: 95%+

## 🛠️ **Maintenance**

### **Adding New Tests**

1. Create test file in `tests/` directory
2. Follow naming convention: `test_*.py`
3. Include comprehensive docstrings
4. Add to `run_tests.py` if needed
5. Update this README

### **Test Best Practices**

- Use descriptive test names
- Include setup and teardown
- Mock external dependencies
- Test both success and failure cases
- Include performance assertions
- Document test purpose

## 🎯 **Quality Assurance**

This test suite ensures:

- **Reliability**: All components work as expected
- **Performance**: Meets speed and accuracy requirements
- **Robustness**: Handles errors gracefully
- **Maintainability**: Easy to extend and modify
- **Documentation**: Clear test purposes and coverage
