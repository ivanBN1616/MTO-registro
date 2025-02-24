import customtkinter as ctk
from database.db_manager import init_db
from ui.lectura import LecturaFrame

def main():
    ctk.set_appearance_mode("System")  # Puedes elegir "System", "Dark" o "Light"
    ctk.set_default_color_theme("blue")
    
    # Inicializar la base de datos
    conn = init_db()
    
    # Crear la ventana principal
    app = ctk.CTk()
    app.title("Consulta de Errores")
    app.geometry("900x600")
    
    # Insertar el frame de lectura
    lectura_frame = LecturaFrame(app, conn)
    lectura_frame.pack(expand=True, fill="both")
    
    app.mainloop()

if __name__ == "__main__":
    main()
