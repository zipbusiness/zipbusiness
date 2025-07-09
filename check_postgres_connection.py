#!/usr/bin/env python3
"""
PostgreSQL Connection and Schema Verification
Checks database connectivity and verifies zipbusiness_restaurants table exists
"""

import os
import sys
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from datetime import datetime


class DatabaseConnectionChecker:
    """Handles PostgreSQL connection verification and schema inspection"""
    
    def __init__(self):
        self.database_url = os.environ.get('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Parse database URL
        parsed = urlparse(self.database_url)
        self.connection_params = {
            'host': parsed.hostname,
            'port': parsed.port or 5432,
            'database': parsed.path[1:],
            'user': parsed.username,
            'password': parsed.password
        }
        
    def check_connection(self):
        """Test database connectivity"""
        try:
            conn = psycopg2.connect(**self.connection_params)
            conn.close()
            return True
        except psycopg2.Error as e:
            print(f"❌ Failed to connect to database: {e}")
            return False
    
    def verify_table_schema(self):
        """Check if zipbusiness_restaurants table exists and inspect schema"""
        conn = None
        cursor = None
        
        try:
            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Check if table exists
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'zipbusiness_restaurants'
                );
            """)
            
            table_exists = cursor.fetchone()['exists']
            
            if not table_exists:
                raise RuntimeError("Table 'zipbusiness_restaurants' does not exist in the database")
            
            # Fetch column information
            cursor.execute("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    numeric_precision,
                    numeric_scale,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_schema = 'public' 
                AND table_name = 'zipbusiness_restaurants'
                ORDER BY ordinal_position;
            """)
            
            columns = cursor.fetchall()
            
            return True, columns
            
        except psycopg2.Error as e:
            return False, str(e)
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()
    
    def format_column_info(self, columns):
        """Format column information for display"""
        print("\n📋 Table Schema: zipbusiness_restaurants")
        print("=" * 80)
        print(f"{'Column Name':<25} {'Data Type':<20} {'Nullable':<10} {'Default':<20}")
        print("-" * 80)
        
        for col in columns:
            # Format data type with precision/scale if applicable
            data_type = col['data_type']
            if col['character_maximum_length']:
                data_type = f"{data_type}({col['character_maximum_length']})"
            elif col['numeric_precision'] and col['numeric_scale']:
                data_type = f"{data_type}({col['numeric_precision']},{col['numeric_scale']})"
            elif col['numeric_precision']:
                data_type = f"{data_type}({col['numeric_precision']})"
            
            # Format nullable
            nullable = "YES" if col['is_nullable'] == 'YES' else "NO"
            
            # Format default value
            default = col['column_default'] or '-'
            if len(default) > 20:
                default = default[:17] + "..."
            
            print(f"{col['column_name']:<25} {data_type:<20} {nullable:<10} {default:<20}")
        
        print("=" * 80)
        print(f"Total columns: {len(columns)}")


def main():
    """Main execution function"""
    print("🔍 PostgreSQL Connection and Schema Verification")
    print("=" * 60)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("=" * 60)
    
    try:
        checker = DatabaseConnectionChecker()
        
        # Test connection
        print("\n🔌 Testing database connection...")
        if not checker.check_connection():
            sys.exit(1)
        print("✅ Successfully connected to PostgreSQL database")
        
        # Verify schema
        print("\n🔍 Verifying table schema...")
        success, result = checker.verify_table_schema()
        
        if success:
            print("✅ Table 'zipbusiness_restaurants' exists")
            checker.format_column_info(result)
        else:
            print(f"❌ Schema verification failed: {result}")
            sys.exit(1)
        
        print("\n✅ Database verification completed successfully")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()