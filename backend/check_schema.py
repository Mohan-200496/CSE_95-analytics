import os
os.environ['DATABASE_URL'] = 'postgresql://postgres.gdcrvcvpqzoxsttbecza:EL5kW8V2HLIp!0W@aws-0-us-west-1.pooler.supabase.com:6543/postgres'

try:
    from app.core.database import engine
    from sqlalchemy import inspect
    
    inspector = inspect(engine)
    print('Available tables:', inspector.get_table_names())
    
    if 'jobs' in inspector.get_table_names():
        cols = inspector.get_columns('jobs')
        print('\nJob table columns:')
        for col in cols:
            print(f'  - {col["name"]} ({col["type"]})')
    else:
        print('Jobs table not found')
        
except Exception as e:
    print(f'Error: {e}')