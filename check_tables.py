from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://neondb_owner:npg_wo9MZKGJ1zym@ep-proud-art-a8xtxs9t-pooler.eastus2.azure.neon.tech/neondb?sslmode=require"

engine = create_engine(DATABASE_URL)
with engine.connect() as conn:
    result = conn.execute(text("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"))
    tables = result.fetchall()
    print('Tables:', [t[0] for t in tables])