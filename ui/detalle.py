import customtkinter as ctk

def ver_detalle(parent, tree, conn):
    """Muestra una ventana con los detalles del error seleccionado."""
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
        for label in labels:
            frame = ctk.CTkFrame(main_frame, bg_color="#f5f5f5")
            frame.pack(fill="x", pady=5, padx=10)
            frames[label] = frame

        # Crear las etiquetas y valores en cada frame
        for idx, label in enumerate(labels):
            field_label = ctk.CTkLabel(frames[label], text=f"{label}:", font=("Arial", 12, "bold"))
            field_label.pack(side="left", padx=10)

            # Mostrar el valor de cada campo en una etiqueta
            field_value = ctk.CTkLabel(frames[label], text=detalle[idx+1], font=("Arial", 12), anchor="w", wraplength=600)
            field_value.pack(side="left", padx=10)

            # Si el campo es "Causa" o "Solución", aseguramos que el texto largo se ajuste correctamente
            if label in ["Causa", "Solución"]:
                field_value.configure(wraplength=600)  # Ajustar el largo máximo de cada línea

        # Botón de cerrar con estilo
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
        ctk.CTkMessageBox.showerror("Error", f"Hubo un error al cargar los detalles del error: {e}")
