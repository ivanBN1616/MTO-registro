import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import tkinter.messagebox as MessageBox
import tkinter.filedialog as filedialog
from database.database import insertar_error, eliminar_error, actualizar_error
from utils.excel_loader import cargar_datos_desde_excel
from ui.agregar import AgregarErrorWindow
from config import DATABASE_NAME_2

import sqlite3


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


        # Botón para seleccionar base de datos
        self.db_selector = ctk.CTkOptionMenu(
            search_frame, 
            values=["lenze9300.db", "lenze8200.db", "lenze8400.db"], 
            command=self.cambiar_base_datos
        )
        self.db_selector.pack(side="left", padx=5)

        search_label = ctk.CTkLabel(search_frame, text="Buscar:")
        search_label.pack(side="left", padx=5)

        self.buscar_entry = ctk.CTkEntry(search_frame, width=200)
        self.buscar_entry.pack(side="left", padx=5)

        # Botón Buscar
        buscar_btn = ctk.CTkButton(search_frame, text="Buscar", width=80, command=self.buscar_errores)
        buscar_btn.pack(side="left", padx=5)

        # --- Treeview con Scroll ---
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        # Treeview
        self.tree = ttk.Treeview(self.tree_frame, columns=("Num", "Pantalla", "Descripcion"), show='headings')
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        # Estilo del Scrollbar
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar", gripcount=0, background="gray", troughcolor="gray", sliderrelief="flat", slidercolor="gray")

        # Scrollbar
        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

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

        cargar_excel_btn = ctk.CTkButton(search_frame, text="Excel", width=80, command=self.cargar_desde_excel)
        cargar_excel_btn.pack(side="left", padx=5)

        boton_refrescar = ctk.CTkButton(search_frame, text="Refrescar", width=80, command=self.cargar_todos)
        boton_refrescar.pack(side="left", padx=5, pady=5)


    def cambiar_base_datos(self, db_name):
        """Cambia la base de datos y recarga los datos en la interfaz."""
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()  # Cerrar la conexión anterior
            
            self.conn = sqlite3.connect(db_name)  # Crear una nueva conexión
            self.cargar_todos()  # Recargar los datos en la tabla
            print(f"Conectado a la base de datos: {db_name}")
        except Exception as e:
            MessageBox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")


    def cargar_desde_excel(self):
        """Carga datos desde un archivo Excel a la base de datos."""
        file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
        if not file_path:
            return

        cargar_datos_desde_excel(self.conn, self.cargar_todos, file_path)

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
            self.tree.yview_moveto(0)  # Mueve el scroll al inicio

    def show_menu(self):
        """Muestra el menú desplegable."""
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Agregar", command=self.abrir_ventana_agregar)
        menu.add_command(label="Eliminar", command=self.eliminar_error)
        menu.add_command(label="Editar", command=self.editar_error)

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
        ventana = ctk.CTkToplevel(self.master)
        ventana.title("Agregar Nuevo Error")

        # Obtener dimensiones de la ventana principal
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()

        # Calcular la posición al lado de la ventana principal
        ventana_width = 400
        ventana_height = 350
        posicion_x = master_x + master_width + 200  # Colocarla al lado derecho
        posicion_y = master_y

        ventana.geometry(f"{ventana_width}x{ventana_height}+{posicion_x}+{posicion_y}")

        # Asegurarse de que la ventana emergente esté en primer plano
        ventana.lift()

        # Definir las etiquetas para los campos
        labels = ["Núm.", "Pantalla", "Descripción", "Causa", "Solución"]
        self.entries = {}

        # Crear los campos de entrada y las etiquetas
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

        # Botón de guardar
        guardar_btn = ctk.CTkButton(ventana, text="Guardar", command=lambda: self.guardar_error(ventana))
        guardar_btn.grid(row=len(labels), column=0, columnspan=2, pady=10)

    def guardar_error(self, ventana):
        """Guarda los datos introducidos en la base de datos activa."""
        num = self.entries["Núm."].get()
        pantalla = self.entries["Pantalla"].get()
        descripcion = self.entries["Descripción"].get()
        causa = self.entries["Causa"].get("1.0", "end-1c")
        solucion = self.entries["Solución"].get("1.0", "end-1c")

        if not all([num, pantalla, descripcion, causa, solucion]):
            MessageBox.showwarning("Campos incompletos", "Por favor, completa todos los campos.")
            return

        self.insertar_en_base_datos(num, pantalla, descripcion, causa, solucion, self.conn)  # Usar self.conn

        ventana.destroy()
        self.cargar_todos()  # Recargar la tabla después de agregar



    def insertar_en_base_datos(self, num, pantalla, descripcion, causa, solucion, conn):
        """Inserta los datos en la base de datos."""
        try:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO errores (num, pantalla, descripcion, causa, solucion)
                VALUES (?, ?, ?, ?, ?)
            ''', (num, pantalla, descripcion, causa, solucion))

            conn.commit()
            cursor.close()  # Cierra el cursor
            print("Error guardado exitosamente en la base de datos.")
        except Exception as e:
            print(f"Error al guardar en la base de datos: {e}")


    def ver_detalle(self, event):
        """Muestra una ventana con los detalles del error seleccionado."""
        item = self.tree.selection()[0]
        error_id = int(item)
        cursor = self.conn.cursor()
        cursor.execute('SELECT * FROM errores WHERE id = ?', (error_id,))
        detalle = cursor.fetchone()

        # Crear una nueva ventana
        detalle_win = ctk.CTkToplevel(self)
        detalle_win.title("Detalle del Error")
        
        # Establecer tamaño inicial y color de fondo
        detalle_win.geometry("800x500")
        detalle_win.configure(bg="#f5f5f5")  # Fondo gris claro

        # Etiquetas para los campos
        labels = ["Núm.", "Pantalla", "Descripción", "Causa", "Solución"]
        
        for idx, info in enumerate(detalle[1:]):  # Omitir el id
            # Etiqueta para el nombre del campo
            lbl = ctk.CTkLabel(detalle_win, text=f"{labels[idx]}:", font=("Arial", 12, "bold"))
            lbl.grid(row=idx, column=0, sticky="e", padx=20, pady=10)

            # Valor del campo, usando etiquetas para valores
            valor = ctk.CTkLabel(detalle_win, text=info, font=("Arial", 12), anchor="w", wraplength=600)
            valor.grid(row=idx, column=1, sticky="w", padx=20, pady=10)

            # Si el campo es "Causa" o "Solución", aseguramos que el texto largo se ajuste correctamente
            if labels[idx] in ["Causa", "Solución"]:
                valor.configure(wraplength=600)  # Ajustar el largo máximo de cada línea

            # Reajustamos la columna para que se expanda en función del contenido
            detalle_win.grid_columnconfigure(1, weight=1, uniform="column1")

        # Botón de cerrar
        cerrar_btn = ctk.CTkButton(detalle_win, text="Cerrar", command=detalle_win.destroy, width=100)
        cerrar_btn.grid(row=len(labels), column=0, columnspan=2, pady=20, padx=10)

        # Asegurar que la ventana de detalles esté al frente y no sea redimensionable
        detalle_win.resizable(True, True)  # Permitir redimensionar
        detalle_win.lift()  # Asegura que la ventana emergente esté al frente
        detalle_win.focus_set()  # Focaliza la ventana emergente

        # Ajustar el tamaño de las filas y columnas para que se adapten correctamente
        detalle_win.grid_rowconfigure(len(labels), weight=1)
        detalle_win.grid_columnconfigure(0, weight=1)
        detalle_win.grid_columnconfigure(1, weight=3)

        # Actualizar la ventana para ajustarse al contenido
        detalle_win.update_idletasks()

        # Establecer un tamaño mínimo para la ventana
        detalle_win.geometry(f"{detalle_win.winfo_width()}x{detalle_win.winfo_height()}")



    def eliminar_error(self):
        """Elimina el error seleccionado en el Treeview."""
        selected_item = self.tree.selection()

        if not selected_item:
            MessageBox.showwarning("Selección requerida", "Por favor, selecciona un error para eliminar.")
            return

        error_id = selected_item[0]

        confirmar = MessageBox.askyesno("Confirmar eliminación", "¿Estás seguro de que deseas eliminar este error?")

        if confirmar:
            try:
                eliminar_error(self.conn, error_id)  # Asegúrate de que esta función esté implementada correctamente en database.py
                self.cargar_todos()
            except Exception as e:
                MessageBox.showerror("Error", f"No se pudo eliminar el error.\n{str(e)}")

    def editar_error(self):
        """Abre una ventana emergente para editar un error seleccionado."""
        selected_item = self.tree.selection()

        if not selected_item:
            MessageBox.showwarning("Selección requerida", "Por favor, selecciona un error para editar.")
            return

        error_id = int(selected_item[0])
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, num, pantalla, descripcion, causa, solucion FROM errores WHERE id = ?', (error_id,))
        detalle = cursor.fetchone()

        if not detalle:
            MessageBox.showerror("Error", "No se encontraron detalles para este error.")
            return

        ventana = ctk.CTkToplevel(self)
        ventana.title("Editar Error")
        ventana.geometry("450x400")
        ventana.resizable(False, False)

        labels = ["Núm.", "Pantalla", "Descripción", "Causa", "Solución"]
        self.entries = {}

        for idx, label_text in enumerate(labels):
            lbl = ctk.CTkLabel(ventana, text=label_text)
            lbl.grid(row=idx, column=0, padx=10, pady=5, sticky="e")

            valor = detalle[idx + 1] if idx + 1 < len(detalle) else ""

            if label_text in ["Causa", "Solución"]:
                text_box = ctk.CTkTextbox(ventana, width=250, height=80, wrap="word")
                text_box.grid(row=idx, column=1, padx=10, pady=5, sticky="ew")
                text_box.insert("1.0", valor)
                text_box.configure(state="normal")
                self.entries[label_text] = text_box
            else:
                entry = ctk.CTkEntry(ventana, width=250)
                entry.grid(row=idx, column=1, padx=10, pady=5, sticky="ew")
                entry.insert(0, valor)
                self.entries[label_text] = entry

        guardar_btn = ctk.CTkButton(ventana, text="Guardar", command=lambda: self.guardar_edicion(ventana, error_id), width=100, height=30)
        guardar_btn.grid(row=len(labels), column=0, columnspan=2, pady=10, padx=10, sticky="e")

        ventana.grid_columnconfigure(1, weight=1)

    def guardar_edicion(self, ventana, error_id):
        """Guarda las ediciones de un error seleccionado."""
        num = self.entries["Núm."].get()
        pantalla = self.entries["Pantalla"].get()
        descripcion = self.entries["Descripción"].get()
        causa = self.entries["Causa"].get("1.0", "end-1c")
        solucion = self.entries["Solución"].get("1.0", "end-1c")

        if not all([num, pantalla, descripcion, causa, solucion]):
            return

        actualizar_error(self.conn, error_id, num, pantalla, descripcion, causa, solucion)
        ventana.destroy()
        self.cargar_todos()
