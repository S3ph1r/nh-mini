import asyncio
import os
from pathlib import Path
import sys
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Carica .env
prod_env = Path("/opt/Lifelog2/.env")
dev_env = Path(__file__).parent.parent.parent / "sviluppi" / "Lifelog2" / ".env"
if prod_env.exists():
    load_dotenv(prod_env)
elif dev_env.exists():
    load_dotenv(dev_env)

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src" / "backend"))
sys.path.insert(0, "/opt/Lifelog2/src/backend")

from lifelog2.core.config import get_settings

TARGET_PERSON_ID = "5bc0e95b-4602-4684-a573-db8431868c90"
TARGET_HASH = "5abf6072"

async def main():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    
    async with engine.begin() as conn:
        print("--- CLEANING UP TEST DATA ---")
        
        # 1. Rimuove il fatto di test
        res_facts = await conn.execute(
            text("DELETE FROM user_profile_facts WHERE claim LIKE :claim_match"),
            {"claim_match": f"%Marco Rossi (Test Biometrico)%"}
        )
        print(f"Deleted test facts: {res_facts.rowcount}")
        
        # 2. Ripristina l'interlocutore a livello 0, 'unknown', nome originario
        res_person = await conn.execute(
            text("""
                UPDATE persons
                SET identity_level = 0,
                    relationship_type = 'unknown',
                    first_name = 'Interlocutore',
                    last_name = :last_name,
                    display_name = :display_name
                WHERE person_id = :pid
            """),
            {
                "pid": TARGET_PERSON_ID,
                "last_name": f"Ricorrente {TARGET_HASH}",
                "display_name": f"Interlocutore Ricorrente {TARGET_HASH}"
            }
        )
        print(f"Restored test person to original state: {res_person.rowcount}")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
