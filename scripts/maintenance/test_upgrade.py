import asyncio
import os
from pathlib import Path
import sys
import uuid
import json
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

# Dati della persona target per il test
TARGET_PERSON_ID = "5bc0e95b-4602-4684-a573-db8431868c90"
TARGET_HASH = "5abf6072"
NEW_DISPLAY_NAME = "Marco Rossi (Test Biometrico)"

async def main():
    settings = get_settings()
    engine = create_async_engine(settings.database_url)
    
    async with engine.begin() as conn:
        print("--- RUNNING IDENTITY UPGRADE TEST SKETCH ---")
        
        # 1. Creiamo un fatto relazionale finto legato alla persona target (Tier B format)
        fact_id = uuid.uuid4()
        claim = f"Roberto interagisce regolarmente con un interlocutore ricorrente non identificato [cluster_id: {TARGET_HASH}]"
        src_dict = {"memory_ids": ["00000000-0000-0000-0000-000000000000"], "person_id": TARGET_PERSON_ID}
        
        # Pulisce eventuali vecchi fatti di test
        await conn.execute(text("DELETE FROM user_profile_facts WHERE claim LIKE :claim_match"), {"claim_match": f"%{TARGET_HASH}%"})
        
        # Inserisce il fatto finto
        await conn.execute(
            text("""
                INSERT INTO user_profile_facts
                  (fact_id, claim, category, confidence, source_memory_ids,
                   sensitivity, created_at, updated_at, user_confirmed)
                VALUES
                  (:fid, :claim, 'relation', 0.50, CAST(:src AS jsonb),
                   'normal', NOW() - INTERVAL '2 days', NOW() - INTERVAL '2 days', false)
            """),
            {
                "fid": str(fact_id),
                "claim": claim,
                "src": json.dumps(src_dict),
            }
        )
        print(f"Created dummy relation fact: {fact_id}")
        
        # 2. Promuoviamo la persona target a confirmed (identity_level = 2) ed impostiamo il nuovo display name
        await conn.execute(
            text("""
                UPDATE persons
                SET identity_level = 2,
                    relationship_type = 'friend',
                    first_name = 'Marco',
                    last_name = 'Rossi (Test)',
                    display_name = :display_name
                WHERE person_id = :pid
            """),
            {
                "pid": TARGET_PERSON_ID,
                "display_name": NEW_DISPLAY_NAME
            }
        )
        print(f"Promoted person {TARGET_PERSON_ID} to {NEW_DISPLAY_NAME}")
        
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(main())
