## 1. Initialize alembic (creates alembic/ folder + alembic.ini)
alembic init alembic

## 2. Generate migration from your models (creates enum types + all 8 tables)
alembic revision --autogenerate -m "init schema"

## 3. Apply migration to Supabase Postgres
alembic upgrade head

## --- If you already manually ran the SQL in Supabase's SQL editor, use this instead of upgrade: ---
alembic stamp head

## Future schema changes:
alembic revision --autogenerate -m "add new field"
alembic upgrade head

## Rollback last migrate
alembic downgrade -1

## 4. Implementing seed file
python -m scripts.seed

## 5. Run server
uvicorn backend.app.main:app --reload --port 8000