-- ZipBusiness.ai Restaurant Table Schema
-- Production-ready PostgreSQL table for storing normalized Yelp restaurant data
-- Designed for millions of rows with optimal indexing strategy

CREATE TABLE zipbusiness_restaurants (
    -- Primary Key
    id SERIAL PRIMARY KEY,
    
    -- Required Fields (NOT NULL)
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    zip_code TEXT NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    categories TEXT[] NOT NULL,
    yelp_id TEXT UNIQUE NOT NULL,
    
    -- Optional Fields (NULLABLE)
    phone TEXT,
    display_phone TEXT,
    price TEXT,
    rating NUMERIC(2,1),
    review_count INTEGER,
    hours JSONB,
    is_open_now BOOLEAN,
    image_url TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for optimal query performance
CREATE INDEX idx_zipbusiness_restaurants_zip_code ON zipbusiness_restaurants(zip_code);
CREATE INDEX idx_zipbusiness_restaurants_city ON zipbusiness_restaurants(city);
CREATE INDEX idx_zipbusiness_restaurants_categories ON zipbusiness_restaurants USING GIN(categories);
CREATE INDEX idx_zipbusiness_restaurants_location ON zipbusiness_restaurants(latitude, longitude);

-- Trigger to automatically update the updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_zipbusiness_restaurants_updated_at 
    BEFORE UPDATE ON zipbusiness_restaurants 
    FOR EACH ROW 
    EXECUTE FUNCTION update_updated_at_column();