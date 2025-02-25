import tkinter as tk
import customtkinter as ctk

class AgregarErrorWindow(tk.Toplevel):
    def __init__(self, parent, insertar_error):
        super().__init__(parent)
        self.title("Agregar Error")
        self.geometry("400x300")
        self.transient(parent)  # La ventana se superpone a la principal
        self.grab_set()         # Evita que se interactúe con la ventana principal hasta cerrarla
        
        # Ejemplo: campos para ingresar datos
        tk.Label(self, text="Número:").pack(pady=5)
        self.num_entry = tk.Entry(self)
        self.num_entry.pack(pady=5)
        
        tk.Label(self, text="Pantalla:").pack(pady=5)
        self.pantalla_entry = tk.Entry(self)
        self.pantalla_entry.pack(pady=5)
        
        tk.Label(self, text="Descripción:").pack(pady=5)
        self.descripcion_entry = tk.Entry(self)
        self.descripcion_entry.pack(pady=5)
        
        tk.Label(self, text="Causa:").pack(pady=5)
        self.causa_entry = tk.Entry(self)
        self.causa_entry.pack(pady=5)
        
        tk.Label(self, text="Solución:").pack(pady=5)
        self.solucion_entry = tk.Entry(self)
        self.solucion_entry.pack(pady=5)
        
        guardar_btn = tk.Button(self, text="Guardar", command=self.guardar_error)
        guardar_btn.pack(pady=10)
        
        self.insertar_error = insertar_error
        self.parent = parent

    def guardar_error(self):
        # Recoge los datos ingresados
        num = self.num_entry.get()
        pantalla = self.pantalla_entry.get()
        descripcion = self.descripcion_entry.get()
        causa = self.causa_entry.get()
        solucion = self.solucion_entry.get()
        
        # Aquí se llama a la función insertar_error
        self.insertar_error(num, pantalla, descripcion, causa, solucion)
        
        # Si se inserta correctamente, se cierra la ventana
        self.destroy()
