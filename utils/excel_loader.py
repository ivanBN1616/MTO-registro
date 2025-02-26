import pandas as pd
import sqlite3

def borrar_datos(conn):
    try:
        cursor = conn.cursor()
        # Borrar todos los datos de la tabla 'errores'
        cursor.execute("DELETE FROM errores")
        conn.commit()
        print("✅ Todos los datos han sido eliminados correctamente.")
    except Exception as e:
        print(f"❌ Error al borrar los datos: {e}")

def cargar_datos_desde_excel(conn, callback, file_path):
    try:
        # Eliminar los datos existentes antes de añadir nuevos
        borrar_datos(conn)

        # Cargar archivo Excel
        df = pd.read_excel(file_path, dtype=str)  # Leer todo como texto
        df.columns = df.columns.str.strip().str.lower()  # Limpiar espacios y convertir a minúsculas

        # Renombrar columnas para asegurarnos de que coincidan
        df.rename(columns={
            'núm.': 'num',
            'descripción': 'descripcion',
            'causa': 'causa',  # Aseguramos que causa sea parte de las columnas
            'solución': 'solucion'  # Aseguramos que solucion sea parte de las columnas
        }, inplace=True)

        # Mostrar los nombres de las columnas para depuración
        print(f"🛠 Columnas encontradas en el Excel: {df.columns.tolist()}")

        # Mapeo esperado (normalizamos los nombres)
        columnas_requeridas = {"num", "pantalla", "descripcion", "causa", "solucion"}

        if not columnas_requeridas.issubset(set(df.columns)):
            raise ValueError(f"❌ El archivo Excel no tiene las columnas requeridas: {columnas_requeridas}")

        # Rellenar las celdas vacías con el valor anterior (para celdas combinadas)
        df["num"] = df["num"].fillna(method="ffill")
        df["pantalla"] = df["pantalla"].fillna(method="ffill")
        df["descripcion"] = df["descripcion"].fillna(method="ffill")
        df["causa"] = df["causa"].fillna(method="ffill")
        df["solucion"] = df["solucion"].fillna(method="ffill")

        cursor = conn.cursor()

        for _, row in df.iterrows():
            try:
                num = row.get("num", "").strip() if pd.notna(row.get("num")) else ""
                pantalla = row.get("pantalla", "").strip() if pd.notna(row.get("pantalla")) else ""
                descripcion = row.get("descripcion", "").strip() if pd.notna(row.get("descripcion")) else ""
                causa = row.get("causa", "").strip() if pd.notna(row.get("causa")) else ""
                solucion = row.get("solucion", "").strip() if pd.notna(row.get("solucion")) else ""

                # Verificar si num no está vacío
                if num:
                    cursor.execute(
                        "INSERT INTO errores (num, pantalla, descripcion, causa, solucion) VALUES (?, ?, ?, ?, ?)",
                        (num, pantalla, descripcion, causa, solucion)
                    )
                else:
                    print(f"⚠️ Fila {_} tiene un valor vacío en 'num', se omite.")

            except Exception as fila_error:
                print(f"⚠️ Error al procesar la fila {_}: {fila_error}")

        conn.commit()
        callback()
        print("✅ Datos cargados exitosamente.")

    except Exception as e:
        print(f"❌ Error al cargar el archivo Excel: {e}")
