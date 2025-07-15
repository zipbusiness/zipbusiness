# ZIP-First City Batch Ingestion System Architecture

## Overview

This document defines the complete file architecture for ZipPicks' ZIP-first City Batch Ingestion System. This system collects and stores restaurant data from Yelp based on ZIP codes, supporting both single and batch ingestion workflows.

### Core Principles
- **ZIP-first architecture** - All ingestion is triggered by ZIP codes, not cities
- **No hardcoded values** - All configuration externalized
- **Type safety** - Pydantic DTOs for data contracts
- **Scalable** - Supports quotas, rate limiting, and resumability
- **Observable** - Comprehensive metrics and logging

## File Architecture

### Core Ingestion Services

#### 1. `app/services/yelp_city_ingestor.py`
**Purpose**: ZIP-first batch ingestion engine for processing restaurants by ZIP code  
**Key Classes/Functions**:
- `YelpCityIngestor`: Main orchestration class
  - `ingest_zip_code()`: Process single ZIP with rate limiting
  - `ingest_city_batch()`: Process all ZIPs for a city
  - `validate_ingestion_config()`: Ensure config integrity
  - `track_ingestion_progress()`: Monitor API usage and results
**Integration**: 
- Consumes `YelpService` for API calls
- Delegates to `RestaurantService` for storage
- Uses `ZPIDGenerator` for ID generation
- Reports to `BatchProcessor` for quota tracking

#### 2. `app/services/yelp_service.py`
**Purpose**: Yelp API integration and data transformation  
**Key Classes/Functions**:
- `YelpService`: API client wrapper
  - `search_restaurants_by_zip()`: Core search method
  - `format_restaurant_data()`: Transform Yelp response to DTO
  - `validate_api_response()`: Ensure data quality
  - `handle_rate_limits()`: Manage API throttling
**Integration**:
- Called by `YelpCityIngestor` for data retrieval
- Returns `RestaurantIngestionData` DTOs
- Uses `YelpAPIClient` for low-level API calls

#### 3. `app/services/restaurant_service.py`
**Purpose**: Central restaurant data persistence handler  
**Key Classes/Functions**:
- `RestaurantService`: Storage orchestrator
  - `store_restaurant()`: Single restaurant persistence
  - `store_restaurant_batch()`: Bulk storage operations
  - `update_or_create()`: Idempotent storage logic
  - `validate_zpid_uniqueness()`: Ensure ID integrity
**Integration**:
- Receives `RestaurantIngestionData` from ingestion services
- Uses `RestaurantRepository` for database operations
- Integrates with `DataQualityService` for validation

#### 4. `app/services/zpid_generator.py`
**Purpose**: Deterministic restaurant ID generation using full address  
**Key Classes/Functions**:
- `ZPIDGenerator`: ID generation engine
  - `generate_zpid()`: Create ID from address components
  - `normalize_address()`: Standardize address format
  - `validate_address_components()`: Ensure completeness
**Integration**:
- Used by all ingestion services before storage
- Ensures consistent IDs across data sources

### Data Models and DTOs

#### 5. `app/schemas/restaurant_ingestion.py`
**Purpose**: Pydantic DTOs defining data contracts for ingestion pipeline  
**Key Classes**:
- `RestaurantIngestionData`: Core DTO for restaurant data flow
  - All fields from external sources (Yelp, Google, etc.)
  - Validation rules and transformations
  - Optional fields with defaults
- `IngestionConfig`: Batch processing configuration
  - ZIP codes to process
  - API quotas and rate limits
  - Processing options
- `IngestionResult`: Operation outcome tracking
  - Success/failure counts
  - API usage metrics
  - Error details
**Integration**:
- Used by all services for type safety
- Validates data at service boundaries
- Ensures consistent data flow

#### 6. `app/models/restaurant.py`
**Purpose**: SQLAlchemy ORM model for restaurant persistence  
**Key Fields**:
- `zpid`: Primary key from ZPIDGenerator
- `yelp_id`, `google_place_id`: External identifiers
- `yelp_categories`, `yelp_attributes`: JSON fields for Yelp data
- `elite_category`: Restaurant classification
- `data_quality_score`: Ingestion quality metrics
**Integration**:
- Mapped from `RestaurantIngestionData` DTOs
- Accessed via `RestaurantRepository`
- Includes relationships to `DataSource`, `ZipMetadata`

