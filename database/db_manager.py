import sqlite3
from config import DATABASE_NAME
from config import DATABASE_NAME_2

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
    return conn  # Devuelve la conexión para su uso posterior

def init_db_2():
    """
    Conecta con la segunda base de datos y crea la tabla 'errores' si no existe.
    """
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_NAME_2)
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
        print(f"Base de datos {DATABASE_NAME_2} y tabla creadas correctamente.")
        return conn  # Devuelve la conexión para su uso posterior
    except sqlite3.Error as e:
        print(f"Error al conectar o crear la base de datos: {e}")
    finally:
        # Asegurarse de cerrar la conexión si no fue devuelta
        if conn:
            conn.close()
    return None  # Si hay un error, retorna None

# Llamar a ambas funciones para inicializar las bases de datos
conn_1 = init_db()  # Crea y conecta a la base de datos principal
conn_2 = init_db_2()  # Crea y conecta a la segunda base de datos

# Ejemplo de uso de las conexiones
if conn_1:
    print(f"Conexión a {DATABASE_NAME} establecida.")
if conn_2:
    print(f"Conexión a {DATABASE_NAME_2} establecida.")
