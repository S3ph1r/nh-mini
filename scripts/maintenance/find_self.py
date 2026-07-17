import asyncio
import os
from pathlib import Path
import sys
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Carica .env a seconda dell'ambiente
prod_env = Path("/opt/Lifelog2/.env")
dev_env = Path(__file__).parent.parent.parent / "sviluppi" / "Lifelog2" / ".env"

if prod_env.exists():
    load_dotenv(prod_env)
    print(f"Loaded production .env from {prod_env}")
elif dev_env.exists():
    load_dotenv(dev_env)
    print(f"Loaded development .env from {dev_env}")

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "backend"))
# Se siamo in produzione su CT203, il path del backend è /opt/Lifelog2/src/backend
sys.path.insert(0, "/opt/Lifelog2/src/backend")

from lifelog2.core.config import get_settings

async def main():
    settings = get_settings()
    print("Database URL:", settings.database_url)
    engine = create_async_engine(settings.database_url)
    
    async with engine.connect() as conn:
        print("--- QUERY SELF PERSONS ---")
        res = await conn.execute(text("SELECT person_id, display_name, first_name, last_name, identity_level, relationship_type FROM persons WHERE relationship_type = 'self'"))
        rows = res.all()
        print(f"Found {len(rows)} self persons:")
        for r in rows:
            print(f"  - ID: {r[0]}, Name: {r[1]}, First: {r[2]}, Last: {r[3]}, Level: {r[4]}, Relation: {r[5]}")
            
        print("\n--- QUERY RECURRENT INTERLOCUTORS (TIER B) ---")
        res_b = await conn.execute(text("SELECT person_id, display_name, first_name, last_name, identity_level, relationship_type FROM persons WHERE first_name = 'Interlocutore'"))
        rows_b = res_b.all()
        print(f"Found {len(rows_b)} recurrent interlocutors:")
        for r in rows_b:
            print(f"  - ID: {r[0]}, Name: {r[1]}, First: {r[2]}, Last: {r[3]}, Level: {r[4]}, Relation: {r[5]}")
            
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
