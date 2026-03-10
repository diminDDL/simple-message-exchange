from fastapi import FastAPI, HTTPException, Query, Depends, Security
from fastapi.security.api_key import APIKeyHeader
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uvicorn
import time
import logging

app = FastAPI(title="Message Exchange API")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "timescaledb")
DB_PORT = os.getenv("DB_PORT", 5432)
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "message_exchange")
API_KEY = os.getenv("API_KEY", "my-super-secret-api-key")

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

def get_api_key(api_key: str = Security(api_key_header)):
    if not api_key or api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            user=DB_USER,
            password=DB_PASSWORD,
            dbname=DB_NAME
        )
        return conn
    except psycopg2.OperationalError as e:
        logger.error(f"Database connection error: {e}")
        raise HTTPException(status_code=503, detail="Database connection failed")

@app.get("/api/messages/recent")
def get_recent_messages(limit: int = Query(5, ge=1, le=100), api_key: str = Depends(get_api_key)):
    conn = get_db_connection()
    try:
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        query = """
            SELECT time, message_id, device_id, message_type, service_name, topic, payload
            FROM messages
            ORDER BY time DESC
            LIMIT %s;
        """
        cursor.execute(query, (limit,))
        rows = cursor.fetchall()
        
        # Convert datetime objects to string
        for row in rows:
            if 'time' in row and row['time']:
                row['time'] = row['time'].isoformat()
                
        return {"messages": rows}
    except psycopg2.Error as e:
        logger.error(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Database query failed")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)