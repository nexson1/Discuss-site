import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

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

sqlite_engine = create_engine(
    "sqlite:///instance/discuss-site.db"
)

postgres_engine = create_engine(database_url)

tables = ["users", "discuss_posts", "comments"]

for name, engine in [
    ("SQLITE", sqlite_engine),
    ("POSTGRESQL", postgres_engine)
]:
    print(f"\n--- {name} ---")

    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()

    with engine.connect() as connection:
        for table in tables:
            if table in existing_tables:
                count = connection.execute(
                    text(f'SELECT COUNT(*) FROM "{table}"')
                ).scalar()

                columns = [
                    column["name"]
                    for column in inspector.get_columns(table)
                ]

                print(f"{table}: {count} records")
                print(f"Columns: {columns}")
            else:
                print(f"{table}: TABLE NOT FOUND")