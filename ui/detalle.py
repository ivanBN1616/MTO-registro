import customtkinter as ctk
from tkinter import messagebox

def ver_detalle(parent, tree, conn):
    """Muestra una ventana con los detalles del error seleccionado y permite editar en la misma ventana."""
    try:
        # Verificar si se seleccionó un ítem
        item = tree.selection()
        if not item:
            return  # Si no hay selección, salir de la función
        error_id = int(item[0])

        cursor = conn.cursor()
        cursor.execute('SELECT * FROM errores WHERE id = ?', (error_id,))
        detalle = cursor.fetchone()

        if not detalle:
            return  # Si no se encuentra el detalle, salir de la función

        # Crear una nueva ventana para los detalles
        detalle_win = ctk.CTkToplevel(parent)
        detalle_win.title("Detalle del Error")

        # Establecer tamaño inicial y color de fondo
        detalle_win.geometry("700x400")
        detalle_win.configure(bg="#f5f5f5")  # Fondo gris claro

        # Etiquetas para los campos
        labels = ["Núm.", "Pantalla", "Descripción", "Causa", "Solución"]

        # Crear un frame principal que contenga todos los detalles
        main_frame = ctk.CTkFrame(detalle_win, bg_color="#f5f5f5")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Crear frames separados para cada categoría
        frames = {}
        fields = {}  # Aquí almacenaremos las entradas y etiquetas
        for label in labels:
            frame = ctk.CTkFrame(main_frame, bg_color="#f5f5f5")
            frame.pack(fill="x", pady=5, padx=10)
            frames[label] = frame

        # Crear las etiquetas y campos (labels y Entry)
        for idx, label in enumerate(labels):
            field_label = ctk.CTkLabel(frames[label], text=f"{label}:", font=("Arial", 12, "bold"))
            field_label.pack(side="left", padx=10)

            # Mostrar el valor de cada campo en una etiqueta
            if label == "Núm.":
                field_value = ctk.CTkLabel(frames[label], text=detalle[1], font=("Arial", 12), anchor="w", wraplength=600)
            else:
                field_value = ctk.CTkLabel(frames[label], text=detalle[idx + 1], font=("Arial", 12), anchor="w", wraplength=600)

            field_value.pack(side="left", padx=10)
            fields[label] = field_value

        # Función para activar la edición de los campos
        def habilitar_editar():
            """Habilita la edición de los campos en la ventana actual."""
            # Cambiar el texto del botón de "Editar" a "Guardar"
            btn_editar.configure(text="Guardar", command=guardar_cambios)

            # Cambiar las etiquetas a entradas
            for label in labels:
                current_field = fields[label]
                current_value = current_field.cget("text")
                current_field.destroy()  # Eliminar la etiqueta

                if label == "Núm.":
                    new_field = ctk.CTkEntry(frames[label], font=("Arial", 12), width=500)
                    new_field.insert(0, current_value)  # Insertar el valor actual
                    new_field.pack(side="left", padx=10)
                else:
                    new_field = ctk.CTkEntry(frames[label], font=("Arial", 12), width=500)
                    new_field.insert(0, current_value)  # Insertar el valor actual
                    new_field.pack(side="left", padx=10)

                fields[label] = new_field  # Actualizar el campo

        # Función para guardar los cambios
        def guardar_cambios():
            try:
                # Obtener los nuevos valores de los campos editados
                nuevos_valores = [fields[label].get() for label in labels]

                # Actualizar la base de datos
                cursor.execute('''
                    UPDATE errores
                    SET num = ?, pantalla = ?, descripcion = ?, causa = ?, solucion = ?
                    WHERE id = ?
                ''', (nuevos_valores[0], nuevos_valores[1], nuevos_valores[2], nuevos_valores[3], nuevos_valores[4], error_id))
                conn.commit()

                # Mostrar mensaje de éxito y cerrar la ventana de detalles
                messagebox.showinfo("Éxito", "Los cambios se han guardado correctamente.")
                detalle_win.destroy()  # Cerrar la ventana de detalles

            except Exception as e:
                messagebox.showerror("Error", f"Hubo un error al guardar los cambios: {e}")

        # Botón para editar o guardar los cambios
        btn_editar = ctk.CTkButton(main_frame, text="Editar", width=100, height=40, command=habilitar_editar)
        btn_editar.pack(pady=10)

        # Botón de cerrar la ventana de detalles
        cerrar_btn = ctk.CTkButton(main_frame, text="Cerrar", command=detalle_win.destroy, width=100, height=40)
        cerrar_btn.pack(pady=20)

        # Asegurar que la ventana de detalles esté al frente
        detalle_win.lift()  # Asegura que la ventana emergente esté al frente
        detalle_win.focus_set()  # Focaliza la ventana emergente

        # Permitir que la ventana se redimensione (habilita la maximización)
        detalle_win.resizable(True, True)  # Permitir redimensionar la ventana

        # Actualizar la ventana para ajustarse al contenido
        detalle_win.update_idletasks()

    except Exception as e:
        print(f"Error al mostrar detalles: {e}")
        # Mostrar error en una ventana emergente
        messagebox.showerror("Error", f"Hubo un error al cargar los detalles del error: {e}")
