import sqlite3

def init_db():
    conn = sqlite3.connect('errores.db')
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
