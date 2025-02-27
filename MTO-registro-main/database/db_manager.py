import sqlite3
from config import DATABASE_NAME

def init_db():
    """
    Conecta con la base de datos y crea la tabla 'errores' si no existe.
    La tabla incluye: num, pantalla, descripcion, causa y solucion.
    """
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS errores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            num TEXT,
            pantalla TEXT,
            descripcion TEXT,
            causa TEXT,
            solucion TEXT
        )
    ''')
    conn.commit()
    return conn
