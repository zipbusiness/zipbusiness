"""
Yelp Fusion API Sample Fetcher for Zip Intelligence API
Step 2: Fetch and analyze restaurant data structure from Pleasanton, CA
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

import httpx
from dotenv import load_dotenv

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))
from utils.json_utils import get_field_paths

# Load environment variables
load_dotenv()

# Configuration
YELP_API_BASE_URL = "https://api.yelp.com/v3"
YELP_API_KEY = os.getenv("YELP_API_KEY")
OUTPUT_FILE = "pleasanton_sample_response.json"

# Test search parameters
SEARCH_PARAMS = {
    "location": "Pleasanton, CA",
    "categories": "restaurants",
    "limit": 20
}


class YelpAPIError(Exception):
    """Custom exception for Yelp API errors."""
    pass


def fetch_yelp_businesses(api_key: str, params: dict) -> dict:
    """
    Fetch businesses from Yelp Fusion API.
    
    Args:
        api_key: Yelp API Bearer token
        params: Search parameters
        
    Returns:
        JSON response from Yelp API
        
    Raises:
        YelpAPIError: On API authentication or request errors
    """
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json"
    }
    
    url = f"{YELP_API_BASE_URL}/businesses/search"
    
    print(f"[{datetime.now().isoformat()}] Initiating Yelp API request...")
    print(f"URL: {url}")
    print(f"Parameters: {json.dumps(params, indent=2)}")
    
    try:
        with httpx.Client() as client:
            response = client.get(url, headers=headers, params=params, timeout=30.0)
            
            # Check for authentication errors
            if response.status_code == 401:
                raise YelpAPIError("Authentication failed. Please check your YELP_API_KEY.")
            
            # Check for rate limit errors
            if response.status_code == 429:
                raise YelpAPIError("API rate limit exceeded. Please try again later.")
            
            # Check for other HTTP errors
            response.raise_for_status()
            
            print(f"[{datetime.now().isoformat()}] Request successful. Status: {response.status_code}")
            return response.json()
            
    except httpx.HTTPStatusError as e:
        error_detail = ""
        try:
            error_detail = e.response.json()
        except:
            error_detail = e.response.text
        raise YelpAPIError(f"HTTP error {e.response.status_code}: {error_detail}")
    except httpx.RequestError as e:
        raise YelpAPIError(f"Request error: {str(e)}")


def analyze_response_structure(data: dict) -> None:
    """
    Analyze and print the structure of the API response.
    
    Args:
        data: The API response data
    """
    print("\n" + "="*80)
    print("RESPONSE STRUCTURE ANALYSIS")
    print("="*80)
    
    # Get all field paths
    field_paths = get_field_paths(data)
    
    print(f"\nTotal fields discovered: {len(field_paths)}")
    print("\nField paths (dot notation):")
    print("-"*80)
    
    for path in field_paths:
        print(f"  {path}")
    
    # Summary statistics
    print("\n" + "-"*80)
    print("SUMMARY STATISTICS:")
    if "businesses" in data and isinstance(data["businesses"], list):
        print(f"  Total businesses returned: {len(data['businesses'])}")
        if data["businesses"]:
            print(f"  First business name: {data['businesses'][0].get('name', 'N/A')}")
            print(f"  First business ID: {data['businesses'][0].get('id', 'N/A')}")
    
    if "total" in data:
        print(f"  Total results available: {data['total']}")
    
    print("="*80)


def save_response(data: dict, filename: str) -> None:
    """
    Save the API response to a JSON file.
    
    Args:
        data: The API response data
        filename: Output filename
    """
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\n[{datetime.now().isoformat()}] Response saved to: {filename}")


def main():
    """Main execution function."""
    print("="*80)
    print("Zip Intelligence API - Yelp Sample Fetcher")
    print("Step 2: Fetch sample data from Pleasanton, CA")
    print("="*80)
    
    # Validate API key
    if not YELP_API_KEY:
        print("\nERROR: YELP_API_KEY not found in environment variables.")
        print("Please create a .env file with your Yelp API key.")
        print("Example: YELP_API_KEY=your_api_key_here")
        sys.exit(1)
    
    print(f"\nAPI Key: {'*' * (len(YELP_API_KEY) - 4)}{YELP_API_KEY[-4:]}")
    
    try:
        # Fetch data from Yelp
        response_data = fetch_yelp_businesses(YELP_API_KEY, SEARCH_PARAMS)
        
        # Log full JSON response
        print("\n" + "="*80)
        print("FULL JSON RESPONSE")
        print("="*80)
        print(json.dumps(response_data, indent=2, ensure_ascii=False))
        
        # Analyze response structure
        analyze_response_structure(response_data)
        
        # Save response to file
        save_response(response_data, OUTPUT_FILE)
        
        print(f"\n[{datetime.now().isoformat()}] Script completed successfully.")
        
    except YelpAPIError as e:
        print(f"\n[{datetime.now().isoformat()}] ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[{datetime.now().isoformat()}] UNEXPECTED ERROR: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()