#### 7. `app/repositories/restaurant_repository.py`
**Purpose**: Data access layer for restaurant operations  
**Key Methods**:
- `create_or_update()`: Idempotent storage
- `find_by_zpid()`: Primary lookup
- `find_by_external_id()`: Lookup by Yelp/Google IDs
- `bulk_upsert()`: Efficient batch operations
**Integration**:
- Used exclusively by `RestaurantService`
- Handles database transactions
- Implements query optimization

### Batch Processing and Orchestration

#### 8. `app/services/batch_processor.py`
**Purpose**: High-level batch job orchestration with quota management  
**Key Classes/Functions**:
- `YelpBatchProcessor`: Main orchestrator
  - `process_daily_batch()`: Execute daily ingestion quota
  - `manage_city_priority()`: Tier-based city scheduling
  - `track_quota_usage()`: Monitor API consumption
  - `persist_progress()`: Save state for resumability
**Integration**:
- Calls `YelpCityIngestor` for ZIP processing
- Updates `BackgroundJobLog` for tracking
- Reads/writes `batch_schedule.json` for state

#### 9. `app/services/ingestion_scheduler.py`
**Purpose**: Schedule management for batch ingestion jobs  
**Key Classes/Functions**:
- `IngestionScheduler`: Schedule orchestration
  - `get_next_batch()`: Determine ZIPs to process
  - `update_schedule()`: Mark completed work
  - `rebalance_priorities()`: Adjust based on results
  - `estimate_completion()`: Project timeline
**Integration**:
- Used by `BatchProcessor` for work allocation
- Reads city tier configuration
- Maintains processing history

#### 10. `app/models/background_job_log.py`
**Purpose**: Track batch job execution history  
**Key Fields**:
- `job_type`: Ingestion job identifier
- `status`: Success/failure/partial
- `metadata`: JSON with metrics (API calls, restaurants found)
- `error_details`: Failure information
**Integration**:
- Written by `BatchProcessor` after each run
- Used for monitoring and debugging
- Enables job resumption

#### 11. `scripts/batch_ingestion_runner.py`
**Purpose**: CLI script for manual batch execution  
**Key Functions**:
- `run_city_batch()`: Process specific city
- `run_zip_batch()`: Process specific ZIPs
- `validate_prerequisites()`: Check system readiness
- `report_results()`: Display outcomes
**Integration**:
- Invokes service layer components
- Bypasses API layer for direct execution
- Used for testing and manual runs

### Configuration and Utilities

#### 12. `app/configurations/city_config.json`
**Purpose**: City tier definitions with ZIP code mappings  
**Structure**:
```json
{
  "tier_1_cities": {
    "new_york": {
      "name": "New York",
      "state": "NY",
      "zip_codes": ["10001", "10002", ...]
    }
  }
}
```
**Integration**:
- Read by `IngestionScheduler` for prioritization
- Defines batch processing order
- No hardcoded values in code

#### 13. `app/configurations/ingestion_quotas.json`
**Purpose**: API quota and rate limit configuration  
**Structure**:
```json
{
  "daily_limits": {
    "yelp_api_calls": 5000,
    "max_restaurants": 2500
  },
  "rate_limits": {
    "calls_per_second": 5,
    "burst_size": 10
  }
}
```
**Integration**:
- Enforced by `BatchProcessor`
- Monitored by `YelpService`
- Updated based on vendor changes

#### 14. `app/utils/address_normalizer.py`
**Purpose**: Address standardization utilities  
**Key Functions**:
- `normalize_street_address()`: Standardize format
- `validate_zip_code()`: Ensure valid ZIP
- `extract_address_components()`: Parse full addresses
**Integration**:
- Used by `ZPIDGenerator`
- Ensures consistent ID generation

#### 15. `app/utils/data_quality_validator.py`
**Purpose**: Validate ingested restaurant data  
**Key Functions**:
- `validate_restaurant_data()`: Check completeness
- `calculate_quality_score()`: Rate data quality
- `identify_missing_fields()`: Find gaps
**Integration**:
- Called by `RestaurantService` before storage
- Updates quality metrics on restaurant records

