import pandas as pd
import sqlite3

def cargar_datos_desde_excel(conn, callback, file_path):
    try:
        # Cargar archivo Excel
        df = pd.read_excel(file_path, dtype=str)  # Leer todo como texto
        df.columns = df.columns.str.strip().str.lower()  # Limpiar espacios y convertir a minúsculas

        # Mostrar los nombres de las columnas para depuración
        print(f"🛠 Columnas encontradas en el Excel: {df.columns.tolist()}")

        # Mapeo esperado (normalizamos los nombres)
        columnas_requeridas = {"num", "pantalla", "descripcion"}

        if not columnas_requeridas.issubset(set(df.columns)):
            raise ValueError(f"❌ El archivo Excel no tiene las columnas requeridas: {columnas_requeridas}")

        cursor = conn.cursor()

        for _, row in df.iterrows():
            try:
                num = row.get("num", "").strip() if pd.notna(row.get("num")) else ""
                pantalla = row.get("pantalla", "").strip() if pd.notna(row.get("pantalla")) else ""
                descripcion = row.get("descripcion", "").strip() if pd.notna(row.get("descripcion")) else ""

                cursor.execute(
                    "INSERT INTO errores (num, pantalla, descripcion) VALUES (?, ?, ?)",
                    (num, pantalla, descripcion)
                )
            except Exception as fila_error:
                print(f"⚠️ Error al procesar la fila {_}: {fila_error}")

        conn.commit()
        callback()
        print("✅ Datos cargados exitosamente.")

    except Exception as e:
        print(f"❌ Error al cargar el archivo Excel: {e}")
