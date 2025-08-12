# db.py
import mysql.connector
import sys
from datetime import datetime
from typing import List, Dict, Any

# Configuració de la base de dades
DB_HOST = "el_teu_servidor_mariadb"
DB_USER = "el_teu_usuari"
DB_PASSWORD = "la_teva_contrasenya"
DB_NAME = "el_nom_de_la_teva_base_de_dades"

# --- Validació i creació de la base de dades i la taula ---
def setup_database():
    """
    Connecta's a MariaDB i crea la base de dades i la taula si no existeixen.
    """
    db_connection = None
    try:
        db_connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = db_connection.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")
        cursor.execute(f"USE {DB_NAME}")
        
        create_table_query = """
        CREATE TABLE IF NOT EXISTS logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user VARCHAR(255) NOT NULL,
            long_text TEXT
        )
        """
        cursor.execute(create_table_query)
        db_connection.commit()
        
        print("Configuració de la base de dades completada correctament.")

    except mysql.connector.Error as err:
        print(f"Error en la configuració de la base de dades: {err}")
        sys.exit(1)
    finally:
        if db_connection and db_connection.is_connected():
            cursor.close()
            db_connection.close()

# --- Funcions per a les operacions amb la base de dades ---
def get_db_connection():
    """
    Retorna una connexió a la base de dades ja configurada.
    """
    return mysql.connector.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )

def create_log_entry(user: str, long_text: str) -> Dict[str, Any]:
    """Insereix un nou registre de log a la base de dades."""
    db_connection = get_db_connection()
    cursor = db_connection.cursor(dictionary=True)
    
    sql = "INSERT INTO logs (user, long_text) VALUES (%s, %s)"
    val = (user, long_text)
    cursor.execute(sql, val)
    db_connection.commit()
    
    last_id = cursor.lastrowid
    cursor.execute("SELECT * FROM logs WHERE id = %s", (last_id,))
    new_log = cursor.fetchone()

    cursor.close()
    db_connection.close()
    return new_log

def get_logs_by_user(user: str) -> List[Dict[str, Any]]:
    """Cerca logs per nom d'usuari."""
    db_connection = get_db_connection()
    cursor = db_connection.cursor(dictionary=True)
    
    sql = "SELECT * FROM logs WHERE user = %s ORDER BY timestamp DESC"
    cursor.execute(sql, (user,))
    logs = cursor.fetchall()

    cursor.close()
    db_connection.close()
    return logs

def get_logs_by_user_and_time(user: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """Cerca logs per nom d'usuari i rang de temps."""
    db_connection = get_db_connection()
    cursor = db_connection.cursor(dictionary=True)
    
    sql = "SELECT * FROM logs WHERE user = %s AND timestamp BETWEEN %s AND %s ORDER BY timestamp DESC"
    cursor.execute(sql, (user, start_time, end_time))
    logs = cursor.fetchall()
    
    cursor.close()
    db_connection.close()
    return logs