#### 16. `app/services/yelp_api_client.py`
**Purpose**: Low-level Yelp API HTTP client  
**Key Methods**:
- `search_businesses()`: Raw API search
- `get_business_details()`: Fetch specific restaurant
- `handle_auth()`: Manage API credentials
**Integration**:
- Wrapped by `YelpService`
- Handles HTTP specifics
- Implements retry logic

### API Endpoints and Integration

#### 17. `app/api/endpoints/etl.py`
**Purpose**: API endpoints for batch ingestion operations  
**Key Endpoints**:
- `POST /run-etl`: Trigger daily batch processing
- `GET /etl/status`: Check current job status
- `POST /etl/zip/{zip_code}`: Manual single ZIP ingestion
- `GET /etl/metrics`: Retrieve ingestion statistics
**Integration**:
- Protected by secret header authentication
- Invokes `BatchProcessor` as background task
- Returns job IDs for tracking

#### 18. `app/api/dependencies/auth.py`
**Purpose**: Authentication for ETL endpoints  
**Key Functions**:
- `verify_etl_secret()`: Validate secret header
- `check_ingestion_permissions()`: Role-based access
**Integration**:
- Applied to all ETL endpoints
- Reads secrets from environment

#### 19. `app/tasks/background_tasks.py`
**Purpose**: Async task definitions for batch processing  
**Key Tasks**:
- `process_batch_ingestion()`: Background batch execution
- `process_single_zip()`: Async ZIP processing
- `generate_ingestion_report()`: Create summary reports
**Integration**:
- Launched by API endpoints
- Updates `BackgroundJobLog`
- Sends completion notifications

#### 20. `app/monitoring/ingestion_metrics.py`
**Purpose**: Track and report ingestion performance  
**Key Classes**:
- `IngestionMetrics`: Metrics aggregator
  - `track_api_call()`: Record API usage
  - `track_restaurant_stored()`: Count successes
  - `generate_daily_report()`: Summarize activity
**Integration**:
- Called throughout ingestion pipeline
- Stores metrics for reporting
- Enables performance optimization

### Supporting Files

#### 21. `app/exceptions/ingestion_exceptions.py`
**Purpose**: Custom exceptions for ingestion pipeline  
**Key Exceptions**:
- `QuotaExceededException`: Daily limit reached
- `InvalidZipCodeException`: Bad ZIP provided
- `DuplicateRestaurantException`: ZPID conflict
**Integration**:
- Raised by services
- Caught by orchestration layer
- Logged with context

#### 22. `tests/services/test_yelp_city_ingestor.py`
**Purpose**: Unit tests for ingestion engine  
**Key Tests**:
- ZIP code processing logic
- Rate limit handling
- Error recovery scenarios
**Integration**:
- Uses pytest fixtures
- Mocks external dependencies
- Validates business logic

#### 23. `tests/integration/test_batch_pipeline.py`
**Purpose**: End-to-end ingestion tests  
**Key Tests**:
- Full ZIP ingestion flow
- Quota management
- Data quality validation
**Integration**:
- Tests entire pipeline
- Uses test database
- Validates data persistence

## Data Flow

1. **Trigger**: ETL endpoint or scheduled job initiates batch
2. **Scheduling**: `IngestionScheduler` determines ZIPs to process
3. **Orchestration**: `BatchProcessor` manages quotas and progress
4. **ZIP Processing**: `YelpCityIngestor` processes each ZIP
5. **API Calls**: `YelpService` retrieves restaurant data
6. **ID Generation**: `ZPIDGenerator` creates deterministic IDs
7. **Validation**: `DataQualityValidator` ensures data integrity
8. **Storage**: `RestaurantService` persists via repository
9. **Metrics**: `IngestionMetrics` tracks performance
10. **Logging**: `BackgroundJobLog` records execution

## Key Design Decisions

1. **ZIP-first approach**: More granular than city-level, enables better progress tracking
2. **Deterministic IDs**: ZPID based on full address ensures consistency
3. **DTO pattern**: Type safety and validation at service boundaries
4. **Repository pattern**: Clean separation of data access
5. **Configuration externalization**: No hardcoded values
6. **Quota management**: Respect API limits, enable resumability
7. **Background processing**: Non-blocking API operations
8. **Comprehensive testing**: Unit and integration test coverage

This architecture provides a scalable, maintainable, and observable system for restaurant data ingestion that can grow with ZipPicks' needs.