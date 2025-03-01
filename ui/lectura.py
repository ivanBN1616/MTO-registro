import customtkinter as ctk
from tkinter import ttk
import tkinter as tk
import tkinter.messagebox as MessageBox
from tkinter import messagebox
import tkinter.filedialog as filedialog
import sqlite3
from database.database import insertar_error, eliminar_error, actualizar_error,obtener_error_por_id
from utils.excel_loader import cargar_datos_desde_excel
from ui.detalle import ver_detalle

class LecturaFrame(ctk.CTkFrame):
    def __init__(self, master, conn, **kwargs):
        super().__init__(master, **kwargs)
        self.conn = conn
        self.entries = {}
        self.create_widgets()
        self.cargar_todos()
        self.detalle_abierto = False

    def create_widgets(self):
        self.create_search_panel()
        self.create_treeview()

    def create_search_panel(self):
        search_frame = ctk.CTkFrame(self)
        search_frame.pack(side="top", fill="x", padx=5, pady=5)

        self.create_menu_button(search_frame)
        self.create_db_selector(search_frame)
        self.create_search_label(search_frame)
        self.create_search_entry(search_frame)
        self.create_search_button(search_frame)
        self.create_excel_button(search_frame)
        self.create_refresh_button(search_frame)

    def create_menu_button(self, search_frame):
        fg_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"]
        hover_color = ctk.ThemeManager.theme["CTkButton"]["hover_color"]
        # Estilo moderno para el botón
        menu_button = ctk.CTkButton(
            search_frame, 
            text="☰", 
            width=30, 
            height=30, 
            command=self.show_menu,
            font=("Arial", 18),   # Fuente más moderna y grande
            fg_color=fg_color,  # Color de fondo personalizado
            hover_color=hover_color,  # Color al pasar el ratón
            corner_radius=10,  # Bordes redondeados
            border_width=0,  # Sin borde
            text_color="white"  # Color del texto
    )
    
        # Empaquetar el botón
        menu_button.pack(side="left", padx=5)

    def create_db_selector(self, search_frame):
        self.db_selector = ctk.CTkOptionMenu(
            search_frame, 
            values=["lenze9300.db", "lenze8200.db", "lenze8400.db"], 
            command=self.cambiar_base_datos
        )
        self.db_selector.pack(side="left", padx=5)

    def create_search_label(self, search_frame):
        search_label = ctk.CTkLabel(search_frame, text="Buscar:")
        search_label.pack(side="left", padx=5)

    def create_search_entry(self, search_frame):
        self.buscar_entry = ctk.CTkEntry(search_frame, width=200)
        self.buscar_entry.pack(side="left", padx=5)
        self.buscar_entry.bind("<Return>", lambda event: self.buscar_errores())

    def create_search_button(self, search_frame):
        buscar_btn = ctk.CTkButton(search_frame, text="Buscar", width=80, command=self.buscar_errores)
        buscar_btn.pack(side="left", padx=5)

    def create_excel_button(self, search_frame):
        cargar_excel_btn = ctk.CTkButton(search_frame, text="Excel", width=80, command=self.cargar_desde_excel)
        cargar_excel_btn.pack(side="left", padx=5)

    def create_refresh_button(self, search_frame):
        boton_refrescar = ctk.CTkButton(search_frame, text="Refrescar", width=80, command=self.cargar_todos)
        boton_refrescar.pack(side="left", padx=5, pady=5)

    def create_treeview(self):
        self.tree_frame = ctk.CTkFrame(self)
        self.tree_frame.pack(side="top", fill="both", expand=True, padx=5, pady=5)

        self.tree = ttk.Treeview(self.tree_frame, columns=("Num", "Pantalla", "Descripcion"), show='headings')
        self.tree.pack(side="left", fill="both", expand=True, padx=5, pady=5)

        self.tree.tag_configure('gris_claro', background='#f2f2f2')

        self.create_treeview_scrollbar()

        self.tree.heading("Num", text="Núm.")
        self.tree.heading("Pantalla", text="Pantalla")
        self.tree.heading("Descripcion", text="Descripción")
        self.tree.column("Num", width=80, stretch=False)
        self.tree.column("Pantalla", width=100, stretch=False)
        self.tree.column("Descripcion", width=250, stretch=True)

        self.tree.bind("<Double-1>", lambda event: ver_detalle(self, self.tree, self.conn))

    def create_treeview_scrollbar(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("Vertical.TScrollbar", gripcount=0, background="gray", troughcolor="gray", sliderrelief="flat", slidercolor="gray")

        self.scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.tree.yview, style="Vertical.TScrollbar")
        self.scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=self.scrollbar.set)

    def cambiar_base_datos(self, db_name):
        try:
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()

            self.conn = sqlite3.connect(db_name)
            self.cargar_todos()
            print(f"Conectado a la base de datos: {db_name}")
        except Exception as e:
            MessageBox.showerror("Error", f"No se pudo conectar a la base de datos: {e}")

    def cargar_desde_excel(self):
        file_path = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx")])
        if not file_path:
            return
        cargar_datos_desde_excel(self.conn, self.cargar_todos, file_path)

    def cargar_todos(self):
        cursor = self.conn.cursor()
        cursor.execute('SELECT id, num, pantalla, descripcion FROM errores')
        registros = cursor.fetchall()
        for i in self.tree.get_children():
            self.tree.delete(i)
        for idx, reg in enumerate(registros):
            id_reg, num, pantalla, descripcion = reg
            tag = 'gris_claro' if idx % 2 == 0 else ''
            # Aplicar negrita solo a la columna de "Pantalla"
            self.tree.insert("", "end", iid=str(id_reg), values=(num, pantalla, descripcion), tags=(tag,))
            self.tree.tag_configure(f'negrita_{id_reg}', font=("Arial", 10, "bold"))
        
            # Asignar el tag 'negrita' al valor de 'Pantalla' en cada fila
            self.tree.item(str(id_reg), tags=(tag, f'negrita_{id_reg}'))
        
            self.tree.yview_moveto(0)

    def editar_error_desde_detalle(self, ventana_detalle, error_id):
        ventana_detalle.destroy()  # Cerrar ventana de detalle

        error_data = obtener_error_por_id(self.conn, error_id)  # Obtener datos del error desde database.py
        if not error_data:
            MessageBox.showerror("Error", "No se pudo encontrar el error.")
            return

        self.editar_error(error_id)

    def editar_error_desde_detalle(self, ventana_detalle, error_id):
        """Cierra la ventana de detalles y abre la edición del error."""
        ventana_detalle.destroy()  # Cerrar la ventana de detalles

        error_data = obtener_error_por_id(self.conn, error_id)  # Obtener datos del error
        if not error_data:
            MessageBox.showerror("Error", "No se pudo encontrar el error.")
            return

        self.editar_error(error_id) 

    def show_menu(self):
        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label="Agregar", command=self.abrir_ventana_agregar)
        menu.add_command(label="Eliminar", command=self.eliminar_error)
        menu.post(self.winfo_rootx() + 35, self.winfo_rooty() + 55)

    def buscar_errores(self):
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
            tag = 'gris_claro' if idx % 2 == 0 else ''
            self.tree.insert("", "end", iid=str(id_reg), values=(num, pantalla, descripcion), tags=(tag,))
            self.tree.tag_configure(f'negrita_{id_reg}', font=("Arial", 10, "bold"))
            self.tree.item(str(id_reg), tags=(tag, f'negrita_{id_reg}'))
            

    def abrir_detalle(self, event):
        # Verificar si ya hay una ventana de detalle abierta
        if self.detalle_abierto:
            MessageBox.showinfo("Información", "Ya hay una ventana de detalle abierta. Cierra la ventana actual antes de abrir otra.")
            return

        selected_item = self.tree.selection()
        if selected_item:
            error_id = int(selected_item[0])
            self.detalle_abierto = True  # Marcar que la ventana de detalle está abierta
            ver_detalle(self, self.tree, self.conn, error_id, self.cerrar_detalle)

    def cerrar_detalle(self, ventana):
        # Esta función se llama cuando se cierra la ventana de detalle
        self.detalle_abierto = False  # Marcar que la ventana de detalle se ha cerrado
        ventana.destroy()
    
    def abrir_ventana_agregar(self):
        ventana = ctk.CTkToplevel(self.master)
        ventana.title("Agregar Nuevo Error")
        self.setup_new_error_window(ventana)
        self.create_window_fields(ventana)
        self.create_save_button(ventana)

    def setup_new_error_window(self, ventana):
        master_width = self.master.winfo_width()
        master_height = self.master.winfo_height()
        master_x = self.master.winfo_x()
        master_y = self.master.winfo_y()

        ventana_width = 400
        ventana_height = 350
        posicion_x = master_x + master_width + 200
        posicion_y = master_y
        ventana.geometry(f"{ventana_width}x{ventana_height}+{posicion_x}+{posicion_y}")
        ventana.lift()

    def create_window_fields(self, ventana):
        labels = ["Núm.", "Pantalla", "Descripción", "Causa", "Solución"]
        for idx, label_text in enumerate(labels):
            lbl = ctk.CTkLabel(ventana, text=label_text)
            lbl.grid(row=idx, column=0, padx=10, pady=5, sticky="e")

            if label_text in ["Causa", "Solución"]:
                text_box = ctk.CTkTextbox(ventana, width=250, height=80)
                text_box.grid(row=idx, column=1, padx=10, pady=5)
                self.entries[label_text] = text_box
            else:
                entry = ctk.CTkEntry(ventana, width=250)
                entry.grid(row=idx, column=1, padx=10, pady=5)
                self.entries[label_text] = entry

    def create_save_button(self, ventana):
        guardar_btn = ctk.CTkButton(ventana, text="Guardar", command=lambda: self.guardar_error(ventana))
        guardar_btn.grid(row=len(self.entries), column=0, columnspan=2, pady=10)

    def guardar_error(self, ventana):
        num = self.entries["Núm."].get()
        pantalla = self.entries["Pantalla"].get()
        descripcion = self.entries["Descripción"].get()
        causa = self.entries["Causa"].get("1.0", "end-1c")
        solucion = self.entries["Solución"].get("1.0", "end-1c")

        if not all([num, pantalla, descripcion, causa, solucion]):
            MessageBox.showwarning("Campos incompletos", "Por favor, completa todos los campos.")
            return

        self.insertar_en_base_datos(num, pantalla, descripcion, causa, solucion, self.conn)
        ventana.destroy()
        self.cargar_todos()

    def insertar_en_base_datos(self, num, pantalla, descripcion, causa, solucion, conn):
        try:
            cursor = conn.cursor()
            insertar_error(conn, num, pantalla, descripcion, causa, solucion)
            cursor.close()
            print("Error guardado exitosamente en la base de datos.")
        except Exception as e:
            print(f"Error al guardar en la base de datos: {e}")

    def eliminar_error(self):
        selected_item = self.tree.selection()
        if not selected_item:
            MessageBox.showwarning("Selección requerida", "Por favor, selecciona un error para eliminar.")
            return
        error_id = selected_item[0]
        confirmar = MessageBox.askyesno("Confirmar eliminación", "¿Estás seguro de que deseas eliminar este error?")
        if confirmar:
            try:
                eliminar_error(self.conn, error_id)
                self.cargar_todos()
            except Exception as e:
                MessageBox.showerror("Error", f"No se pudo eliminar el error.\n{str(e)}")

    def editar_error(self, error_id):
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
        num = self.entries["Núm."].get()
        pantalla = self.entries["Pantalla"].get()
        descripcion = self.entries["Descripción"].get()
        causa = self.entries["Causa"].get("1.0", "end-1c")
        solucion = self.entries["Solución"].get("1.0", "end-1c")

        if not all([num, pantalla, descripcion, causa, solucion]):
            return

        actualizar_error(self.conn, error_id, num, pantalla, descripcion, causa, solucion)

        # Actualizar los campos de la ventana con los datos nuevos
        self.entries["Núm."].delete(0, 'end')
        self.entries["Pantalla"].delete(0, 'end')
        self.entries["Descripción"].delete(0, 'end')
        self.entries["Causa"].delete('1.0', 'end')
        self.entries["Solución"].delete('1.0', 'end')

        # Asignar los nuevos datos
        self.entries["Núm."].insert(0, num)
        self.entries["Pantalla"].insert(0, pantalla)
        self.entries["Descripción"].insert(0, descripcion)
        self.entries["Causa"].insert('1.0', causa)
        self.entries["Solución"].insert('1.0', solucion)

        # Mostrar un mensaje de éxito si se desea
        messagebox.showinfo("Guardado", "Los cambios se han guardado correctamente")

        ventana.destroy()
        self.cargar_todos()


    