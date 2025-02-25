import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import tkinter.messagebox as MessageBox
from database.database import insertar_error, eliminar_error, actualizar_error

class LecturaFrame(ctk.CTkFrame):
    def __init__(self, master, conn, **kwargs):
        super().__init__(master, **kwargs)
        self.conn = conn
        self.create_widgets()
        self.cargar_todos()

    def create_widgets(self):
        # --- Panel de Búsqueda ---
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(side="top", fill="x", padx=5, pady=5)

        # Botón hamburguesa para el menú desplegable
        menu_button = ctk.CTkButton(search_frame, text="☰", width=30, height=30, command=self.show_menu)
        menu_button.pack(side="left", padx=5)

        search_label = ctk.CTkLabel(search_frame, text="Buscar:")
        search_label.pack(side="left", padx=5)

        self.buscar_entry = ctk.CTkEntry(search_frame, width=300)
        self.buscar_entry.pack(side="left", padx=5)

        # Botón Buscar
        buscar_btn = ctk.CTkButton(search_frame, text="Buscar", command=self.buscar_errores)
        buscar_btn.pack(side="left", padx=5)

        # --- Treeview ---
        self.tree = ttk.Treeview(self, columns=("Num", "Pantalla", "Descripcion"), show='headings')
        self.tree.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # Configuración de cabeceras del Treeview
        self.tree.heading("Num", text="Núm.")
        self.tree.heading("Pantalla", text="Pantalla")
        self.tree.heading("Descripcion", text="Descripción")

        self.tree.column("Num", width=80, stretch=False)
        self.tree.column("Pantalla", width=100, stretch=False)
        self.tree.column("Descripcion", width=250, stretch=True)

        # Establecer un fondo gris claro para las filas de datos
        self.tree.tag_configure('gris_claro', background='#f2f2f2')

        self.tree.bind("<Double-1>", self.ver_detalle)

    def cargar_todos(self):
        """Carga todos los registros de la base de datos en el Treeview."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, num, pantalla, descripcion FROM errores')
        registros = cursor.fetchall()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx, reg in enumerate(registros):
            id_reg, num, pantalla, descripcion = reg
            tag = 'gris_claro' if idx % 2 == 0 else ''  # Alternar el color de fondo
            self.tree.insert("", "end", iid=str(id_reg), values=(num, pantalla, descripcion), tags=(tag,))

    def show_menu(self):
        """Muestra el menú desplegable."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Agregar", command=self.abrir_ventana_agregar)
        menu.add_command(label="Eliminar", command=self.eliminar_error)
        #menu.add_command(label="Editar", command=self.editar_error)

        # Posicionamos el menú debajo del botón de hamburguesa
        menu.post(self.winfo_rootx() + 35, self.winfo_rooty() + 55)

    def buscar_errores(self):
        """Filtra los registros en el Treeview según el término de búsqueda."""
        busqueda = self.buscar_entry.get()
        cursor = self.conn.cursor()
        cursor.execute(''' 
            SELECT id, num, pantalla, descripcion FROM errores
            WHERE num LIKE ? OR pantalla LIKE ? OR descripcion LIKE ? 
        ''', (f'%{busqueda}%', f'%{busqueda}%', f'%{busqueda}%'))
        registros = cursor.fetchall()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx, reg in enumerate(registros):
            id_reg, num, pantalla, descripcion = reg
            tag = 'gris_claro' if idx % 2 == 0 else ''  # Alternar el color de fondo
            self.tree.insert("", "end", iid=str(id_reg), values=(num, pantalla, descripcion), tags=(tag,))

    def abrir_ventana_agregar(self):
        """Abre una ventana emergente para agregar un nuevo error."""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Agregar Nuevo Error")

        # Obtener dimensiones de la ventana principal
        master_width = self.winfo_width()
        master_height = self.winfo_height()
        master_x = self.winfo_x()
        master_y = self.winfo_y()

        # Calcular la posición al lado de la ventana principal
        ventana_width = 400
        ventana_height = 350
        posicion_x = master_x + master_width + 200  # Colocarla al lado derecho
        posicion_y = master_y

        ventana.geometry(f"{ventana_width}x{ventana_height}+{posicion_x}+{posicion_y}")

        # Asegurarse de que la ventana emergente esté en primer plano
        ventana.lift()

        labels = ["Núm.", "Pantalla", "Descripción", "Causa", "Solución"]
        self.entries = {}

        for idx, label_text in enumerate(labels):
            lbl = ctk.CTkLabel(ventana, text=label_text)
            lbl.grid(row=idx, column=0, padx=10, pady=5, sticky="e")

            # Para Causa y Solución usar Text en lugar de Entry
            if label_text in ["Causa", "Solución"]:
                text_box = ctk.CTkTextbox(ventana, width=250, height=80)
                text_box.grid(row=idx, column=1, padx=10, pady=5)
                self.entries[label_text] = text_box
            else:
                entry = ctk.CTkEntry(ventana, width=250)
                entry.grid(row=idx, column=1, padx=10, pady=5)
                self.entries[label_text] = entry

        guardar_btn = ctk.CTkButton(ventana, text="Guardar", command=lambda: self.guardar_error(ventana))
        guardar_btn.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def guardar_error(self, ventana):
        """Guarda los datos ingresados en la ventana emergente en la base de datos."""
        num = self.entries["Núm."].get()
        pantalla = self.entries["Pantalla"].get()
        descripcion = self.entries["Descripción"].get()
        causa = self.entries["Causa"].get("1.0", "end-1c")  # Obtener texto completo de Text
        solucion = self.entries["Solución"].get("1.0", "end-1c")  # Obtener texto completo de Text

        # Validar que no falte ningún dato
        if not all([num, pantalla, descripcion, causa, solucion]):
            return

        # Llamar a la función del módulo database para insertar el error
        insertar_error(self.conn, num, pantalla, descripcion, causa, solucion)
        ventana.destroy()
        self.cargar_todos()

    def ver_detalle(self, event):
        """Muestra una ventana con los detalles del error seleccionado."""
        item = self.tree.selection()[0]
        error_id = int(item)
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM errores WHERE id = ?', (error_id,))
        detalle = cursor.fetchone()

        detalle_win = ctk.CTkToplevel(self)
        detalle_win.title("Detalle del Error")
        labels = ["Núm.", "Pantalla", "Descripción", "Causa", "Solución"]
        for idx, info in enumerate(detalle[1:]):  # Omitir id
            lbl = ctk.CTkLabel(detalle_win, text=f"{labels[idx]}:")
            lbl.grid(row=idx, column=0, sticky="e", padx=5, pady=5)
            valor = ctk.CTkLabel(detalle_win, text=info)
            valor.grid(row=idx, column=1, sticky="w", padx=5, pady=5)

    def eliminar_error(self):
        """Elimina el error seleccionado en el Treeview."""
        selected_item = self.tree.selection()

        if not selected_item:
            MessageBox.showwarning("Selección requerida", "Por favor, selecciona un error para eliminar.")
            return

        # Obtenemos el ID del error seleccionado, que es el iid
        error_id = selected_item[0]

        # Mostrar el cuadro de confirmación
        confirmar = MessageBox.askyesno("Confirmar eliminación", "¿Estás seguro de que deseas eliminar este error?")

        if confirmar:
            try:
                # Llamar a la función de eliminación (deberías tener la lógica en database.py)
                eliminar_error(self.conn, error_id)  # Asegúrate de que esta función esté implementada correctamente en database.py
                # Recargar la lista de errores
                self.cargar_todos()
            except Exception as e:
                MessageBox.showerror("Error", f"No se pudo eliminar el error.\n{str(e)}")

    def editar_error(self):
        """Abre una ventana emergente para editar un error seleccionado."""
        selected_item = self.tree.selection()

        if not selected_item:
            MessageBox.showwarning("Selección requerida", "Por favor, selecciona un error para editar.")
            return

        # Si se ha seleccionado un elemento, proceder con la edición
        item = selected_item[0]
        error_id = int(item)
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM errores WHERE id = ?', (error_id,))
        detalle = cursor.fetchone()

        if not detalle:
            MessageBox.showerror("Error", "No se encontraron detalles para este error.")
            return

        # Abrir ventana emergente para editar
        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar Error")

        labels = ["Núm.", "Pantalla", "Descripción", "Causa", "Solución"]
        self.entries = {}

        for idx, label_text in enumerate(labels):
            lbl = ctk.CTkLabel(ventana, text=label_text)
            lbl.grid(row=idx, column=0, padx=10, pady=5, sticky="e")

            # Para Causa y Solución usar Text en lugar de Entry
            if label_text in ["Causa", "Solución"]:
                text_box = ctk.CTkTextbox(ventana, width=250, height=80)
                text_box.grid(row=idx, column=1, padx=10, pady=5)
                self.entries[label_text] = text_box
            else:
                entry = ctk.CTkEntry(ventana, width=250)
                entry.grid(row=idx, column=1, padx=10, pady=5)
                self.entries[label_text] = entry

        # Rellenar con los datos existentes
        for idx, label_text in enumerate(labels):
            if label_text in ["Causa", "Solución"]:
                self.entries[label_text].insert("1.0", detalle[idx + 3])  # Causa y Solución empiezan desde el índice 3
            else:
                self.entries[label_text].insert(0, detalle[idx + 1])  # Para los demás, insertamos en el índice correspondiente

        guardar_btn = ctk.CTkButton(ventana, text="Guardar", 
                                command=lambda: self.guardar_edicion(ventana, error_id))
        guardar_btn.grid(row=len(labels), column=0, columnspan=2, pady=10)


    def guardar_edicion(self, ventana, error_id):
        """Guarda las ediciones de un error seleccionado."""
        num = self.entries["Núm."].get()
        pantalla = self.entries["Pantalla"].get()
        descripcion = self.entries["Descripción"].get()
        causa = self.entries["Causa"].get("1.0", "end-1c")
        solucion = self.entries["Solución"].get("1.0", "end-1c")

        # Validar que no falte ningún dato
        if not all([num, pantalla, descripcion, causa, solucion]):
            return

        # Llamar a la función para actualizar los datos en la base de datos
        actualizar_error(self.conn, error_id, num, pantalla, descripcion, causa, solucion)
        ventana.destroy()
        self.cargar_todos()
