#!/bin/bash
# Render.com deployment start script

echo "🚀 Starting Punjab Rozgar Portal deployment..."

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migration
echo "🔄 Running database migration..."
python -c "
import asyncio
import os
from sqlalchemy import text, create_engine, MetaData
from sqlalchemy.engine import Engine

def migrate_sync_database():
    database_url = os.getenv('DATABASE_URL', '')
    if not database_url or 'sqlite' in database_url:
        print('⚠️  Skipping migration - not PostgreSQL')
        return
        
    print('🔄 Running synchronous database migration...')
    
    # Convert postgres:// to postgresql:// if needed
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    engine = create_engine(database_url)
    
    required_columns = {
        'resume_required': 'BOOLEAN DEFAULT true',
        'application_url': 'TEXT',
        'contact_email': 'VARCHAR(200)',
        'contact_phone': 'VARCHAR(20)',
        'views_count': 'INTEGER DEFAULT 0',
        'applications_count': 'INTEGER DEFAULT 0',
        'saves_count': 'INTEGER DEFAULT 0',
        'shares_count': 'INTEGER DEFAULT 0',
        'slug': 'VARCHAR(500)',
        'meta_description': 'TEXT',
        'featured': 'BOOLEAN DEFAULT false',
        'urgent': 'BOOLEAN DEFAULT false',
        'government_scheme': 'BOOLEAN DEFAULT false',
        'reservation_category': 'VARCHAR(100)',
        'age_limit_min': 'INTEGER',
        'age_limit_max': 'INTEGER',
        'benefits': 'TEXT',
        'working_hours': 'VARCHAR(100)',
        'interview_process': 'TEXT',
        'additional_info': 'TEXT'
    }
    
    try:
        with engine.connect() as conn:
            # Check existing columns
            result = conn.execute(text(\"\"\"
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'jobs'
            \"\"\"))
            existing_columns = {row[0] for row in result}
            print(f'📋 Found {len(existing_columns)} existing columns')
            
            # Add missing columns
            for column, definition in required_columns.items():
                if column not in existing_columns:
                    print(f'➕ Adding column: {column}')
                    try:
                        conn.execute(text(f'ALTER TABLE jobs ADD COLUMN {column} {definition}'))
                        conn.commit()
                        print(f'✅ Added {column}')
                    except Exception as e:
                        print(f'⚠️  Column {column} might already exist: {e}')
            
            print('✅ Migration completed successfully')
            
    except Exception as e:
        print(f'❌ Migration failed: {e}')
        raise

if __name__ == '__main__':
    migrate_sync_database()
"

echo "✅ Migration completed"

# Start the application
echo "🚀 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port $PORT