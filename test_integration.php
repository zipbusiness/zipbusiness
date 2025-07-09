<?php
/**
 * Test script to verify ZipBusiness API integration with Master Critic
 * 
 * This script tests:
 * 1. API connectivity
 * 2. Data retrieval for a specific city
 * 3. Restaurant data format
 */

$api_url = "https://zipbusiness-api.onrender.com";
$api_key = "SzfHh+mfnQWzE8fFIR4WAqkMf24KEDDVNAIU4o9kLVg=";

echo "Testing ZipBusiness API Integration\n";
echo "===================================\n\n";

// Test 1: Check API health
echo "1. Testing API Health Check...\n";
$health_url = $api_url . "/health";
$health_response = file_get_contents($health_url);
echo "Health Check Response: " . $health_response . "\n\n";

// Test 2: Get restaurants for Austin, TX
echo "2. Testing Restaurant Data Retrieval for Austin, TX...\n";
$restaurants_url = $api_url . "/api/v1/restaurants?city=Austin&state=TX&limit=5";

$context = stream_context_create([
    'http' => [
        'header' => "X-API-Key: " . $api_key . "\r\n"
    ]
]);

$restaurants_response = file_get_contents($restaurants_url, false, $context);
$restaurants = json_decode($restaurants_response, true);

if ($restaurants) {
    echo "Found " . count($restaurants['restaurants']) . " restaurants\n";
    echo "Total available: " . $restaurants['total'] . "\n\n";
    
    echo "Sample Restaurant Data:\n";
    if (!empty($restaurants['restaurants'])) {
        $sample = $restaurants['restaurants'][0];
        echo "- Name: " . $sample['name'] . "\n";
        echo "- ZPID: " . $sample['zpid'] . "\n";
        echo "- Rating: " . $sample['rating'] . "\n";
        echo "- Review Count: " . $sample['review_count'] . "\n";
        echo "- Cuisine: " . ($sample['cuisine_type'] ?? 'N/A') . "\n";
        echo "- Price Range: " . $sample['price_range'] . "\n";
    }
} else {
    echo "No restaurant data retrieved. The city might not have data yet.\n";
}

echo "\n===================================\n";
echo "Integration test complete!\n";
echo "\nNext steps:\n";
echo "1. Run the collect_cities.sh script to populate data\n";
echo "2. Verify data appears in the API\n";
echo "3. Test Master Critic list generation with Restaurant Intelligence enabled\n";