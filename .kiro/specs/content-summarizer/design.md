# Design Document

## Overview

The Content Summarizer is a Python application that provides text summarization capabilities using Amazon Bedrock's foundation models. The application follows a modular architecture with clear separation between input handling, AWS service interaction, and output formatting. It uses boto3 as the AWS SDK for Python to communicate with Amazon Bedrock's runtime API.

The system is designed to be simple, testable, and production-ready with proper error handling, configuration management, and comprehensive test coverage.

## Architecture

The application follows a layered architecture:

1. **Input Layer**: Handles content validation and preprocessing
2. **Service Layer**: Manages Amazon Bedrock API interactions
3. **Configuration Layer**: Manages AWS credentials and application settings
4. **Output Layer**: Formats and returns summarization results

```
User Input → Input Validator → Bedrock Service → Response Formatter → Summary Output
                ↓                      ↓
         Configuration Manager    Error Handler
```

## Components and Interfaces

### 1. ContentValidator

**Purpose**: Validates and preprocesses input content

**Interface**:
```python
class ContentValidator:
    def validate(self, content: str) -> bool
    def preprocess(self, content: str) -> str
```

**Responsibilities**:
- Check for empty or whitespace-only content
- Validate content length constraints
- Handle special characters and encoding

### 2. BedrockSummarizer

**Purpose**: Core service that interacts with Amazon Bedrock

**Interface**:
```python
class BedrockSummarizer:
    def __init__(self, config: Config)
    def summarize(self, content: str) -> SummaryResult
    def _build_request(self, content: str) -> dict
    def _parse_response(self, response: dict) -> str
```

**Responsibilities**:
- Initialize boto3 Bedrock runtime client
- Construct API requests with proper parameters
- Invoke foundation models
- Parse and extract summary from responses
- Handle API errors and retries

### 3. Config

**Purpose**: Manages application configuration

**Interface**:
```python
class Config:
    aws_region: str
    model_id: str
    max_tokens: int
    temperature: float
    
    @classmethod
    def from_env(cls) -> Config
    @classmethod
    def from_file(cls, path: str) -> Config
```

**Responsibilities**:
- Load configuration from environment variables
- Load configuration from files (.env)
- Provide default values
- Validate configuration parameters

### 4. SummaryResult

**Purpose**: Data structure for summarization results

**Interface**:
```python
@dataclass
class SummaryResult:
    summary: str
    original_length: int
    summary_length: int
    model_used: str
    timestamp: datetime
```

## Data Models

### Input Content
- Type: String
- Constraints: Non-empty, max 100,000 characters
- Encoding: UTF-8

### Configuration
```python
{
    "aws_region": "us-east-1",
    "model_id": "anthropic.claude-3-haiku-20240307-v1:0",
    "max_tokens": 1024,
    "temperature": 0.5
}
```

### Bedrock Request Format
```python
{
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1024,
    "messages": [
        {
            "role": "user",
            "content": "Summarize the following text: {content}"
        }
    ],
    "temperature": 0.5
}
```

### Bedrock Response Format
```python
{
    "content": [
        {
            "type": "text",
            "text": "Summary text here..."
        }
    ],
    "usage": {
        "input_tokens": 150,
        "output_tokens": 75
    }
}
```


## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property Reflection

After analyzing all acceptance criteria, I've identified the following redundancies:
- Properties 2.3 and 6.2 both test that AWS region configuration is respected - these will be combined
- Properties 3.3 and 6.4 both test that model parameters from config are included in requests - these will be combined
- Several properties test configuration loading which can be consolidated into comprehensive configuration properties

### Properties

**Property 1: Non-empty content validation**
*For any* non-empty string, the validator should accept it as valid input
**Validates: Requirements 1.1**

**Property 2: Whitespace-only content rejection**
*For any* string composed entirely of whitespace characters (spaces, tabs, newlines), the validator should reject it as invalid input
**Validates: Requirements 1.4**

**Property 3: Large content preservation**
*For any* string with length greater than 10,000 characters, the content should be processed without truncation and the full content should be preserved
**Validates: Requirements 1.2**

**Property 4: Input source equivalence**
*For any* content string, reading it from a file and passing it directly as a string should produce equivalent results
**Validates: Requirements 1.5**

**Property 5: Configuration region application**
*For any* valid AWS region string in configuration, the Bedrock client should be initialized with that region
**Validates: Requirements 2.3, 6.2**

**Property 6: Request parameter inclusion**
*For any* configuration with model parameters (max_tokens, temperature), the built request should include those exact parameter values
**Validates: Requirements 3.3, 6.4**

**Property 7: Response parsing correctness**
*For any* valid Bedrock API response structure, the parser should correctly extract the summary text from the response content
**Validates: Requirements 3.4**

**Property 8: Result type consistency**
*For any* successful summarization operation, the result should contain a summary field of type string
**Validates: Requirements 4.1**

**Property 9: Metadata completeness**
*For any* summarization result, it should include all required metadata fields: original_length, summary_length, model_used, and timestamp
**Validates: Requirements 4.3**

**Property 10: Result structure consistency**
*For any* summarization result, the structure should match the SummaryResult dataclass format with proper field types
**Validates: Requirements 4.4**

**Property 11: API error handling**
*For any* Bedrock API exception type, the error handler should catch it and return a user-friendly error message without exposing internal details
**Validates: Requirements 5.1**

