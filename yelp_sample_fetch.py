#!/usr/bin/env python3
"""
Yelp Fusion API Authentication and Sample Fetch
Step 1: Test API authentication and retrieve sample restaurant data from Los Angeles
"""

import requests
import json
import sys
from typing import Dict, Any, Optional
import logging
from datetime import datetime


class YelpAPIClient:
    """Enterprise-grade client for Yelp Fusion API interactions"""
    
    BASE_URL = "https://api.yelp.com/v3"
    SEARCH_ENDPOINT = "/businesses/search"
    
    def __init__(self, api_key: str):
        """
        Initialize the Yelp API client with authentication
        
        Args:
            api_key: Yelp Fusion API key for Bearer token authentication
        """
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json"
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def search_restaurants(self, location: str, limit: int = 3) -> Dict[str, Any]:
        """
        Search for restaurants in a specific location
        
        Args:
            location: City or address to search in
            limit: Number of results to return (max 50)
            
        Returns:
            Dict containing API response or error information
        """
        endpoint = f"{self.BASE_URL}{self.SEARCH_ENDPOINT}"
        
        params = {
            "location": location,
            "categories": "restaurants",
            "limit": limit
        }
        
        self.logger.info(f"Initiating API request to {endpoint}")
        self.logger.info(f"Request parameters: {params}")
        
        try:
            response = self.session.get(endpoint, params=params)
            
            # Log response details
            self.logger.info(f"Response Status Code: {response.status_code}")
            self.logger.info(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "status_code": response.status_code,
                    "data": response.json()
                }
            else:
                return {
                    "success": False,
                    "status_code": response.status_code,
                    "error": response.text,
                    "headers": dict(response.headers)
                }
                
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {str(e)}")
            return {
                "success": False,
                "status_code": None,
                "error": str(e)
            }
    
    def analyze_response_structure(self, response_data: Dict[str, Any]) -> None:
        """
        Analyze and report on the structure of the API response
        
        Args:
            response_data: The API response data to analyze
        """
        if not response_data.get("success"):
            print("\n❌ API Request Failed")
            print(f"Status Code: {response_data.get('status_code', 'N/A')}")
            print(f"Error: {response_data.get('error', 'Unknown error')}")
            return
        
        data = response_data.get("data", {})
        
        print("\n✅ API Request Successful")
        print(f"Status Code: {response_data['status_code']}")
        print(f"\n📊 Response Structure Analysis:")
        print(f"- Total businesses returned: {len(data.get('businesses', []))}")
        print(f"- Total results available: {data.get('total', 'N/A')}")
        
        # Analyze fields in the first business result
        if data.get('businesses'):
            first_business = data['businesses'][0]
            print(f"\n🏢 Sample Business Fields:")
            for key in sorted(first_business.keys()):
                value_type = type(first_business[key]).__name__
                print(f"  - {key}: {value_type}")
        
        # Check for any unexpected or missing standard fields
        expected_fields = {
            'id', 'name', 'image_url', 'is_closed', 'url', 'review_count',
            'categories', 'rating', 'coordinates', 'transactions', 'price',
            'location', 'phone', 'display_phone', 'distance'
        }
        
        if data.get('businesses'):
            actual_fields = set(first_business.keys())
            missing_fields = expected_fields - actual_fields
            extra_fields = actual_fields - expected_fields
            
            if missing_fields:
                print(f"\n⚠️  Missing expected fields: {', '.join(sorted(missing_fields))}")
            if extra_fields:
                print(f"\n🆕 Additional fields found: {', '.join(sorted(extra_fields))}")


def main():
    """Main execution function"""
    
    # API Key - Replace with actual key
    API_KEY = "amadLnlvUF1klTs23lb3VdeI9PQtZ7Sn2M8GxSj8FCaBs7zByMyqq69BNQ9mFM6J9Z93pEpxgcqJUqZzUiPEwGiyAg5yv3Eqk-L3jCzSCofT1NQ7XocLjbH6H9hraHYx"
    
    if API_KEY == "YOUR_YELP_API_KEY_HERE":
        print("❌ Error: Please replace YOUR_YELP_API_KEY_HERE with your actual Yelp Fusion API key")
        sys.exit(1)
    
    print("🚀 Yelp Fusion API - Sample Restaurant Fetch")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print(f"Target Location: Los Angeles")
    print(f"Category: restaurants")
    print(f"Result Limit: 3")
    print("=" * 60)
    
    # Initialize client and make request
    client = YelpAPIClient(API_KEY)
    response = client.search_restaurants("Los Angeles", limit=3)
    
    # Analyze response structure
    client.analyze_response_structure(response)
    
    # Print raw JSON response
    print("\n📄 Raw JSON Response:")
    print("=" * 60)
    if response.get("success"):
        print(json.dumps(response["data"], indent=2, ensure_ascii=False))
    else:
        print(json.dumps(response, indent=2, ensure_ascii=False))
    
    print("\n✅ Script execution completed")


if __name__ == "__main__":
    main()