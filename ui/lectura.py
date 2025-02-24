import customtkinter as ctk
from tkinter import ttk
import sqlite3

class LecturaFrame(ctk.CTkFrame):
    def __init__(self, master, conn, **kwargs):
        super().__init__(master, **kwargs)
        self.conn = conn
        self.create_widgets()
        self.cargar_todos()  # Cargar todos los registros al iniciar

    def create_widgets(self):
        # Etiqueta y campo de búsqueda
        label = ctk.CTkLabel(self, text="Buscar:")
        label.grid(row=0, column=0, padx=5, pady=5, sticky='e')

        self.buscar_entry = ctk.CTkEntry(self, width=300)
        self.buscar_entry.grid(row=0, column=1, padx=5, pady=5)

        buscar_btn = ctk.CTkButton(self, text="Buscar", command=self.buscar_errores)
        buscar_btn.grid(row=0, column=2, padx=5, pady=5)

        # Treeview que muestra todos los atributos: NUM., Pantalla, Descripcion, Causa y Solucion
        self.tree = ttk.Treeview(self, columns=("Num", "Pantalla", "Descripcion", "Causa", "Solucion"), show='headings')
        self.tree.heading("Num", text="NUM.")
        self.tree.heading("Pantalla", text="Pantalla")
        self.tree.heading("Descripcion", text="Descripcion")
        self.tree.heading("Causa", text="Causa")
        self.tree.heading("Solucion", text="Solucion")

        self.tree.column("Num", width=80)
        self.tree.column("Pantalla", width=100)
        self.tree.column("Descripcion", width=300)
        self.tree.column("Causa", width=200)
        self.tree.column("Solucion", width=200)

        self.tree.grid(row=1, column=0, columnspan=3, padx=5, pady=5)

        # Vincular el evento de doble clic para ver detalles
        self.tree.bind("<Double-1>", self.ver_detalle)

    def cargar_todos(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, num, pantalla, descripcion, causa, solucion FROM errores')
        registros = cursor.fetchall()
        # Limpiar el Treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Insertar todos los registros en el Treeview, usando el id como identificador interno (iid)
        for reg in registros:
            id_reg, num, pantalla, descripcion, causa, solucion = reg
            self.tree.insert("", "end", iid=str(id_reg), values=(num, pantalla, descripcion, causa, solucion))

    def buscar_errores(self):
        busqueda = self.buscar_entry.get()
        cursor = self.conn.cursor()
        # Buscar en todos los campos relevantes
        cursor.execute('''
            SELECT id, num, pantalla, descripcion, causa, solucion FROM errores
            WHERE num LIKE ? OR pantalla LIKE ? OR descripcion LIKE ? OR causa LIKE ? OR solucion LIKE ?
        ''', (f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%'))
        registros = cursor.fetchall()
        # Limpiar el Treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        # Insertar registros filtrados en el Treeview
        for reg in registros:
            id_reg, num, pantalla, descripcion, causa, solucion = reg
            self.tree.insert("", "end", iid=str(id_reg), values=(num, pantalla, descripcion, causa, solucion))

    def ver_detalle(self, event):
        # Obtener el ID a través del identificador del ítem seleccionado
        item = self.tree.selection()[0]
        error_id = int(item)
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM errores WHERE id = ?', (error_id,))
        detalle = cursor.fetchone()

        # Crear una ventana emergente para mostrar el detalle completo
        detalle_win = ctk.CTkToplevel(self)
        detalle_win.title("Detalle del Error")

        # Los campos a mostrar (omitimos el id)
        labels = ["NUM.", "Pantalla", "Descripcion", "Causa", "Solucion"]
        for idx, info in enumerate(detalle[1:]):  # detalle[0] es el id
            label_text = ctk.CTkLabel(detalle_win, text=f"{labels[idx]}:")
            label_text.grid(row=idx, column=0, sticky='e', padx=5, pady=5)
            value_text = ctk.CTkLabel(detalle_win, text=info)
            value_text.grid(row=idx, column=1, sticky='w', padx=5, pady=5)
