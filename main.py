import os
from datetime import datetime
import sqlite3

from fastapi import FastAPI
from dotenv import load_dotenv
import uvicorn

# Cargar variables de entorno
load_dotenv()
DB = os.getenv("SQLITE3_DB")

if not DB:
    raise ValueError("La variable de entorno SQLITE3_DB no está definida. Verifica el archivo .env")

print(f"Usando base de datos: {DB}")

app = FastAPI()

# Conexión a la base de datos
def get_db_connection():
    try:
        conn = sqlite3.connect(DB)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise


@app.get("/advisors/{advisor_id}/expired-policies")
def list_expired_policies(advisor_id: str):
    """Lista las pólizas vencidas de un asesor."""

    conn = get_db_connection()
    cursor = conn.cursor()

    try:
        today = datetime.now().date()

        cursor.execute(
            """
            SELECT id, client_id, insurer, expiration_date, status
            FROM policies
            WHERE advisor_id = ?
              AND expiration_date < ?
            """,
            (advisor_id, today),
        )

        expired = cursor.fetchall()
        result = []

        for policy in expired:
            policy_id, client_id, insurer, exp_date_str, status = policy

            exp_date = datetime.strptime(
                exp_date_str, "%Y-%m-%d"
            ).date()

            days_overdue = (today - exp_date).days

            cursor.execute(
                """
                SELECT name, phone
                FROM clients
                WHERE id = ?
                """,
                (client_id,),
            )

            client = cursor.fetchone()

            cursor.execute(
                """
                SELECT COUNT(*)
                FROM contact_attempts
                WHERE policy_id = ?
                """,
                (policy_id,),
            )

            attempts = cursor.fetchone()[0]

            priority = "urgent" if days_overdue > 7 else "normal"

            result.append(
                {
                    "policy_id": policy_id,
                    "client_name": client[0],
                    "client_phone": client[1],
                    "insurer": insurer,
                    "expiration_date": exp_date_str,
                    "days_overdue": days_overdue,
                    "contact_attempts": attempts,
                    "priority": priority,
                    "recommended_action": (
                        "Contactar urgentemente para evitar pérdida del cliente"
                    ),
                }
            )

        return result

    finally:
        conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
