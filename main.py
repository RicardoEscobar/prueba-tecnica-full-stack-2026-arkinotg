import os
from datetime import datetime
import sqlite3

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
import uvicorn

# Cargar variables de entorno
load_dotenv()

app = FastAPI()


def get_db_path():
    db_path = os.getenv("SQLITE3_DB")

    if not db_path:
        raise ValueError(
            "La variable de entorno SQLITE3_DB no está definida. Verifica el archivo .env"
        )

    if not os.path.isfile(db_path):
        raise FileNotFoundError(
            f"No se encontró el archivo de base de datos en la ruta especificada: {db_path}"
        )

    return db_path


# Conexión a la base de datos
def get_db_connection(db_path=None):
    try:
        if db_path is None:
            db_path = get_db_path()

        conn = sqlite3.connect(db_path)
        return conn
    except sqlite3.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        raise


@app.get("/advisors/{advisor_id}/expired-policies")
def list_expired_policies(advisor_id: str):
    """Lista las pólizas vencidas de un asesor."""

    try:
        conn = get_db_connection()
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="No se pudo conectar a la base de datos"
        ) from e
    cursor = conn.cursor()

    try:
        now = datetime.now()
        now_str = now.strftime("%Y-%m-%d %H:%M:%S")
        today = now.date()

        cursor.execute(
            """
            SELECT id, client_id, insurer, expiration_date, status
            FROM policies
            WHERE advisor_id = ?
              AND expiration_date < ?
            """,
                        (advisor_id, now_str),
        )

        expired = cursor.fetchall()
        result = []

        for policy in expired:
            policy_id, client_id, insurer, exp_date_str, status = policy

            exp_date = datetime.fromisoformat(exp_date_str).date()

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
            days_overdue = max(days_overdue, 0)
            priority_message = {
                "urgent": f"Contactar urgentemente para evitar pérdida del cliente. Han pasado {days_overdue} días desde el vencimiento.",
                "normal": f"Contactar al cliente pronto para renovar la póliza. Han pasado {days_overdue} días desde el vencimiento.",
            }

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
                    "recommended_action": priority_message[priority],
                }
            )

        return result

    except sqlite3.Error as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e

    finally:
        conn.close()

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
