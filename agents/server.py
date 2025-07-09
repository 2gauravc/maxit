import psycopg2
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse

app = FastAPI()
DB_DSN = "postgresql://postgres:postgres@langgraph-postgres:5432/postgres"

@app.get("/healthz")
def health_check():
    try:
        conn = psycopg2.connect(DB_DSN)
        cursor = conn.cursor()

        # Check if table 'run' exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name = 'run'
            );
        """)
        has_run_table = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        if not has_run_table:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"status": "fail", "reason": "`run` table missing"},
            )
        
        return {"status": "ok"}

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"status": "fail", "error": str(e)},
        )