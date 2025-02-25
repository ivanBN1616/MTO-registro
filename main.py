import customtkinter as ctk
from database.db_manager import init_db
from ui.lectura import LecturaFrame

def main():
    # Configuración de CustomTkinter
    ctk.set_appearance_mode("System")  # "System", "Dark" o "Light"
    ctk.set_default_color_theme("blue")

    # Inicializar la base de datos
    conn = init_db()

    # Crear la ventana principal
    app = ctk.CTk()
    app.title("Registro de Errores - Lenze 9300")
    app.geometry("900x400")

    # Insertar el frame principal de lectura
    lectura_frame = LecturaFrame(app, conn)
    lectura_frame.pack(expand=True, fill="both")

    app.mainloop()

if __name__ == "__main__":
    main()
