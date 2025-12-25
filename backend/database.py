import psycopg2
from psycopg2.extras import RealDictCursor, Json
import os
from datetime import datetime
import json

class Database:
    def __init__(self):
        """Initialize database connection"""
        self.conn = None
        self.connect()
    
    def connect(self):
        """Connect to PostgreSQL database"""
        try:
            # Get database credentials from environment variables
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'cable_validation'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', 'postgres'),
                port=os.getenv('DB_PORT', '5432')
            )
            print("✓ Connected to PostgreSQL database")
        except Exception as e:
            print(f"✗ Database connection failed: {e}")
            raise
    
    def init_db(self):
        """Create validations table if it doesn't exist"""
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS validations (
                        id SERIAL PRIMARY KEY,
                        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        design_query TEXT NOT NULL,
                        hitl_mode BOOLEAN NOT NULL,
                        extracted_attributes JSONB,
                        compliance_status TEXT,
                        recommendations JSONB,
                        confidence_score REAL,
                        session_id TEXT
                    )
                """)
                self.conn.commit()
                print("✓ Database table initialized")
        except Exception as e:
            print(f"✗ Failed to initialize database: {e}")
            self.conn.rollback()
            raise
    
    def store_validation(self, design_query, hitl_mode, validation_result, session_id=None):
        """
        Store validation results in database
        
        Args:
            design_query: Original design query string
            hitl_mode: Boolean indicating if HITL mode was used
            validation_result: Dictionary containing validation results
            session_id: Optional session ID for tracking
            
        Returns:
            validation_id: ID of the stored validation
        """
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO validations 
                    (design_query, hitl_mode, extracted_attributes, compliance_status, 
                     recommendations, confidence_score, session_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id
                """, (
                    design_query,
                    hitl_mode,
                    Json(validation_result.get('extracted_attributes', {})),
                    validation_result.get('compliance_status', 'UNKNOWN'),
                    Json(validation_result.get('recommendations', [])),
                    validation_result.get('confidence_score', 0.0),
                    session_id
                ))
                validation_id = cur.fetchone()[0]
                self.conn.commit()
                print(f"✓ Stored validation with ID: {validation_id}")
                return validation_id
        except Exception as e:
            print(f"✗ Failed to store validation: {e}")
            self.conn.rollback()
            raise
    
    def get_validation(self, validation_id):
        """
        Retrieve validation by ID
        
        Args:
            validation_id: ID of the validation to retrieve
            
        Returns:
            Dictionary containing validation data
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM validations WHERE id = %s
                """, (validation_id,))
                result = cur.fetchone()
                return dict(result) if result else None
        except Exception as e:
            print(f"✗ Failed to retrieve validation: {e}")
            return None
    
    def get_all_validations(self, limit=100):
        """
        Retrieve all validations
        
        Args:
            limit: Maximum number of validations to retrieve
            
        Returns:
            List of validation dictionaries
        """
        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM validations 
                    ORDER BY timestamp DESC 
                    LIMIT %s
                """, (limit,))
                results = cur.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            print(f"✗ Failed to retrieve validations: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")

# Global database instance
db = None

def get_db():
    """Get or create database instance"""
    global db
    if db is None:
        db = Database()
        db.init_db()
    return db
