import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.core.database import async_engine

async def check_table_structure():
    try:
        async with AsyncSession(async_engine) as session:
            # Check table structure
            result = await session.execute(text("PRAGMA table_info(users)"))
            columns = result.fetchall()
            print("Users table columns:")
            for col in columns:
                print(f"  {col}")
            
            print("\nCompanies table columns:")
            result = await session.execute(text("PRAGMA table_info(companies)"))
            columns = result.fetchall()
            for col in columns:
                print(f"  {col}")
                
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(check_table_structure())