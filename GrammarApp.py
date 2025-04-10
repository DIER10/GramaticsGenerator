import tkinter as tk
from tkinter import filedialog, ttk, messagebox, scrolledtext
from GrammarLogic import GrammarLogicNLTK
from Constants import MAX_GENERATED_STRINGS, EPSILON
from nltk import CFG, Tree

class GrammarApp:
    def __init__(self, master):
        self.master = master
        master.title("Generador de Gramáticas") # Título actualizado
        master.geometry("800x700")

        # Usar la nueva clase lógica
        self.logic = GrammarLogicNLTK()
        self.production_rows_widgets = []

        # --- Estilos (sin cambios) ---
        style = ttk.Style()
        # ... (configuración de estilos igual que antes) ...

        # --- Layout Principal (sin cambios) ---
        main_frame = ttk.Frame(master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Sección Definición Gramática ---
        grammar_frame = ttk.LabelFrame(main_frame, text="1. Definición de la Gramática", padding="10")
        grammar_frame.pack(fill=tk.X, pady=5)

        # Inputs S, T, NT (igual que antes)
        # ... (Labels y Entries para S, T, NT) ...
        ttk.Label(grammar_frame, text="Símbolo Inicial (S):").grid(row=0, column=0, sticky=tk.W)
        self.start_symbol_var = tk.StringVar()
        self.start_symbol_entry = ttk.Entry(grammar_frame, textvariable=self.start_symbol_var, width=15, font=('Helvetica', 10))
        self.start_symbol_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(grammar_frame, text="Terminales (T) (e.g., a,b,c):").grid(row=1, column=0, sticky=tk.W)
        self.terminals_var = tk.StringVar()
        self.terminals_entry = ttk.Entry(grammar_frame, textvariable=self.terminals_var, width=50, font=('Helvetica', 10))
        self.terminals_entry.grid(row=1, column=1, columnspan=3, sticky=tk.W+tk.E)

        ttk.Label(grammar_frame, text="No Terminales (NT) (e.g., S,A,B):").grid(row=2, column=0, sticky=tk.W)
        self.non_terminals_var = tk.StringVar()
        self.non_terminals_entry = ttk.Entry(grammar_frame, textvariable=self.non_terminals_var, width=50, font=('Helvetica', 10))
        self.non_terminals_entry.grid(row=2, column=1, columnspan=3, sticky=tk.W+tk.E)


        # Frame para Producciones con botones (igual que antes, incluyendo Cargar/Guardar)
        prod_header_frame = ttk.Frame(grammar_frame)
        prod_header_frame.grid(row=3, column=0, columnspan=4, sticky=tk.W+tk.E, pady=(10,0))
        ttk.Label(prod_header_frame, text="Producciones (P) (RHS vacío = ε):").pack(side=tk.LEFT) # Aclarar epsilon

        self.add_prod_button = ttk.Button(prod_header_frame, text="Añadir", command=self.add_production_row)
        self.add_prod_button.pack(side=tk.RIGHT, padx=(5,0))

        self.save_grammar_button = ttk.Button(prod_header_frame, text="Guardar", command=self.save_grammar_action)
        self.save_grammar_button.pack(side=tk.RIGHT, padx=(0, 5))

        self.load_grammar_button = ttk.Button(prod_header_frame, text="Cargar", command=self.load_grammar_action)
        self.load_grammar_button.pack(side=tk.RIGHT, padx=(0, 5))


        # Canvas y Frame para producciones (igual que antes)
        self.productions_canvas = tk.Canvas(grammar_frame, borderwidth=0, height=150)
        self.productions_frame = ttk.Frame(self.productions_canvas)
        self.productions_scrollbar = ttk.Scrollbar(grammar_frame, orient="vertical", command=self.productions_canvas.yview)
        self.productions_canvas.configure(yscrollcommand=self.productions_scrollbar.set)
        self.productions_canvas.grid(row=4, column=0, columnspan=4, sticky="nsew", pady=5)
        self.productions_scrollbar.grid(row=4, column=4, sticky="ns")
        self.productions_canvas_window = self.productions_canvas.create_window((0, 0), window=self.productions_frame, anchor="nw")
        # ... (binds para el canvas igual que antes) ...
        def _configure_canvas(event):
             canvas_width = event.width
             self.productions_canvas.itemconfig(self.productions_canvas_window, width=canvas_width)
             self.productions_canvas.configure(scrollregion=self.productions_canvas.bbox("all"))
        self.productions_frame.bind("<Configure>", lambda e: self.productions_canvas.configure(scrollregion=self.productions_canvas.bbox("all")))
        self.productions_canvas.bind('<Configure>', _configure_canvas)
        grammar_frame.grid_rowconfigure(4, weight=1)
        grammar_frame.grid_columnconfigure(1, weight=1)
        self.add_production_row() # Fila inicial

        # --- Sección Validación Tipo --- (igual que antes)
        type_frame = ttk.LabelFrame(main_frame, text="2. Tipo de Gramática", padding="10")
        type_frame.pack(fill=tk.X, pady=5)
        self.validate_type_button = ttk.Button(type_frame, text="Validar Tipo", command=self.validate_grammar_type_action)
        self.validate_type_button.pack(side=tk.LEFT, padx=5)
        self.grammar_type_label = ttk.Label(type_frame, text="Tipo: (Presione validar)", style="Result.TLabel")
        self.grammar_type_label.pack(side=tk.LEFT, padx=5)

        # --- Sección Validación Cadena --- (igual que antes)
        validation_frame = ttk.LabelFrame(main_frame, text="3. Validación de Cadena", padding="10")
        validation_frame.pack(fill=tk.X, pady=5)
        ttk.Label(validation_frame, text="Cadena a validar:").pack(side=tk.LEFT, padx=5)
        self.string_to_validate_var = tk.StringVar()
        self.string_to_validate_entry = ttk.Entry(validation_frame, textvariable=self.string_to_validate_var, width=30, font=('Helvetica', 10))
        self.string_to_validate_entry.pack(side=tk.LEFT, padx=5)
        self.validate_string_button = ttk.Button(validation_frame, text="Validar Cadena", command=self.validate_string_action)
        self.validate_string_button.pack(side=tk.LEFT, padx=5)
        self.validation_result_label = ttk.Label(validation_frame, text="Resultado: (Ingrese cadena y valide)", style="Result.TLabel")
        self.validation_result_label.pack(side=tk.LEFT, padx=(10,0))

        # --- Sección Generación Cadenas --- (igual que antes)
        generation_frame = ttk.LabelFrame(main_frame, text="4. Generación de Cadenas", padding="10")
        generation_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        gen_options_frame = ttk.Frame(generation_frame)
        gen_options_frame.pack(fill=tk.X)
        # ... (widgets de generación igual que antes) ...
        ttk.Label(gen_options_frame, text="Max Cadenas:").pack(side=tk.LEFT, padx=5)
        self.generation_n_var = tk.StringVar(value=str(MAX_GENERATED_STRINGS))
        self.generation_n_entry = ttk.Entry(gen_options_frame, textvariable=self.generation_n_var, width=5, font=('Helvetica', 10))
        self.generation_n_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(gen_options_frame, text="Max Profundidad:").pack(side=tk.LEFT, padx=5)
        self.generation_depth_var = tk.StringVar(value="7") # Añadir control profundidad NLTK
        self.generation_depth_entry = ttk.Entry(gen_options_frame, textvariable=self.generation_depth_var, width=5, font=('Helvetica', 10))
        self.generation_depth_entry.pack(side=tk.LEFT, padx=5)

        self.generate_strings_button = ttk.Button(gen_options_frame, text="Generar Cadenas", command=self.generate_strings_action)
        self.generate_strings_button.pack(side=tk.LEFT, padx=5)
        self.generation_count_label = ttk.Label(generation_frame, text="Cadenas generadas: 0", style="Result.TLabel")
        self.generation_count_label.pack(anchor=tk.W, padx=5, pady=(5,0))
        self.generated_strings_text = scrolledtext.ScrolledText(generation_frame, height=6, width=70, wrap=tk.WORD, state=tk.DISABLED, font=('Courier New', 10))
        self.generated_strings_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)


    # --- Métodos de la App ---

    def add_production_row(self):
        # (Sin cambios)
        row_frame = ttk.Frame(self.productions_frame)
        row_frame.pack(fill=tk.X, pady=1) # pady añade espacio entre filas

        lhs_entry = ttk.Entry(row_frame, width=10, font=('Helvetica', 10)) # LHS editable
        lhs_entry.pack(side=tk.LEFT, padx=(0, 0))

        ttk.Label(row_frame, text=" ->").pack(side=tk.LEFT, padx=(0, 5))

        rhs_entry = ttk.Entry(row_frame, font=('Helvetica', 10))
        rhs_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))

        remove_button = ttk.Button(row_frame, text="X", width=2, style="Toolbutton",
                                  command=lambda rf=row_frame: self.remove_production_row(rf))
        remove_button.pack(side=tk.RIGHT)

        row_data = {'frame': row_frame, 'lhs': lhs_entry, 'rhs': rhs_entry}
        self.production_rows_widgets.append(row_data)

        self.productions_frame.update_idletasks()
        self.productions_canvas.configure(scrollregion=self.productions_canvas.bbox("all"))
        self.productions_canvas.yview_moveto(1)


    def remove_production_row(self, row_frame_to_remove):
        # (Sin cambios)
        index_to_remove = -1
        for i, row_data in enumerate(self.production_rows_widgets):
            if row_data['frame'] == row_frame_to_remove:
                index_to_remove = i
                break
        if index_to_remove != -1:
            self.production_rows_widgets[index_to_remove]['frame'].destroy()
            del self.production_rows_widgets[index_to_remove]
            self.productions_frame.update_idletasks()
            self.productions_canvas.configure(scrollregion=self.productions_canvas.bbox("all"))

    def clear_production_rows(self):
         # (Sin cambios respecto a la versión anterior con Cargar/Guardar)
         for i in range(len(self.production_rows_widgets) - 1, -1, -1):
            row_data = self.production_rows_widgets[i]
            row_data['frame'].destroy()
            del self.production_rows_widgets[i]
         self.productions_frame.update_idletasks()
         if self.productions_frame.winfo_exists():
             self.productions_canvas.configure(scrollregion=self.productions_canvas.bbox("all"))


    def _collect_productions(self):
        # (Sin cambios)
        productions_list = []
        for row_data in self.production_rows_widgets:
            lhs_val = row_data['lhs'].get()
            rhs_val = row_data['rhs'].get()
            # Añadir incluso si RHS está vacío (para epsilon)
            if lhs_val.strip():
                 productions_list.append((lhs_val, rhs_val))
        return productions_list

    def _process_grammar_input(self):
        """ Recoge input de la UI y llama a logic.set_grammar """
        start_symbol = self.start_symbol_var.get()
        terminals_str = self.terminals_var.get()
        non_terminals_str = self.non_terminals_var.get()
        productions_list = self._collect_productions()

        # Limpiar resultados anteriores
        self.grammar_type_label.config(text="Tipo: Validando...", style="Result.TLabel")
        self.validation_result_label.config(text="Resultado: ...", style="Result.TLabel")
        self.master.update_idletasks()

        errors = self.logic.set_grammar(start_symbol, terminals_str, non_terminals_str, productions_list)

        if errors:
            error_str = "\n".join(errors)
            is_fatal = any("Error:" in e for e in errors)
            if is_fatal:
                 messagebox.showerror("Error de Gramática", error_str, parent=self.master)
                 self.grammar_type_label.config(text="Tipo: Error", style="Error.TLabel")
                 return False # Hubo error fatal
            else: # Solo advertencias
                 messagebox.showwarning("Advertencia de Gramática", error_str, parent=self.master)
                 # Continuar, pero el tipo será determinado por logic.determine...
                 # return True # O False si advertencias deben bloquear
                 return True # Permitir continuar con advertencias

        return True # Gramática parseada OK por la lógica (puede que NLTK fallara internamente)


    def validate_grammar_type_action(self):
        """ Acción botón Validar Tipo """
        if not self._process_grammar_input():
             # Si hubo errores fatales al procesar input, no continuar
              if "Error" not in self.grammar_type_label.cget("text"):
                   self.grammar_type_label.config(text="Tipo: Error definición", style="Error.TLabel")
              return

        # Si _process_grammar_input fue True, pedir el tipo a la lógica
        # (set_grammar ya debería haber llamado a determine_grammar_type)
        grammar_type_result = self.logic.grammar_type # Obtener el tipo ya calculado

        if not grammar_type_result or "Error" in grammar_type_result:
            # Si hubo error en NLTK o en la determinación manual T3
            error_msg = grammar_type_result if grammar_type_result else "Error desconocido"
            self.grammar_type_label.config(text=f"Tipo: {error_msg}", style="Error.TLabel")
        else:
            self.grammar_type_label.config(text=f"Tipo: {grammar_type_result}", style="Result.TLabel")


    def validate_string_action(self):
        """ Acción botón Validar Cadena usando NLTK """
        # 1. Asegurarse que la gramática esté procesada
        if not self.logic.cfg or not self.logic.parser:
            # Intentar procesarla ahora
            if not self._process_grammar_input():
                self.validation_result_label.config(text="Resultado: Corrija la gramática", style="Error.TLabel")
                return
            # Si _process_grammar_input fue OK, pero aún no hay parser (error NLTK interno)
            if not self.logic.cfg or not self.logic.parser:
                 self.validation_result_label.config(text="Resultado: Error interno procesando gramática", style="Error.TLabel")
                 return

        # 2. Validar la cadena
        input_string = self.string_to_validate_var.get()
        self.validation_result_label.config(text="Resultado: Validando...", style="Result.TLabel")
        self.master.update_idletasks()

        try:
            belongs, parse_trees = self.logic.validate_string(input_string+EPSILON)
            print(belongs)

            if belongs:
                self.validation_result_label.config(text=f"Resultado: Cadena '{input_string}' PERTENECE", style="Success.TLabel")
                # Mostrar el primer árbol de derivación encontrado
                if parse_trees:
                     # Usar el método de formato de la lógica
                     tree_output = self.logic.get_derivation_tree_string(parse_trees[0])
                     # Mostrar en la ventana (adaptada)
                     self.show_derivation_tree_window(input_string, tree_output, len(parse_trees))
                else:
                     # Esto no debería pasar si belongs es True, pero por si acaso
                     messagebox.showwarning("Derivación", "La cadena pertenece, pero no se obtuvo árbol de parseo.", parent=self.master)

            else:
                 self.validation_result_label.config(text=f"Resultado: Cadena '{input_string}' NO PERTENECE", style="Error.TLabel")

        except ValueError as e: # Errores de tokenización, etc.
             self.validation_result_label.config(text=f"Error validación: {e}", style="Error.TLabel")
        except RuntimeError as e: # Errores inesperados del parser
             self.validation_result_label.config(text=f"Error NLTK: {e}", style="Error.TLabel")
             messagebox.showerror("Error NLTK", f"Ocurrió un error en el parser NLTK:\n{e}", parent=self.master)
        except Exception as e:
             self.validation_result_label.config(text=f"Error inesperado: {e}", style="Error.TLabel")
             import traceback
             traceback.print_exc()
             messagebox.showerror("Error Inesperado", f"Ocurrió un error:\n{e}", parent=self.master)


    def show_derivation_tree_window(self, input_string, tree_output, tree_count):
        """ Muestra el árbol de derivación (parse tree) de NLTK en texto. 
            Ejemplo de formato (aaa): [Tree('S', ['a', Tree('S', ['a', Tree('S', ['a', Tree('S', ['ε'])])])])]
        """
        deriv_win = tk.Toplevel(self.master)
        title = f"Árbol de Derivación para: '{input_string}'"

        if tree_count > 1:
            title += f" (1 de {tree_count} encontrados - Gramática Ambigua)"
        deriv_win.title(title)
        deriv_win.geometry("500x350") # Ajustar tamaño si es necesario

        frame = ttk.Frame(deriv_win, padding="10")
        frame.pack(expand=True, fill=tk.BOTH)

        lbl = ttk.Label(frame, text=f"Árbol de Derivación para '{input_string}':", font=('Helvetica', 11, 'bold'))
        lbl.pack(pady=(0, 5))

        text_area = scrolledtext.ScrolledText(frame, wrap=tk.NONE, font=('Courier New', 10), height=15) # wrap=NONE para árboles
        text_area.pack(expand=True, fill=tk.BOTH, padx=5, pady=5)

        text_area.insert(tk.END, tree_output)
        text_area.config(state=tk.DISABLED)

        close_button = ttk.Button(frame, text="Cerrar", command=deriv_win.destroy)
        close_button.pack(pady=(10, 0))

        deriv_win.grab_set()
        deriv_win.transient(self.master)
        self.master.wait_window(deriv_win)


    def generate_strings_action(self):
        """ Acción botón Generar Cadenas usando NLTK """
        # 1. Asegurarse que la gramática esté procesada
        if not self.logic.cfg:
            if not self._process_grammar_input():
                self.generated_strings_text.config(state=tk.NORMAL); self.generated_strings_text.delete(1.0, tk.END)
                self.generated_strings_text.insert(tk.END, "Corrija la gramática primero."); self.generated_strings_text.config(state=tk.DISABLED)
                self.generation_count_label.config(text="Generadas: Error", style="Error.TLabel")
                return
            if not self.logic.cfg:
                 self.generated_strings_text.config(state=tk.NORMAL); self.generated_strings_text.delete(1.0, tk.END)
                 self.generated_strings_text.insert(tk.END, "Error interno procesando gramática."); self.generated_strings_text.config(state=tk.DISABLED)
                 self.generation_count_label.config(text="Generadas: Error", style="Error.TLabel")
                 return

        # 2. Obtener parámetros N y Profundidad
        try:
            n_str = self.generation_n_var.get()
            n = int(n_str)
            depth_str = self.generation_depth_var.get()
            depth = int(depth_str)
            if n <= 0 or depth <= 0: raise ValueError("N y Profundidad deben ser > 0.")
        except ValueError:
             messagebox.showerror("Error Parámetros", "Max Cadenas (N) y Max Profundidad deben ser enteros positivos.", parent=self.master)
             return

        # 3. Generar
        self.generated_strings_text.config(state=tk.NORMAL)
        self.generated_strings_text.delete(1.0, tk.END)
        self.generated_strings_text.insert(tk.END, "Generando...")
        self.generated_strings_text.config(state=tk.DISABLED)
        self.generation_count_label.config(text="Generadas: Calculando...", style="Result.TLabel")
        self.master.update_idletasks()

        try:
             # Actualizar MAX_GENERATED_STRINGS si se cambió en la UI
             # (Nota: NLTK generate() tiene su propio parámetro 'n' para límite de *intentos*)
             global MAX_GENERATED_STRINGS
             MAX_GENERATED_STRINGS = n # Usar valor de la UI

             generated = self.logic.generate_random_strings(n=n, max_depth=depth)

             self.generated_strings_text.config(state=tk.NORMAL)
             self.generated_strings_text.delete(1.0, tk.END)
             if generated:
                 self.generated_strings_text.insert(tk.END, "\n".join(generated))
                 self.generation_count_label.config(text=f"Generadas: {len(generated)}", style="Result.TLabel")
             else:
                  self.generated_strings_text.insert(tk.END, "(Ninguna encontrada con los límites dados)")
                  self.generation_count_label.config(text="Generadas: 0", style="Result.TLabel")
             self.generated_strings_text.config(state=tk.DISABLED)

        except ValueError as e: # Error en lógica de generación
             self.generated_strings_text.config(state=tk.NORMAL); self.generated_strings_text.delete(1.0, tk.END)
             self.generated_strings_text.insert(tk.END, f"Error: {e}"); self.generated_strings_text.config(state=tk.DISABLED)
             self.generation_count_label.config(text="Generadas: Error", style="Error.TLabel")
        except Exception as e:
             self.generated_strings_text.config(state=tk.NORMAL); self.generated_strings_text.delete(1.0, tk.END)
             self.generated_strings_text.insert(tk.END, f"Error inesperado: {e}"); self.generated_strings_text.config(state=tk.DISABLED)
             self.generation_count_label.config(text="Generadas: Error", style="Error.TLabel")
             import traceback
             traceback.print_exc()
             messagebox.showerror("Error de Generación", f"Ocurrió un error inesperado:\n{e}", parent=self.master)


    def save_grammar_action(self):
        """ Guarda la gramática en formato string compatible con NLTK CFG. """
        # Re-procesar la gramática actual para asegurar que logic.grammar_str esté actualizado
        # y obtener la representación string validada por NLTK si es posible.
        if not self._process_grammar_input():
             messagebox.showerror("Guardar Gramática", "La gramática contiene errores y no puede ser guardada.", parent=self.master)
             return
        if not self.logic.grammar_str:
             messagebox.showerror("Guardar Gramática", "No se pudo generar la representación de la gramática (posible error interno).", parent=self.master)
             return

        # Pedir archivo para guardar (usaremos extensión .cfg por convención NLTK)
        file_path = filedialog.asksaveasfilename(
            title="Guardar Gramática como CFG",
            defaultextension=".cfg", # Extensión común para gramáticas
            filetypes=[("CFG files", "*.cfg"), ("Text files", "*.txt"), ("All files", "*.*")],
            parent=self.master
        )

        if file_path:
            try:
                # Guardar directamente el string que usa NLTK
                with open(file_path, 'w', encoding='utf-8') as f:
                    # Podríamos añadir S, T, NT como comentarios al inicio
                    f.write(f"# Start Symbol: {self.start_symbol_var.get()}\n")
                    f.write(f"# Terminals: {self.terminals_var.get()}\n")
                    f.write(f"# NonTerminals: {self.non_terminals_var.get()}\n")
                    f.write("# --- Productions --- \n")
                    f.write(self.logic.grammar_str) # Guardar el string parseable por NLTK
                messagebox.showinfo("Guardar Gramática", f"Gramática guardada exitosamente en:\n{file_path}", parent=self.master)
            except Exception as e:
                messagebox.showerror("Error al Guardar", f"No se pudo guardar la gramática:\n{e}", parent=self.master)


    def load_grammar_action(self):
        """ Carga una gramática desde un archivo .cfg/.txt """
        file_path = filedialog.askopenfilename(
            title="Abrir Archivo de Gramática (.cfg, .txt)",
            filetypes=[("CFG files", "*.cfg"), ("Text files", "*.txt"), ("All files", "*.*")],
            parent=self.master
        )
        if not file_path: return

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Extraer S, T, NT de comentarios (si existen) y producciones
            start_symbol = ""
            terminals = ""
            non_terminals = ""
            production_lines = []

            for line in lines:
                line = line.strip()
                if not line: continue

                if line.startswith("# Start Symbol:"):
                    start_symbol = line.split(":", 1)[1].strip()
                elif line.startswith("# Terminals:"):
                    terminals = line.split(":", 1)[1].strip()
                elif line.startswith("# NonTerminals:"):
                     non_terminals = line.split(":", 1)[1].strip()
                elif line == "# --- Productions ---":
                     in_productions = True
                elif line.startswith("#"):
                     continue # Ignorar otros comentarios
                elif '->' in line: # Asumir que es una línea de producción
                     production_lines.append(line)
                # Si no empieza con # y no tiene ->, podría ser un error o parte de una gramática multilínea simple
                # Para simplificar, solo cargamos líneas con -> como producciones ahora

            if not production_lines:
                 raise ValueError("No se encontraron líneas de producción (con '->') en el archivo.")

            # Intentar parsear con NLTK para obtener S, T, NT si no estaban en comentarios
            temp_cfg_str = "\n".join(production_lines)
            try:
                 temp_cfg = CFG.fromstring(temp_cfg_str)
                 # Si S, T, NT no se leyeron de comentarios, inferirlos de NLTK
                 if not start_symbol: start_symbol = str(temp_cfg.start())
                 # Inferir T y NT puede ser menos preciso que leerlos del comentario
                 # Pero es mejor que nada si los comentarios no están
                 if not terminals:
                      # Obtener todos los símbolos RHS que son strings
                      inferred_terminals = set()
                      for p in temp_cfg.productions():
                           for sym in p.rhs():
                                if isinstance(sym, str): inferred_terminals.add(sym)
                      terminals = ",".join(sorted(list(inferred_terminals)))
                 if not non_terminals:
                       inferred_non_terminals = {str(nt) for nt in temp_cfg.nonterminals()}
                       non_terminals = ",".join(sorted(list(inferred_non_terminals)))

            except Exception as parse_error:
                 raise ValueError(f"Error al pre-parsear producciones con NLTK: {parse_error}")


            # Actualizar UI
            self.start_symbol_var.set(start_symbol)
            self.terminals_var.set(terminals)
            self.non_terminals_var.set(non_terminals)

            self.clear_production_rows()

            # Añadir producciones a la UI (parseando desde las líneas cargadas)
            if not production_lines:
                 self.add_production_row()
            else:
                 for prod_line in production_lines:
                      parts = prod_line.split("->")
                      if len(parts) == 2:
                           lhs = parts[0].strip()
                           rhs_str_nltk = parts[1].strip()
                           # Convertir de formato NLTK (ej 'a' B 'c') a formato UI (ej aBc)
                           rhs_ui = rhs_str_nltk.replace("'", "") # Quitar comillas de terminales
                           rhs_ui = rhs_ui.replace(" ", "") # Quitar espacios entre símbolos
                           
                           self.add_production_row()
                           new_row = self.production_rows_widgets[-1]
                           new_row['lhs'].insert(0, lhs)
                           new_row['rhs'].insert(0, rhs_ui)
                      else:
                           print(f"WARN: Ignorando línea de producción mal formada: {prod_line}")


            # Limpiar resultados
            self.grammar_type_label.config(text="Tipo: (Presione validar)", style="Result.TLabel")
            self.validation_result_label.config(text="Resultado: (Ingrese cadena y valide)", style="Result.TLabel")
            # ... (limpiar area de generación) ...

            messagebox.showinfo("Cargar Gramática", "Gramática cargada. Valide el tipo si es necesario.", parent=self.master)


        except FileNotFoundError:
            messagebox.showerror("Error al Cargar", f"No se encontró el archivo:\n{file_path}", parent=self.master)
        except ValueError as e:
             messagebox.showerror("Error al Cargar", f"Error en el formato del archivo:\n{e}", parent=self.master)
        except Exception as e:
            messagebox.showerror("Error Inesperado", f"Ocurrió un error al cargar:\n{e}", parent=self.master)
            import traceback
            traceback.print_exc()

