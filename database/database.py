import sqlite3


def obtener_error_por_id(conn, error_id):
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM errores WHERE id = ?', (error_id,))
    return cursor.fetchone()  # Retorna una tupla con los datos del error
    

# Función para insertar un nuevo error
def insertar_error(conn, num, pantalla, descripcion, causa, solucion):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO errores (num, pantalla, descripcion, causa, solucion)
        VALUES (?, ?, ?, ?, ?)
    ''', (num, pantalla, descripcion, causa, solucion))
    conn.commit()

# Función para eliminar un error por su ID
def eliminar_error(conn, error_id):
    cursor = conn.cursor()
    cursor.execute('DELETE FROM errores WHERE id = ?', (error_id,))
    conn.commit()


def editar_error(conn, error_id, num, pantalla, descripcion, causa, solucion):
    """Actualiza un error existente en la base de datos."""
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE errores
        SET num = ?, pantalla = ?, descripcion = ?, causa = ?, solucion = ?
        WHERE id = ?
    ''', (num, pantalla, descripcion, causa, solucion, error_id))
    conn.commit()


 
def actualizar_error(conn, error_id, num, pantalla, descripcion, causa, solucion):
    """Actualiza un error en la base de datos."""
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE errores
        SET num = ?, pantalla = ?, descripcion = ?, causa = ?, solucion = ?
        WHERE id = ?
    ''', (num, pantalla, descripcion, causa, solucion, error_id))
    conn.commit()
