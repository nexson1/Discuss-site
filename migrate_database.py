import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, MetaData, select, inspect, text

load_dotenv()

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL was not found in .env")

if database_url.startswith("postgres://"):
    database_url = database_url.replace(
        "postgres://", "postgresql+psycopg://", 1
    )
elif database_url.startswith("postgresql://"):
    database_url = database_url.replace(
        "postgresql://", "postgresql+psycopg://", 1
    )

# Connect to both databases
sqlite_engine = create_engine("sqlite:///instance/discuss-site.db")
postgres_engine = create_engine(database_url)

tables = ["users", "discuss_posts", "comments"]

# Read the existing SQLite database structure
metadata = MetaData()
metadata.reflect(bind=sqlite_engine, only=tables)

# Safety check: stop if any destination table already exists
existing_tables = inspect(postgres_engine).get_table_names()

already_existing = [
    table for table in tables if table in existing_tables
]

if already_existing:
    raise RuntimeError(
        f"These PostgreSQL tables already exist: {already_existing}. "
        "Migration stopped to prevent duplicate records."
    )

# Create matching tables in PostgreSQL
metadata.create_all(postgres_engine)

print("PostgreSQL tables created successfully.")

# Copy records in foreign-key dependency order
with sqlite_engine.connect() as source:
    with postgres_engine.begin() as destination:

        for table_name in tables:
            table = metadata.tables[table_name]

            rows = source.execute(
                select(table)
            ).mappings().all()

            if rows:
                destination.execute(
                    table.insert(),
                    [dict(row) for row in rows]
                )

            print(f"Migrated {len(rows)} records from {table_name}.")

# Reset PostgreSQL ID sequences
with postgres_engine.begin() as connection:
    for table_name in tables:
        connection.execute(
            text(f"""
                SELECT setval(
                    pg_get_serial_sequence('{table_name}', 'id'),
                    COALESCE(MAX(id), 1),
                    MAX(id) IS NOT NULL
                )
                FROM "{table_name}"
            """)
        )

print("\nMigration completed successfully!")

# Verify the migrated records
with postgres_engine.connect() as connection:
    for table_name in tables:
        count = connection.execute(
            text(f'SELECT COUNT(*) FROM "{table_name}"')
        ).scalar()

        print(f"PostgreSQL {table_name}: {count} records")

sqlite_engine.dispose()
postgres_engine.dispose()