import customtkinter as ctk
from database.db_manager import init_db
from ui.lectura import LecturaFrame
import sys
import os
from PIL import Image

def main():
    # Configuración de CustomTkinter
    ctk.set_appearance_mode("System")  # "System", "Dark" o "Light"
    ctk.set_default_color_theme("blue")

    # Inicializar la base de datos
    conn = init_db()

    # Crear la ventana principal
    app = ctk.CTk()
    app.title("Registro de Errores - Lenze")
    app.geometry("750x400")

    # Insertar el frame principal de lectura
    lectura_frame = LecturaFrame(app, conn)
    lectura_frame.pack(expand=True, fill="both")

    app.mainloop()

if __name__ == "__main__":
    main()


# Ruta del icono dependiendo si estamos en el ejecutable empaquetado o en modo desarrollo
if getattr(sys, 'frozen', False):
    # Si estamos en el ejecutable empaquetado
    icon_path = os.path.join(sys._MEIPASS, "icons", "paros.ico")
else:
    # Si estamos en el entorno de desarrollo (script)
    icon_path = "icons/paros.ico"



def cargar_iconos(self):
    # Detecta si la aplicación está ejecutándose como un EXE
    ruta_base = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(__file__)

    return {
        "menu": ctk.CTkImage(Image.open(os.path.join(ruta_base, "icons", "menu.png")), size=(25, 25)),
        # Aquí puedes agregar más iconos según lo necesites
    }