**Property 12: Invalid parameter rejection**
*For any* invalid model parameter values (negative max_tokens, temperature outside 0-1 range), validation should reject them before making API calls
**Validates: Requirements 5.4**

**Property 13: Configuration loading correctness**
*For any* valid configuration data (as dict or env vars), the Config class should load all fields correctly with proper type conversion
**Validates: Requirements 6.1**

**Property 14: Model ID application**
*For any* valid model ID specified in configuration, that exact model ID should be used in the Bedrock API request
**Validates: Requirements 6.3**

**Property 15: Default configuration fallback**
*For any* missing configuration field, the Config class should provide a sensible default value
**Validates: Requirements 6.5**

## Error Handling

### Error Categories

1. **Input Validation Errors**
   - Empty or whitespace-only content
   - Content exceeding maximum length
   - Invalid encoding
   - Custom exception: `InvalidContentError`

2. **Configuration Errors**
   - Missing required configuration
   - Invalid parameter values
   - Custom exception: `ConfigurationError`

3. **AWS Authentication Errors**
   - Missing credentials
   - Invalid credentials
   - Insufficient permissions
   - Wrapped from boto3 exceptions

4. **Bedrock API Errors**
   - Rate limiting (ThrottlingException)
   - Model not available (ModelNotReadyException)
   - Invalid request (ValidationException)
   - Service errors (ServiceException)
   - Network errors (ConnectionError)

5. **Response Processing Errors**
   - Malformed response
   - Missing expected fields
   - Custom exception: `ResponseParseError`

### Error Handling Strategy

- All errors should be caught at the appropriate layer
- User-facing error messages should be clear and actionable
- Internal error details should be logged for debugging
- Errors should include context (what operation failed, with what input)
- Network errors should be retryable with exponential backoff
- Authentication errors should fail fast with clear messages

## Testing Strategy

### Unit Testing

The application will use **pytest** as the testing framework with the following structure:

**Test Coverage Areas**:
- Input validation logic (ContentValidator)
- Configuration loading and defaults (Config)
- Request building logic (BedrockSummarizer._build_request)
- Response parsing logic (BedrockSummarizer._parse_response)
- Error handling for each error category
- Edge cases: empty strings, very long strings, special characters

**Mocking Strategy**:
- Mock boto3 Bedrock client for unit tests
- Mock file I/O operations
- Mock environment variables for config tests

### Property-Based Testing

The application will use **Hypothesis** as the property-based testing library for Python.

**Configuration**:
- Each property test should run a minimum of 100 iterations
- Use Hypothesis strategies to generate diverse test inputs
- Configure appropriate example generation for edge cases

**Property Test Requirements**:
- Each property-based test MUST be tagged with a comment referencing the correctness property
- Tag format: `# Feature: content-summarizer, Property {number}: {property_text}`
- Each correctness property MUST be implemented by a SINGLE property-based test
- Tests should use smart generators that constrain to valid input spaces

**Property Test Coverage**:
- Content validation properties (Properties 1, 2, 3)
- Configuration properties (Properties 5, 6, 13, 14, 15)
- Response parsing properties (Property 7)
- Result structure properties (Properties 8, 9, 10)
- Error handling properties (Properties 11, 12)
- Input source equivalence (Property 4)

**Hypothesis Strategies**:
- `st.text()` for general string generation
- `st.text(alphabet=st.characters(whitespace=True), min_size=1)` for whitespace strings
- `st.text(min_size=10001)` for large content
- `st.integers()`, `st.floats()` for parameter values
- Custom strategies for AWS regions, model IDs
- Custom strategies for Bedrock response structures

### Integration Testing

**Scope**:
- End-to-end tests with actual AWS Bedrock API (optional, requires credentials)
- File I/O integration tests
- Environment variable integration tests

**Approach**:
- Use pytest markers to separate integration tests from unit tests
- Integration tests should be skippable if AWS credentials are not available
- Use small, fast test cases for integration tests

### Test Organization

```
tests/
├── unit/
│   ├── test_validator.py
│   ├── test_config.py
│   ├── test_summarizer.py
│   └── test_error_handling.py
├── property/
│   ├── test_validation_properties.py
│   ├── test_config_properties.py
│   ├── test_response_properties.py
│   └── test_error_properties.py
└── integration/
    ├── test_bedrock_integration.py
    └── test_file_integration.py
```

## Implementation Notes

### AWS Bedrock Setup

- Use boto3 version 1.28.0 or higher for Bedrock support
- Bedrock runtime client: `boto3.client('bedrock-runtime')`
- Recommended model: `anthropic.claude-3-haiku-20240307-v1:0` (fast and cost-effective)
- Alternative models: Claude 3 Sonnet, Claude 3.5 Sonnet for higher quality

### Dependencies

```
boto3>=1.28.0
python-dotenv>=1.0.0
hypothesis>=6.90.0
pytest>=7.4.0
```

### Environment Variables

```
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
BEDROCK_MODEL_ID=anthropic.claude-3-haiku-20240307-v1:0
MAX_TOKENS=1024
TEMPERATURE=0.5
```

### Performance Considerations

- Bedrock API calls are synchronous and may take 2-5 seconds
- Consider implementing async support for batch processing
- Implement request timeout (30 seconds recommended)
- Cache configuration to avoid repeated file/env reads
- Consider implementing retry logic with exponential backoff for transient errors
