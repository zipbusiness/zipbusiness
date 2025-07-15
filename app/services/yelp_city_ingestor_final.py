# ZIP-first City Batch Ingestion System - Production Ready
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

class YelpService:
    """Stub service class that safely logs restaurant storage without assuming schema or DB structure."""
    
    def __init__(self, logger: Optional[logging.Logger] = None):
        self.logger = logger or logging.getLogger(__name__)
        self.stored_count = 0
    
    def search_businesses(self, **params) -> Dict[str, Any]:
        """Stub method for Yelp API search - would be replaced with actual API implementation."""
        self.logger.info(f"[SEARCH] Searching with params: {params}")
        # This would be replaced with actual Yelp API call
        # For now, return empty response to avoid assumptions
        return {'businesses': [], 'total': 0}
    
    def store_restaurant(self, restaurant_data: Dict[str, Any]) -> None:
        """Stub method to safely log restaurant storage without assuming schema or DB structure."""
        self.stored_count += 1
        self.logger.info(
            f"[STORE] Would store restaurant #{self.stored_count}: "
            f"{restaurant_data.get('name', '[unknown]')} at ZIP {restaurant_data.get('zip_code')} "
            f"(Yelp ID: {restaurant_data.get('yelp_id', 'N/A')})"
        )

class YelpCityIngestor:
    """Enterprise-grade ZIP-first Yelp restaurant ingestion engine."""
    
    def __init__(self, zip_codes: List[str], ingestion_settings: Dict[str, Any], logger: Optional[logging.Logger] = None):
        """Initialize the ingestor with ZIP codes and settings.
        
        Args:
            zip_codes: List of ZIP codes to ingest (core identifiers)
            ingestion_settings: Configuration dict with:
                - max_api_calls: Maximum API calls allowed (default: 5000)
                - restaurants_per_zip: Target restaurants per ZIP (default: 50)
                - radius_meters: Search radius in meters (default: 5000)
                - batch_size: Number of businesses per API call (default: 50)
            logger: Optional logger instance
        """
        self.zip_codes = zip_codes
        self.ingestion_settings = ingestion_settings
        self.logger = logger or logging.getLogger(__name__)
        
        # Initialize results structure
        self.results = {
            'successful_zips': [],
            'failed_zips': [],
            'total_restaurants': 0,
            'errors': [],
            'ingestion_start': datetime.utcnow().isoformat(),
            'ingestion_end': None,
            'api_calls_made': 0
        }
        
        # Runtime tracking
        self.api_calls_count = 0
        
        # Configuration with defaults
        self.max_api_calls = ingestion_settings.get('max_api_calls', 5000)
        self.restaurants_per_zip = ingestion_settings.get('restaurants_per_zip', 50)
        self.radius_meters = ingestion_settings.get('radius_meters', 5000)
        self.batch_size = min(50, ingestion_settings.get('batch_size', 50))  # Yelp max is 50

    def run(self, yelp_service: YelpService) -> Dict[str, Any]:
        """Execute the ZIP-first ingestion process.
        
        Args:
            yelp_service: Service instance for Yelp API and storage operations
            
        Returns:
            Dict with ingestion results including successful_zips, failed_zips, total_restaurants, errors
        """
        self.logger.info(f"Starting ZIP-first ingestion for {len(self.zip_codes)} ZIP codes")
        self.logger.info(f"Settings: max_api_calls={self.max_api_calls}, restaurants_per_zip={self.restaurants_per_zip}, radius={self.radius_meters}m")

        for zip_index, zip_code in enumerate(self.zip_codes, 1):
            if self.api_calls_count >= self.max_api_calls:
                self.logger.warning(f"API call limit ({self.max_api_calls}) reached at ZIP {zip_index}/{len(self.zip_codes)}")
                remaining_zips = self.zip_codes[zip_index-1:]
                for remaining_zip in remaining_zips:
                    self.results['failed_zips'].append(remaining_zip)
                    self.results['errors'].append({
                        'zip_code': remaining_zip,
                        'error': 'API call limit reached',
                        'type': 'limit_exceeded',
                        'timestamp': datetime.utcnow().isoformat()
                    })
                break

            self.logger.info(f"Processing ZIP {zip_code} ({zip_index}/{len(self.zip_codes)})")
            
            try:
                zip_results = self._ingest_zip(zip_code, yelp_service)
                
                if zip_results['restaurant_count'] > 0:
                    self.results['successful_zips'].append({
                        'zip_code': zip_code,
                        'restaurant_count': zip_results['restaurant_count'],
                        'api_calls': zip_results['api_calls'],
                        'stored_count': zip_results['stored_count']
                    })
                    self.results['total_restaurants'] += zip_results['restaurant_count']
                else:
                    self.results['failed_zips'].append(zip_code)
                    if not any(e['zip_code'] == zip_code for e in self.results['errors']):
                        self.results['errors'].append({
                            'zip_code': zip_code,
                            'error': 'No restaurants found in ZIP code area',
                            'type': 'no_data',
                            'timestamp': datetime.utcnow().isoformat()
                        })

            except Exception as zip_error:
                self.logger.error(f"Critical failure for ZIP {zip_code}: {str(zip_error)}")
                self.results['failed_zips'].append(zip_code)
                self.results['errors'].append({
                    'zip_code': zip_code,
                    'error': str(zip_error),
                    'type': 'processing_error',
                    'timestamp': datetime.utcnow().isoformat()
                })

        # Finalize results
        self.results['ingestion_end'] = datetime.utcnow().isoformat()
        self.results['api_calls_made'] = self.api_calls_count
        
        self.logger.info(
            f"Ingestion complete. "
            f"Success: {len(self.results['successful_zips'])} ZIPs, "
            f"Failed: {len(self.results['failed_zips'])} ZIPs, "
            f"Total restaurants: {self.results['total_restaurants']}, "
            f"API calls: {self.api_calls_count}/{self.max_api_calls}"
        )
        
        return self.results

    def _ingest_zip(self, zip_code: str, yelp_service: YelpService) -> Dict[str, Any]:
        """Ingest restaurants for a single ZIP code.
        
        Args:
            zip_code: The ZIP code to process
            yelp_service: Service instance for API and storage
            
        Returns:
            Dict with restaurant_count, api_calls, stored_count for this ZIP
        """
        offset = 0
        zip_restaurants = []
        zip_api_calls = 0
        stored_count = 0

        while len(zip_restaurants) < self.restaurants_per_zip and self.api_calls_count < self.max_api_calls:
            # Prepare search parameters
            search_params = {
                'location': zip_code,
                'categories': 'restaurants',
                'radius': self.radius_meters,
                'limit': min(self.batch_size, self.restaurants_per_zip - len(zip_restaurants)),
                'offset': offset
            }

            try:
                # Make API call
                response = yelp_service.search_businesses(**search_params)
                self.api_calls_count += 1
                zip_api_calls += 1

                # Check for businesses in response
                businesses = response.get('businesses', [])
                if not businesses:
                    self.logger.debug(f"No more businesses for ZIP {zip_code} at offset {offset}")
                    break

                # Process each business
                for business in businesses:
                    # Strict ZIP code matching - only include if business is actually in target ZIP
                    business_zip = business.get('location', {}).get('zip_code', '')
                    if business_zip == zip_code:
                        restaurant_data = self._extract_restaurant_data(business, zip_code)
                        zip_restaurants.append(restaurant_data)
                        
                        # Attempt to store the restaurant
                        try:
                            yelp_service.store_restaurant(restaurant_data)
                            stored_count += 1
                        except Exception as store_error:
                            self.logger.error(f"Storage failed for {restaurant_data.get('name')}: {str(store_error)}")
                            self.results['errors'].append({
                                'zip_code': zip_code,
                                'restaurant': restaurant_data.get('name'),
                                'yelp_id': restaurant_data.get('yelp_id'),
                                'error': str(store_error),
                                'type': 'storage_error',
                                'timestamp': datetime.utcnow().isoformat()
                            })

                # Update offset for pagination
                offset += len(businesses)

                # Check if we've retrieved all available results
                total_available = response.get('total', 0)
                if total_available <= offset:
                    self.logger.debug(f"Retrieved all {total_available} results for ZIP {zip_code}")
                    break

            except Exception as api_error:
                self.logger.error(f"API error for ZIP {zip_code}: {str(api_error)}")
                self.results['errors'].append({
                    'zip_code': zip_code,
                    'error': str(api_error),
                    'type': 'api_error',
                    'timestamp': datetime.utcnow().isoformat()
                })
                break

        self.logger.info(
            f"ZIP {zip_code} complete: {len(zip_restaurants)} restaurants found, "
            f"{stored_count} stored, {zip_api_calls} API calls"
        )

        return {
            'restaurant_count': len(zip_restaurants),
            'api_calls': zip_api_calls,
            'stored_count': stored_count
        }

    def _extract_restaurant_data(self, business: Dict[str, Any], zip_code: str) -> Dict[str, Any]:
        """Extract and structure restaurant data from Yelp business object.
        
        Args:
            business: Raw business data from Yelp API
            zip_code: The ZIP code being processed (for validation)
            
        Returns:
            Structured restaurant data dict
        """
        location = business.get('location', {})
        coordinates = business.get('coordinates', {})
        
        return {
            'yelp_id': business.get('id'),
            'name': business.get('name'),
            'address': location.get('address1'),
            'city': location.get('city'),
            'state': location.get('state'),
            'zip_code': zip_code,  # Use the target ZIP to ensure consistency
            'latitude': coordinates.get('latitude'),
            'longitude': coordinates.get('longitude'),
            'phone': business.get('phone'),
            'rating': business.get('rating'),
            'review_count': business.get('review_count'),
            'price': business.get('price'),
            'categories': [cat.get('alias') for cat in business.get('categories', []) if cat.get('alias')],
            'image_url': business.get('image_url'),
            'url': business.get('url'),
            'is_closed': business.get('is_closed', False),
            'transactions': business.get('transactions', []),
            'ingested_at': datetime.utcnow().isoformat()
        }


# Example usage (for testing/demonstration purposes only)
if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example ZIP codes and settings
    test_zips = ['10001', '10002', '10003']
    settings = {
        'max_api_calls': 100,
        'restaurants_per_zip': 25,
        'radius_meters': 3000
    }
    
    # Create service and ingestor
    yelp_service = YelpService()
    ingestor = YelpCityIngestor(test_zips, settings)
    
    # Run ingestion
    results = ingestor.run(yelp_service)
    
    # Display results
    print(f"\nIngestion Results:")
    print(f"- Successful ZIPs: {len(results['successful_zips'])}")
    print(f"- Failed ZIPs: {len(results['failed_zips'])}")
    print(f"- Total restaurants: {results['total_restaurants']}")
    print(f"- Errors: {len(results['errors'])}")
    print(f"- API calls made: {results['api_calls_made']}")