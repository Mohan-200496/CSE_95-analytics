#!/usr/bin/env python3
"""
Simple script to create database tables
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy import create_engine
from app.core.config import get_settings
from app.core.database import Base

# Import all models to register them
from app.models.user import *
from app.models.job import *
from app.models.application import *
from app.models.company import *
from app.models.admin import *
from app.models.analytics import *
from app.models.skill import *

def create_database_tables():
    """Create all database tables"""
    print("🔧 Creating Database Tables")
    print("=" * 50)
    
    try:
        settings = get_settings()
        engine = create_engine(settings.DATABASE_URL)
        
        print("1. Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("   ✅ All tables created successfully!")
        
        # Verify tables were created
        print("\n2. Verifying tables...")
        inspector = engine.dialect.inspector(engine)
        tables = inspector.get_table_names()
        
        expected_tables = ['users', 'jobs', 'applications', 'companies', 'skills', 'analytics_events']
        
        print("   📋 Tables found:")
        for table in sorted(tables):
            status = "✅" if table in expected_tables else "ℹ️"
            print(f"      {status} {table}")
        
        missing_tables = set(expected_tables) - set(tables)
        if missing_tables:
            print(f"\n   ⚠️ Missing expected tables: {missing_tables}")
        else:
            print("\n   🎯 All expected tables created successfully!")
        
        engine.dispose()
        
        print("\n" + "=" * 50)
        print("✅ Database setup completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        return False

if __name__ == "__main__":
    create_database_tables()