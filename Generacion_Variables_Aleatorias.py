import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.patches as patches
import numpy as np
from scipy.stats import norm, expon, binom, poisson, geom
import math
import re

class MathTextWidget:
    """Widget simplificado para mostrar texto con fórmulas matemáticas"""
    
    def __init__(self, parent, **kwargs):
        self.parent = parent
        self.bg_color = kwargs.get('bg', '#f8f8f8')
        self.fg_color = kwargs.get('fg', '#37474f')
        self.font_family = kwargs.get('font', ('Courier New', 10))
        
        # Crear un frame principal
        self.frame = ttk.Frame(parent)
        
        # Crear un Text widget scrollable para mostrar todo el contenido
        self.text_widget = scrolledtext.ScrolledText(
            self.frame,
            wrap=tk.WORD,
            font=self.font_family,
            bg=self.bg_color,
            fg=self.fg_color,
            relief=tk.FLAT,
            state=tk.NORMAL
        )
        self.text_widget.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para diferentes estilos
        self.text_widget.tag_configure("formula", font=('Times New Roman', 12, 'italic'), foreground='#2E8B57')
        self.text_widget.tag_configure("bold", font=('Courier New', 10, 'bold'))
        self.text_widget.tag_configure("normal", font=self.font_family)
        
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
        
    def delete(self, start, end):
        self.text_widget.delete(start, end)
    
    def insert(self, index, text):
        """Insertar texto procesando las fórmulas matemáticas para mostrarlas de forma más legible"""
        # Procesar el texto para mejorar la visualización de fórmulas
        processed_text = self.process_math_text(text)
        
        # Insertar el texto procesado
        lines = processed_text.split('\n')
        for line in lines:
            if '$' in line:
                # Procesar línea con fórmulas
                parts = self.split_formula_line(line)
                for part, is_formula in parts:
                    if is_formula:
                        # Insertar la fórmula con estilo especial
                        self.text_widget.insert(index, part, "formula")
                    else:
                        # Insertar texto normal
                        self.text_widget.insert(index, part, "normal")
                self.text_widget.insert(index, '\n', "normal")
            else:
                # Línea sin fórmulas
                self.text_widget.insert(index, line + '\n', "normal")
    
    def split_formula_line(self, line):
        """Dividir una línea en partes de texto normal y fórmulas"""
        parts = []
        current_pos = 0
        
        while current_pos < len(line):
            # Buscar el siguiente $
            dollar_pos = line.find('$', current_pos)
            
            if dollar_pos == -1:
                # No hay más fórmulas, agregar el resto como texto normal
                if current_pos < len(line):
                    parts.append((line[current_pos:], False))
                break
            
            # Agregar texto antes de la fórmula
            if dollar_pos > current_pos:
                parts.append((line[current_pos:dollar_pos], False))
            
            # Buscar el $ de cierre
            end_dollar_pos = line.find('$', dollar_pos + 1)
            if end_dollar_pos == -1:
                # No hay $ de cierre, tratar como texto normal
                parts.append((line[dollar_pos:], False))
                break
            
            # Extraer y procesar la fórmula
            formula = line[dollar_pos+1:end_dollar_pos]
            processed_formula = self.format_formula(formula)
            parts.append((processed_formula, True))
            
            current_pos = end_dollar_pos + 1
        
        return parts
    
    def format_formula(self, formula):
        """Convertir LaTeX a una representación más legible"""
        # Reemplazos para hacer las fórmulas más legibles
        replacements = {
            r'\\frac\{([^}]+)\}\{([^}]+)\}': r'(\1)/(\2)',
            r'\\sqrt\{([^}]+)\}': r'√(\1)',
            r'\\ln': 'ln',
            r'\\log': 'log',
            r'\\pi': 'π',
            r'\\mu': 'μ',
            r'\\sigma': 'σ',
            r'\\lambda': 'λ',
            r'\\alpha': 'α',
            r'\\beta': 'β',
            r'\\gamma': 'γ',
            r'\\theta': 'θ',
            r'\\leq': '≤',
            r'\\geq': '≥',
            r'\\le': '≤',
            r'\\ge': '≥',
            r'\\times': '×',
            r'\\cdot': '·',
            r'\\infty': '∞',
            r'\\sum': 'Σ',
            r'\\int': '∫',
            r'\\lfloor': '⌊',
            r'\\rfloor': '⌋',
            r'\\lceil': '⌈',
            r'\\rceil': '⌉',
            r'\\bmod': ' mod ',
            r'\\pmod\{([^}]+)\}': r' mod \1',
            r'\\cos': 'cos',
            r'\\sin': 'sin',
            r'\\tan': 'tan',
            r'\\exp': 'exp',
            r'\\_': '_',
            r'\\\\': '',
            r'\\text\{([^}]+)\}': r'\1',
            r'\\mathrm\{([^}]+)\}': r'\1'
        }
        
        result = formula
        for pattern, replacement in replacements.items():
            if '(' in pattern:  # Es un patrón regex
                result = re.sub(pattern, replacement, result)
            else:  # Es un reemplazo simple
                result = result.replace(pattern, replacement)
        
        # Limpiar espacios extra y formatear subíndices/superíndices
        result = re.sub(r'\{([^}]+)\}', r'\1', result)  # Remover llaves restantes
        result = re.sub(r'_([a-zA-Z0-9]+)', r'₍\1₎', result)  # Subíndices simples
        result = re.sub(r'\^([a-zA-Z0-9]+)', r'^(\1)', result)  # Superíndices simples
        
        return result
    
    def process_math_text(self, text):
        """Procesar todo el texto para mejorar la legibilidad"""
        # Mejorar formato general
        text = text.replace('---', '━━━')  # Líneas de separación más visibles
        text = text.replace('===', '═══')  # Líneas de separación dobles
        
        return text

class GeneradorPseudoaleatorio:
    def __init__(self, root):
        self.root = root
        self.root.title("Generador de Números Pseudoaleatorios y Variables Aleatorias")
        
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight() # Corrected: Removed underscore

        window_width = 1200
        window_height = 800

        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        self.root.state('zoomed') # Maximize the window on startup

        self.bg_color = "#e0f2f7"
        self.frame_bg = "#ffffff"
        self.text_color = "#37474f"
        self.primary_color = "#00796b"
        self.accent_color = "#4db6ac"

        self.root.configure(bg=self.bg_color)

        self.numeros_generados_uniformes = []
        self.valores_x_congruencial = []
        self.procedimiento_texto = ""
        # Store tuples of (Ri_used_for_X1, Ri_used_for_X2, Generated_X) for distribution table
        # For Binomial, this will be (First_U_of_the_n_trials, None, X_binomial_generated)
        self.numeros_generados_distribucion_data = [] # New: to store (Ri, Xi_dist)
        self.procedimiento_distribucion_texto = ""

        self.crear_estilos()
        self.crear_interfaz()

    def crear_estilos(self):
        style = ttk.Style()

        style.configure('TFrame', background=self.frame_bg)
        style.configure('TLabelframe', background=self.frame_bg, foreground=self.primary_color, font=("Segoe UI", 11, "bold"))
        style.configure('TLabelframe.Label', background=self.frame_bg, foreground=self.primary_color)

        style.configure('TButton',
                        background="#4db6ac",
                        foreground='#37474f',
                        font=("Segoe UI", 11, "bold"),
                        relief="flat",
                        padding=10,
                        borderwidth=0)
        style.map('TButton',
                  background=[('active', "#26a69a")],
                  foreground=[('active', '#37474f')])

        style.configure('TRadiobutton', background=self.frame_bg, foreground=self.text_color, font=("Segoe UI", 10))
        style.map('TRadiobutton',
                  background=[('active', self.frame_bg)])

        style.configure('TEntry', fieldbackground="#f0f8ff", foreground=self.text_color, font=("Segoe UI", 10))

        style.configure('TNotebook', background=self.bg_color, borderwidth=0)
        style.configure('TNotebook.Tab',
                        background=self.accent_color,
                        foreground=self.primary_color,
                        font=("Segoe UI", 10, "bold"),
                        padding=[10, 5])
        style.map('TNotebook.Tab',
                  background=[
                      ('selected', self.primary_color),
                      ('active', self.accent_color)
                  ],
                  foreground=[
                      ('selected', "#00796b"),
                      ('active', self.text_color),
                      ('!selected', self.text_color)
                  ])
        style.layout("TNotebook.Tab", [
            ("TNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("TNotebook.padding", {
                        "sticky": "nswe",
                        "children": [
                            ("TNotebook.focus", {
                                "sticky": "nswe",
                                "children": [
                                    ("TNotebook.label", {"sticky": "nswe"})
                                ]
                            })
                        ]
                    })
                ]
            })
        ])

        style.configure('TLabel', background=self.frame_bg, foreground=self.text_color, font=("Segoe UI", 10))
        style.configure('Title.TLabel', font=("Segoe UI", 18, "bold"), background=self.bg_color, foreground=self.primary_color)
        style.configure('Subtitle.TLabel', font=("Segoe UI", 12, "bold"), background=self.frame_bg, foreground=self.primary_color)
        style.configure('Section.TLabel', font=("Segoe UI", 11, "bold"), background=self.frame_bg, foreground=self.primary_color)

    def validar_entrada_numerica(self, P):
        if P.isdigit() or (P == "" and self.root.focus_get() is not None and isinstance(self.root.focus_get(), ttk.Entry)):
            return True
        else:
            messagebox.showerror("Error de Entrada", "Por favor, ingrese solo números enteros no negativos.")
            return False

    def validar_entrada_flotante(self, P):
        try:
            if P == "" and self.root.focus_get() is not None and isinstance(self.root.focus_get(), ttk.Entry):
                return True
            float(P)
            return True
        except ValueError:
            messagebox.showerror("Error de Entrada", "Por favor, ingrese un número válido (entero o decimal).")
            return False

    def crear_interfaz(self):
        vcmd_int = (self.root.register(self.validar_entrada_numerica), '%P')
        vcmd_float = (self.root.register(self.validar_entrada_flotante), '%P')

        titulo = ttk.Label(self.root, text="Generador de Números Pseudoaleatorios y Variables Aleatorias", style='Title.TLabel')
        titulo.pack(pady=15)

        main_frame = ttk.Frame(self.root, style='TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True)

        self.left_frame = ttk.Frame(paned_window, style='TFrame', relief=tk.RAISED, borderwidth=1)
        paned_window.add(self.left_frame, weight=1)

        uniform_gen_frame = ttk.LabelFrame(self.left_frame, text="Configuración de Números Uniformes [0,1)", style='TLabelframe')
        uniform_gen_frame.pack(padx=15, pady=10, fill=tk.X)

        ttk.Label(uniform_gen_frame, text="Método de Generación:", style='Section.TLabel').pack(pady=(5, 5))
        self.metodo_uniforme_var = tk.StringVar(value="mixto")
        ttk.Radiobutton(uniform_gen_frame, text="Congruencial Mixto", variable=self.metodo_uniforme_var, value="mixto", style='TRadiobutton', command=self.actualizar_parametros_uniformes).pack(anchor=tk.W, padx=30, pady=2)
        ttk.Radiobutton(uniform_gen_frame, text="Congruencial Multiplicativo", variable=self.metodo_uniforme_var, value="multiplicativo", style='TRadiobutton', command=self.actualizar_parametros_uniformes).pack(anchor=tk.W, padx=30, pady=2)
        ttk.Radiobutton(uniform_gen_frame, text="Estándar (Python/NumPy)", variable=self.metodo_uniforme_var, value="estandar", style='TRadiobutton', command=self.actualizar_parametros_uniformes).pack(anchor=tk.W, padx=30, pady=2)

        self.params_uniform_frame = ttk.Frame(uniform_gen_frame, style='TFrame')
        self.params_uniform_frame.pack(padx=20, pady=10, fill=tk.X)

        labels = ["Semilla (X₀):", "Constante (a):", "Constante (c):", "Módulo (m):", "Cantidad (N):"]
        self.entries_uniform_params = {}
        for text in labels:
            row_frame = ttk.Frame(self.params_uniform_frame, style='TFrame')
            row_frame.pack(fill=tk.X, pady=2)
            ttk.Label(row_frame, text=text, width=15, anchor=tk.W, style='TLabel').pack(side=tk.LEFT, padx=5)
            entry = ttk.Entry(row_frame, width=20, validate="key", validatecommand=vcmd_int, style='TEntry')
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
            self.entries_uniform_params[text.split(':')[0]] = entry

        self.entries_uniform_params["Semilla (X₀)"].insert(0, "7")
        self.entries_uniform_params["Constante (a)"].insert(0, "3")
        self.entries_uniform_params["Constante (c)"].insert(0, "5")
        self.entries_uniform_params["Módulo (m)"].insert(0, "17")
        self.entries_uniform_params["Cantidad (N)"].insert(0, "100")

        self.actualizar_parametros_uniformes()

        dist_sim_frame = ttk.LabelFrame(self.left_frame, text="Simulación de Variables Aleatorias", style='TLabelframe')
        dist_sim_frame.pack(padx=15, pady=10, fill=tk.X)

        ttk.Label(dist_sim_frame, text="Seleccione Distribución:", style='Section.TLabel').pack(pady=(5, 5))
        self.distribucion_var = tk.StringVar()
        self.distribucion_combobox = ttk.Combobox(dist_sim_frame, textvariable=self.distribucion_var,
                                                   values=["Normal", "Exponencial", "Binomial", "Poisson", "Geométrica"],
                                                   state="readonly", style='TCombobox')
        self.distribucion_combobox.pack(pady=5, padx=20, fill=tk.X)
        self.distribucion_combobox.bind("<<ComboboxSelected>>", self.mostrar_parametros_distribucion)

        self.params_dist_frame = ttk.Frame(dist_sim_frame, style='TFrame')
        self.params_dist_frame.pack(padx=20, pady=10, fill=tk.X)

        self.dist_param_entries = {}
        self.vcmd_int_dist = vcmd_int
        self.vcmd_float_dist = vcmd_float

        self.btn_generar_distribucion = ttk.Button(dist_sim_frame, text="Generar Variable Aleatoria", command=self.generar_variable_aleatoria, state=tk.DISABLED)
        self.btn_generar_distribucion.pack(pady=10)

        self.right_frame = ttk.Frame(paned_window, style='TFrame')
        paned_window.add(self.right_frame, weight=2)

        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.tab_uniformes = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.tab_uniformes, text="Números Uniformes")

        uniform_paned_window = ttk.PanedWindow(self.tab_uniformes, orient=tk.VERTICAL)
        uniform_paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        top_half_frame = ttk.Frame(uniform_paned_window, style='TFrame')
        uniform_paned_window.add(top_half_frame, weight=2)

        table_proc_paned_window = ttk.PanedWindow(top_half_frame, orient=tk.HORIZONTAL)
        table_proc_paned_window.pack(fill=tk.BOTH, expand=True)

        table_frame = ttk.Frame(table_proc_paned_window, style='TFrame')
        table_proc_paned_window.add(table_frame, weight=1)
        ttk.Label(table_frame, text="Tabla de Resultados de Números Uniformes", style='Subtitle.TLabel').pack(pady=(5, 5))
        self.tabla_uniformes = scrolledtext.ScrolledText(table_frame, wrap=tk.WORD, font=("Courier New", 10), bg="#f8f8f8", fg=self.text_color, relief=tk.FLAT)
        self.tabla_uniformes.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        proc_frame = ttk.Frame(table_proc_paned_window, style='TFrame')
        table_proc_paned_window.add(proc_frame, weight=1)
        ttk.Label(proc_frame, text="Procedimiento Paso a Paso", style='Subtitle.TLabel').pack(pady=(5, 5))
        self.procedimiento_text = MathTextWidget(proc_frame, bg="#f8f8f8", fg=self.text_color, font=("Courier New", 10))
        self.procedimiento_text.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        bottom_half_frame = ttk.Frame(uniform_paned_window, style='TFrame')
        uniform_paned_window.add(bottom_half_frame, weight=1)

        ttk.Label(bottom_half_frame, text="Gráfico de Números Uniformes", style='Subtitle.TLabel').pack(pady=(5, 5))
        self.figure_uniformes = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax_uniformes = self.figure_uniformes.add_subplot(111)
        self.canvas_uniformes = FigureCanvasTkAgg(self.figure_uniformes, master=bottom_half_frame)
        self.canvas_uniformes_widget = self.canvas_uniformes.get_tk_widget()
        self.canvas_uniformes_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

        self.tab_distribucion = ttk.Frame(self.notebook, style='TFrame')
        self.notebook.add(self.tab_distribucion, text="Variables Aleatorias")

        dist_paned_window = ttk.PanedWindow(self.tab_distribucion, orient=tk.VERTICAL)
        dist_paned_window.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        dist_top_half_frame = ttk.Frame(dist_paned_window, style='TFrame')
        dist_paned_window.add(dist_top_half_frame, weight=2)

        dist_table_proc_paned_window = ttk.PanedWindow(dist_top_half_frame, orient=tk.HORIZONTAL)
        dist_table_proc_paned_window.pack(fill=tk.BOTH, expand=True)

        dist_table_frame = ttk.Frame(dist_table_proc_paned_window, style='TFrame')
        dist_table_proc_paned_window.add(dist_table_frame, weight=1)
        self.dist_title_label = ttk.Label(dist_table_frame, text="Tabla de Resultados de Variable Aleatoria", style='Subtitle.TLabel')
        self.dist_title_label.pack(pady=(5, 5))
        self.tabla_distribucion = scrolledtext.ScrolledText(dist_table_frame, wrap=tk.WORD, font=("Courier New", 10), bg="#f8f8f8", fg=self.text_color, relief=tk.FLAT)
        self.tabla_distribucion.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        dist_proc_frame = ttk.Frame(dist_table_proc_paned_window, style='TFrame')
        dist_table_proc_paned_window.add(dist_proc_frame, weight=1)
        ttk.Label(dist_proc_frame, text="Procedimiento Paso a Paso", style='Subtitle.TLabel').pack(pady=(5, 5))
        self.procedimiento_distribucion_text_widget = MathTextWidget(dist_proc_frame, bg="#f8f8f8", fg=self.text_color, font=("Courier New", 10))
        self.procedimiento_distribucion_text_widget.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)

        dist_bottom_half_frame = ttk.Frame(dist_paned_window, style='TFrame')
        dist_paned_window.add(dist_bottom_half_frame, weight=1)

        ttk.Label(dist_bottom_half_frame, text="Gráfico de Distribución Generada", style='Subtitle.TLabel').pack(pady=(10, 5))
        self.figure_distribucion = plt.Figure(figsize=(6, 4), dpi=100)
        self.ax_distribucion = self.figure_distribucion.add_subplot(111)
        self.canvas_distribucion = FigureCanvasTkAgg(self.figure_distribucion, master=dist_bottom_half_frame)
        self.canvas_distribucion_widget = self.canvas_distribucion.get_tk_widget()
        self.canvas_distribucion_widget.pack(padx=10, pady=5, fill=tk.BOTH, expand=True)

    def actualizar_parametros_uniformes(self):
        metodo = self.metodo_uniforme_var.get()
        if metodo == "estandar":
            # Only N is editable for standard, other params for congruential are disabled
            for label_text, entry_widget in self.entries_uniform_params.items():
                if label_text != "Cantidad (N)":
                    entry_widget.config(state=tk.DISABLED)
                    entry_widget.delete(0, tk.END) # Clear content
                else:
                    entry_widget.config(state=tk.NORMAL)
                    if not entry_widget.get(): # If N is empty, re-insert default
                        entry_widget.insert(0, "100")
        else:
            # All params are editable for congruential methods
            for label_text, entry_widget in self.entries_uniform_params.items():
                entry_widget.config(state=tk.NORMAL)
            
            # Re-insert default values if empty, after enabling
            if not self.entries_uniform_params["Semilla (X₀)"].get(): self.entries_uniform_params["Semilla (X₀)"].insert(0, "7")
            if not self.entries_uniform_params["Constante (a)"].get(): self.entries_uniform_params["Constante (a)"].insert(0, "3")
            if not self.entries_uniform_params["Módulo (m)"].get(): self.entries_uniform_params["Módulo (m)"].insert(0, "17")
            if not self.entries_uniform_params["Cantidad (N)"].get(): self.entries_uniform_params["Cantidad (N)"].insert(0, "100")

            if metodo == "mixto":
                self.entries_uniform_params["Constante (c)"].config(state=tk.NORMAL)
                if not self.entries_uniform_params["Constante (c)"].get(): self.entries_uniform_params["Constante (c)"].insert(0, "5")
            elif metodo == "multiplicativo":
                self.entries_uniform_params["Constante (c)"].config(state=tk.DISABLED)
                self.entries_uniform_params["Constante (c)"].delete(0, tk.END)


    def mostrar_parametros_distribucion(self, event=None):
        for widget in self.params_dist_frame.winfo_children():
            widget.destroy()
        self.dist_param_entries.clear()
        self.btn_generar_distribucion.config(state=tk.NORMAL)

        distribucion = self.distribucion_var.get()
        labels_params = []
        if distribucion == "Normal":
            labels_params = [("Media (μ):", self.vcmd_float_dist), ("Desviación Estándar (σ):", self.vcmd_float_dist)]
        elif distribucion == "Exponencial":
            labels_params = [("Lambda (λ):", self.vcmd_float_dist)]
        elif distribucion == "Binomial":
            labels_params = [("N (Ensayos):", self.vcmd_int_dist), ("P (Probabilidad):", self.vcmd_float_dist)]
        elif distribucion == "Poisson":
            labels_params = [("Lambda (λ):", self.vcmd_float_dist)]
        elif distribucion == "Geométrica":
            labels_params = [("P (Probabilidad):", self.vcmd_float_dist)]

        for text, vcmd in labels_params:
            row_frame = ttk.Frame(self.params_dist_frame, style='TFrame')
            row_frame.pack(fill=tk.X, pady=2)
            ttk.Label(row_frame, text=text, width=20, anchor=tk.W, style='TLabel').pack(side=tk.LEFT, padx=5)
            entry = ttk.Entry(row_frame, width=20, validate="key", validatecommand=vcmd, style='TEntry')
            entry.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=5)
            self.dist_param_entries[text.split('(')[0].strip()] = entry

            if distribucion == "Normal" and text.startswith("Media"): entry.insert(0, "0")
            elif distribucion == "Normal" and text.startswith("Desviación"): entry.insert(0, "1")
            elif distribucion == "Exponencial" and text.startswith("Lambda"): entry.insert(0, "1")
            elif distribucion == "Binomial" and text.startswith("N"): entry.insert(0, "10")
            elif distribucion == "Binomial" and text.startswith("P"): entry.insert(0, "0.5")
            elif distribucion == "Poisson" and text.startswith("Lambda"): entry.insert(0, "2") # Default lambda for Poisson
            elif distribucion == "Geométrica" and text.startswith("P"): entry.insert(0, "0.5")

    def validar_parametros_uniformes(self, x0, a, c, m, n, metodo):
        if not all(isinstance(val, int) and val >= 0 for val in [x0, a, m, n]):
            messagebox.showerror("Error de Validación", "Todos los parámetros (X₀, a, m, N) deben ser enteros no negativos.")
            return False
        if metodo == "mixto" and not (isinstance(c, int) and c >= 0):
            messagebox.showerror("Error de Validación", "La constante c debe ser un entero no negativo para el método mixto.")
            return False

        if m <= 0:
            messagebox.showerror("Error de Validación", "El módulo (m) debe ser mayor que 0.")
            return False
        if n <= 0:
            messagebox.showerror("Error de Validación", "La cantidad (N) debe ser mayor que 0.")
            return False
        if not (0 <= x0 < m):
            messagebox.showerror("Error de Validación", "La semilla (X₀) debe ser mayor o igual a 0 y menor que el módulo (m).")
            return False
        if not (0 < a < m):
            messagebox.showerror("Error de Validación", "La constante (a) debe ser mayor que 0 y menor que el módulo (m).")
            return False
        if metodo == "mixto" and not (0 <= c < m):
            messagebox.showerror("Error de Validación", "La constante (c) debe ser mayor o igual a 0 y menor que el módulo (m).")
            return False

        if metodo == "multiplicativo":
            if x0 % 2 == 0 or m % 2 == 0:
                messagebox.showerror("Error de Validación", "Para el método multiplicativo (generación de periodo máximo), la Semilla (X₀) y el Módulo (m) deben ser impares.")
                return False
            if m % 5 == 0:
                messagebox.showerror("Error de Validación", "Para el método multiplicativo (generación de periodo máximo), el Módulo (m) no debe ser múltiplo de 5.")
                return False
        return True

    def generar_numeros_uniformes(self, N_uniformes_requeridos):
        # N_uniformes_requeridos is the *total* number of uniforms needed for the current distribution generation
        # This function will generate exactly N_uniformes_requeridos or more if congruential method generates a full cycle
        # We also need to get the N parameter from uniform entries, which is the user-specified N
        
        N_from_entry = 0
        try:
            N_from_entry = int(self.entries_uniform_params["Cantidad (N)"].get())
        except ValueError:
            messagebox.showerror("Error de Entrada", "La cantidad (N) para la generación de uniformes debe ser un número entero.")
            return False

        # If N_uniformes_requeridos is not explicitly passed (e.g., when just generating uniforms)
        # or if the distribution needs fewer than the user-specified N, then use N_from_entry.
        # Otherwise, ensure we generate at least N_uniformes_requeridos.
        actual_N_to_generate = max(N_from_entry, N_uniformes_requeridos)
        
        self.numeros_generados_uniformes = []
        self.valores_x_congruencial = []
        self.procedimiento_texto = ""
        metodo = self.metodo_uniforme_var.get()

        if metodo == "estandar":
            self.procedimiento_text.delete(1.0, tk.END)
            texto_procedimiento = "Generando números aleatorios utilizando np.random.rand()\n"
            texto_procedimiento += f"Se generaron {actual_N_to_generate} números uniformes entre 0 y 1.\n"
            self.procedimiento_text.insert(tk.END, texto_procedimiento)
            self.numeros_generados_uniformes = np.random.rand(actual_N_to_generate).tolist()
            self.valores_x_congruencial = ['N/A'] * actual_N_to_generate # Asignar 'N/A' para el método estándar
        else:
            x0_str = self.entries_uniform_params["Semilla (X₀)"].get()
            a_str = self.entries_uniform_params["Constante (a)"].get()
            c_str = self.entries_uniform_params["Constante (c)"].get()
            m_str = self.entries_uniform_params["Módulo (m)"].get()

            try:
                X0 = int(x0_str)
                a = int(a_str)
                m = int(m_str)
                c = int(c_str) if metodo == "mixto" else 0
            except ValueError:
                messagebox.showerror("Error de Entrada", "Asegúrese de que X₀, a, c, m, y N sean números enteros válidos.")
                return False

            if not self.validar_parametros_uniformes(X0, a, c, m, actual_N_to_generate, metodo):
                return False

            self.procedimiento_text.delete(1.0, tk.END)
            
            # Construir el texto del procedimiento
            texto_procedimiento = f"Parámetros:\n"
            texto_procedimiento += f"  X₀ = {X0}\n  a = {a}\n  m = {m}\n"
            
            if metodo == "mixto":
                texto_procedimiento += f"  c = {c}\n"
                texto_procedimiento += "Método: Congruencial Mixto\n\n"
                texto_procedimiento += "Fórmula: $X_{{i+1}} = (a × X_i + c) \\bmod m$\n"
                texto_procedimiento += "Fórmula: $R_i = X_i / m$\n\n"
            else:
                texto_procedimiento += "Método: Congruencial Multiplicativo (Lehmer)\n\n"
                texto_procedimiento += "Fórmula: $X_{{i+1}} = (a × X_i) \\bmod m$\n"
                texto_procedimiento += "Fórmula: $R_i = X_i / m$\n\n"
            
            texto_procedimiento += "Procedimiento de generación:\n"

            xi = X0
            for i in range(actual_N_to_generate):
                if metodo == "mixto":
                    xi_next = (a * xi + c) % m
                    texto_procedimiento += f"X_{{{i+1}}} = ({a} * {xi} + {c}) mod {m} = {xi_next}\n"
                else:
                    xi_next = (a * xi) % m
                    texto_procedimiento += f"X_{{{i+1}}} = ({a} * {xi}) mod {m} = {xi_next}\n"

                ri = xi_next / m
                self.numeros_generados_uniformes.append(ri)
                self.valores_x_congruencial.append(xi_next)
                texto_procedimiento += f"R_{{{i+1}}} = {xi_next} / {m} = {ri:.8f}\n\n"
                xi = xi_next
            
            # Insertar todo el texto de una vez
            self.procedimiento_text.insert(tk.END, texto_procedimiento)
            
        self.actualizar_tablas_y_graficos_uniformes()
        return True

    def actualizar_tablas_y_graficos_uniformes(self):
        self.tabla_uniformes.delete(1.0, tk.END)
        self.tabla_uniformes.insert(tk.END, " N° |         Xi |          Ri\n")
        self.tabla_uniformes.insert(tk.END, "----|------------|------------------\n")

        # Ensure self.valores_x_congruencial is populated correctly even for "estandar" method
        x_vals_to_display = self.valores_x_congruencial if self.metodo_uniforme_var.get() != "estandar" else ['N/A'] * len(self.numeros_generados_uniformes)

        for i, (x_val, r_val) in enumerate(zip(x_vals_to_display, self.numeros_generados_uniformes)):
            fila = f"{i+1:>3} | {str(x_val):>10} | {r_val:>16.8f}\n"
            self.tabla_uniformes.insert(tk.END, fila)

        if len(self.numeros_generados_uniformes) > 0:
            media = sum(self.numeros_generados_uniformes) / len(self.numeros_generados_uniformes)
            valores_unicos_r = len(set(self.numeros_generados_uniformes))

            resumen = f"\n{'='*40}\n"
            resumen += f"{'RESUMEN ESTADÍSTICO':^40}\n"
            resumen += f"{'='*40}\n"
            resumen += f"Total de números generados: {len(self.numeros_generados_uniformes)}\n"
            resumen += f"Media de valores R: {media:.4f}\n"
            resumen += f"Valores únicos R: {valores_unicos_r}\n"

            if self.metodo_uniforme_var.get() != "estandar":
                valores_unicos_x = len(set(self.valores_x_congruencial))
                resumen += f"Valores únicos X: {valores_unicos_x}\n"
                resumen += f"Mínimo X: {min(self.valores_x_congruencial)}\n"
                resumen += f"Máximo X: {max(self.valores_x_congruencial)}\n"

            resumen += f"Mínimo R: {min(self.numeros_generados_uniformes):.6f}\n"
            resumen += f"Máximo R: {max(self.numeros_generados_uniformes):.6f}\n"
            resumen += f"{'='*40}\n"
            self.tabla_uniformes.insert(tk.END, resumen)

        self.ax_uniformes.clear()
        if self.numeros_generados_uniformes:
            self.ax_uniformes.hist(self.numeros_generados_uniformes, bins=20, density=True, color=self.accent_color, edgecolor=self.primary_color, alpha=0.7)
            self.ax_uniformes.set_title("Histograma de Números Uniformes [0,1)", color=self.text_color)
            self.ax_uniformes.set_xlabel("Valor", color=self.text_color)
            self.ax_uniformes.set_ylabel("Densidad de Probabilidad", color=self.text_color)
            self.ax_uniformes.set_facecolor(self.frame_bg)
            self.figure_uniformes.patch.set_facecolor(self.frame_bg)
            self.ax_uniformes.tick_params(colors=self.text_color)
            for spine in self.ax_uniformes.spines.values():
                spine.set_edgecolor(self.text_color)

            self.ax_uniformes.axhline(1, color='red', linestyle='dashed', linewidth=2, label="PDF Uniforme Teórica")
            self.ax_uniformes.set_ylim(bottom=0, top=1.2)
            self.ax_uniformes.legend()
        else:
            self.ax_uniformes.text(0.5, 0.5, "No hay datos para mostrar", horizontalalignment='center', verticalalignment='center', transform=self.ax_uniformes.transAxes, color=self.text_color)

        self.canvas_uniformes.draw()

    def validar_parametros_distribucion(self, distribucion, params):
        try:
            if distribucion == "Normal":
                media = float(params.get("Media", 0))
                std_dev = float(params.get("Desviación Estándar", 0))
                if std_dev <= 0:
                    messagebox.showerror("Error de Validación", "La desviación estándar debe ser mayor que 0.")
                    return False, None
                return True, {'loc': media, 'scale': std_dev}
            elif distribucion == "Exponencial":
                lam = float(params.get("Lambda", 0))
                if lam <= 0:
                    messagebox.showerror("Error de Validación", "Lambda (λ) debe ser mayor que 0.")
                    return False, None
                return True, {'scale': 1/lam}
            elif distribucion == "Binomial":
                n = int(params.get("N", 0))
                p = float(params.get("P", 0))
                if not (0 <= p <= 1):
                    messagebox.showerror("Error de Validación", "La probabilidad (P) debe estar entre 0 y 1.")
                    return False, None
                if n <= 0:
                    messagebox.showerror("Error de Validación", "El número de ensayos (N) debe ser un entero positivo.")
                    return False, None
                return True, {'n': n, 'p': p}
            elif distribucion == "Poisson":
                lam = float(params.get("Lambda", 0))
                if lam <= 0:
                    messagebox.showerror("Error de Validación", "Lambda (λ) debe ser mayor que 0.")
                    return False, None
                return True, {'mu': lam}
            elif distribucion == "Geométrica":
                p = float(params.get("P", 0))
                if not (0 < p <= 1):
                    messagebox.showerror("Error de Validación", "La probabilidad (P) debe estar entre 0 (exclusive) y 1.")
                    return False, None
                return True, {'p': p}
            return False, None
        except ValueError:
            messagebox.showerror("Error de Entrada", "Por favor, ingrese valores numéricos válidos para los parámetros de la distribución.")
            return False, None

    def generar_variable_aleatoria(self):
        distribucion = self.distribucion_var.get()
        if not distribucion:
            messagebox.showerror("Error", "Por favor, seleccione un tipo de distribución.")
            return

        params_raw = {key: entry.get() for key, entry in self.dist_param_entries.items()}
        es_valido, params = self.validar_parametros_distribucion(distribucion, params_raw)
        if not es_valido:
            return

        # Get N from uniform parameters (this N is the number of distribution samples to generate)
        try:
            N_dist_samples = int(self.entries_uniform_params["Cantidad (N)"].get())
            if N_dist_samples <= 0:
                messagebox.showerror("Error de Entrada", "La cantidad (N) debe ser un número entero positivo.")
                return
        except ValueError:
            messagebox.showerror("Error de Entrada", "La cantidad (N) para la generación de uniformes debe ser un número entero.")
            return

        required_uniforms_for_dist = N_dist_samples # Default, will be adjusted for Normal and Binomial

        if distribucion == "Normal":
            # Normal requires 2 uniforms per sample, so N_dist_samples * 2 uniforms are needed
            # We also ensure an even number of uniforms by adding 1 if N_dist_samples is odd.
            required_uniforms_for_dist = N_dist_samples + (N_dist_samples % 2) 
        elif distribucion == "Binomial":
            n_trials_per_sample = params['n'] # 'n' from Binomial parameters
            required_uniforms_for_dist = N_dist_samples * n_trials_per_sample
            if required_uniforms_for_dist == 0: # Avoid division by zero or infinite loop if n_trials is 0
                messagebox.showerror("Error", "El número de ensayos (N) para la distribución Binomial debe ser mayor que 0.")
                return


        # Always generate uniform numbers first, ensuring enough are available for the chosen distribution
        if not self.generar_numeros_uniformes(required_uniforms_for_dist):
             return

        self.numeros_generados_distribucion_data = [] # Reset for new data
        self.procedimiento_distribucion_texto = ""
        cantidad_uniformes_disponibles = len(self.numeros_generados_uniformes) 

        self.procedimiento_distribucion_texto += f"Distribución seleccionada: {distribucion}\n"
        self.procedimiento_distribucion_texto += f"Parámetros: {params_raw}\n"
        self.procedimiento_distribucion_texto += f"Números Uniformes disponibles: {cantidad_uniformes_disponibles}. (Mostrando los primeros 5 si son muchos): {[f'{u:.4f}' for u in self.numeros_generados_uniformes[:min(5, cantidad_uniformes_disponibles)]]}...\n\n"
        self.procedimiento_distribucion_texto += "--- Procedimiento de Generación ---\n"

        uniform_index = 0 # To keep track of which uniform numbers have been used

        try:
            if distribucion == "Normal":
                self.procedimiento_distribucion_texto += "Usando el Método de Box-Muller (Transformada Inversa):\n"
                self.procedimiento_distribucion_texto += "Fórmulas:\n"
                self.procedimiento_distribucion_texto += "  $Z_0 = \\sqrt{{-2 × \\ln(U_1)}} × \\cos(2π × U_2)$\n"
                self.procedimiento_distribucion_texto += "  $Z_1 = \\sqrt{{-2 × \\ln(U_1)}} × \\sin(2π × U_2)$\n"
                self.procedimiento_distribucion_texto += "  $X = μ + σ × Z$\n\n"

                # Ensure we have an even number of uniforms for Box-Muller
                num_pairs_to_generate = cantidad_uniformes_disponibles // 2
                
                if num_pairs_to_generate < 1:
                    messagebox.showwarning("Advertencia", "Se necesitan al menos 2 números uniformes para la distribución Normal con el método de Box-Muller.")
                    return

                for i in range(num_pairs_to_generate):
                    if uniform_index + 1 >= cantidad_uniformes_disponibles:
                        # Should not happen if required_uniforms_for_dist was correctly calculated
                        self.procedimiento_distribucion_texto += "  No hay suficientes números uniformes para formar un par completo. Deteniendo la generación de Normal.\n"
                        break

                    u1 = self.numeros_generados_uniformes[uniform_index]
                    u2 = self.numeros_generados_uniformes[uniform_index + 1]
                    uniform_index += 2 # Consume two uniforms per pair

                    if u1 == 0: u1 = 1e-10 # Avoid log(0)
                    # u2 can be 0, cos/sin handles it correctly.

                    # Box-Muller Transformation
                    sqrt_term = np.sqrt(-2 * np.log(u1))
                    z0 = sqrt_term * np.cos(2 * np.pi * u2)
                    z1 = sqrt_term * np.sin(2 * np.pi * u2)

                    # Scale and shift to desired mean and std dev
                    x0 = params['loc'] + params['scale'] * z0
                    x1 = params['loc'] + params['scale'] * z1

                    # Store both generated values along with the pair of uniforms that created them
                    self.numeros_generados_distribucion_data.append((u1, u2, x0))
                    self.numeros_generados_distribucion_data.append((u1, u2, x1))

                    self.procedimiento_distribucion_texto += f"Par de uniformes {i+1}: U1={u1:.4f}, U2={u2:.4f}\n"
                    self.procedimiento_distribucion_texto += f"  $Z_0 = \\sqrt{{-2 × \\ln({u1:.4f})}} × \\cos(2π × {u2:.4f}) = {z0:.4f}$\n"
                    self.procedimiento_distribucion_texto += f"  $Z_1 = \\sqrt{{-2 × \\ln({u1:.4f})}} × \\sin(2π × {u2:.4f}) = {z1:.4f}$\n"
                    self.procedimiento_distribucion_texto += f"  $X_0 = {params['loc']:.2f} + {params['scale']:.2f} × {z0:.4f} = {x0:.4f}$\n"
                    self.procedimiento_distribucion_texto += f"  $X_1 = {params['loc']:.2f} + {params['scale']:.2f} × {z1:.4f} = {x1:.4f}$\n\n"
                
                # Truncate to N_dist_samples if more values were generated (e.g., if N_dist_samples was odd)
                if len(self.numeros_generados_distribucion_data) > N_dist_samples:
                    self.numeros_generados_distribucion_data = self.numeros_generados_distribucion_data[:N_dist_samples]
                    self.procedimiento_distribucion_texto += f"Nota: Se truncaron los resultados para coincidir con el N solicitado ({N_dist_samples}).\n"


            elif distribucion == "Exponencial":
                lam = 1 / params['scale']
                self.procedimiento_distribucion_texto += "Usando la Transformada Inversa:\n"
                self.procedimiento_distribucion_texto += "Fórmula: $X = -(1/λ) × \\ln(1 - U)$\n\n"
                for i in range(N_dist_samples): # Generate N_dist_samples samples
                    if uniform_index >= cantidad_uniformes_disponibles:
                        self.procedimiento_distribucion_texto += "  No quedan números uniformes para completar la muestra. Deteniendo.\n"
                        break
                    u = self.numeros_generados_uniformes[uniform_index]
                    uniform_index += 1
                    if u == 1: u = 0.999999 # Avoid log(0)
                    x_val = - (1/lam) * np.log(1 - u)
                    self.numeros_generados_distribucion_data.append((u, None, x_val)) # U1, U2 (None), X_val
                    self.procedimiento_distribucion_texto += f"R_{{{i+1}}}={u:.4f} -> $X_{{{i+1}}} = -(1/{lam:.2f}) × \\ln(1 - {u:.4f}) = {x_val:.4f}$\n"


            elif distribucion == "Binomial":
                n_trials_per_sample = params['n']
                p_success = params['p']
                self.procedimiento_distribucion_texto += f"Simulación de {N_dist_samples} muestras de Binomial(n={n_trials_per_sample}, p={p_success:.2f}).\n"
                self.procedimiento_distribucion_texto += f"Cada muestra Binomial requiere n = {n_trials_per_sample} números uniformes.\n"
                self.procedimiento_distribucion_texto += f"Se cuenta el número de 'éxitos' (U ≤ p = {p_success:.2f}) en cada conjunto de n uniformes.\n\n"
                
                for i_sample in range(N_dist_samples):
                    successes = 0
                    uniforms_for_this_sample = [] # To display in the procedure
                    self.procedimiento_distribucion_texto += f"Muestra Binomial {i_sample+1}:\n"
                    
                    # Ensure enough uniform numbers are available for this specific sample (n_trials_per_sample)
                    if uniform_index + n_trials_per_sample > cantidad_uniformes_disponibles:
                        self.procedimiento_distribucion_texto += f"  No hay suficientes números uniformes ({cantidad_uniformes_disponibles - uniform_index} restantes) para completar esta muestra (se necesitan {n_trials_per_sample}). Deteniendo la generación de Binomial.\n"
                        messagebox.showwarning("Advertencia", f"No hay suficientes números uniformes para generar las {N_dist_samples} muestras Binomiales deseadas. Se generaron {len(self.numeros_generados_distribucion_data)} muestras.")
                        break

                    for j in range(n_trials_per_sample):
                        u_val = self.numeros_generados_uniformes[uniform_index]
                        uniforms_for_this_sample.append(u_val)
                        uniform_index += 1
                        if u_val <= p_success:
                            successes += 1
                            self.procedimiento_distribucion_texto += f"  Ensayo {j+1}: U = {u_val:.4f} ≤ p = {p_success:.2f} → ÉXITO\n"
                        else:
                            self.procedimiento_distribucion_texto += f"  Ensayo {j+1}: U = {u_val:.4f} > p = {p_success:.2f} → FRACASO\n"
                    
                    # Store the first uniform of the set used for this sample, and the generated value
                    display_ri1 = uniforms_for_this_sample[0] if uniforms_for_this_sample else float('nan')
                    self.numeros_generados_distribucion_data.append((display_ri1, None, successes))
                    self.procedimiento_distribucion_texto += f"  Uniformes usados para esta muestra: {', '.join([f'{u:.4f}' for u in uniforms_for_this_sample])}\n" # Detailed display
                    self.procedimiento_distribucion_texto += f"  Total éxitos para esta muestra: {successes}\n\n"
                
                if not self.numeros_generados_distribucion_data and N_dist_samples > 0:
                    messagebox.showwarning("Advertencia", "No se pudieron generar muestras binomiales.")


            elif distribucion == "Poisson":
                lam = params['mu']
                # Open new window for Poisson PMF/CDF table
                self.mostrar_tabla_poisson_pmf_cdf(lam)

                self.procedimiento_distribucion_texto += f"Simulación de {N_dist_samples} muestras de Poisson(λ = {lam:.2f}) usando la Transformada Inversa.\n"
                self.procedimiento_distribucion_texto += "Se genera X tal que $P(X < X_i) \\leq U < P(X \\leq X_i)$.\n\n"
                self.procedimiento_distribucion_texto += "Valores de P(X=k) y P(X ≤ k) usados para la búsqueda:\n"

                # Calculate PMF and CDF for relevant k values
                k_max = int(lam + 5 * np.sqrt(lam)) # Heuristic for max k
                if k_max < 10: k_max = 10
                pmf_values = [poisson.pmf(k, mu=lam) for k in range(k_max + 1)]
                cdf_values = [poisson.cdf(k, mu=lam) for k in range(k_max + 1)]

                for i in range(N_dist_samples):
                    if uniform_index >= cantidad_uniformes_disponibles:
                        self.procedimiento_distribucion_texto += "  No quedan números uniformes para completar la muestra. Deteniendo.\n"
                        break
                    u_val = self.numeros_generados_uniformes[uniform_index]
                    uniform_index += 1
                    self.procedimiento_distribucion_texto += f"Muestra Poisson {i+1}: U = {u_val:.4f}\n"
                    generated_x = -1
                    for k in range(k_max + 1):
                        if k == 0:
                            # pk = pmf_values[k] # Not strictly needed for logic, but for procedure text
                            P_X_less_k = 0.0 # P(X < 0) = 0
                            P_X_le_k = cdf_values[k] # P(X <= 0)
                        else:
                            # pk = pmf_values[k]
                            P_X_less_k = cdf_values[k-1] # P(X < k) = P(X <= k-1)
                            P_X_le_k = cdf_values[k] # P(X <= k)

                        self.procedimiento_distribucion_texto += f"  k={k}, P(X<{k})={P_X_less_k:.6f}, P(X≤{k})={P_X_le_k:.6f}\n"

                        if P_X_less_k <= u_val < P_X_le_k:
                            generated_x = k
                            self.procedimiento_distribucion_texto += f"  Condición {P_X_less_k:.6f} ≤ {u_val:.4f} < {P_X_le_k:.6f} CUMPLIDA. Valor generado: X = {k}\n\n"
                            break
                    if generated_x == -1:
                        # If U is very close to 1, it might exceed all pre-calculated k_max, assign last k_max
                        generated_x = k_max
                        self.procedimiento_distribucion_texto += f"  U={u_val:.4f} excede todas las probabilidades. Asignando k_max ({k_max}).\n\n"
                    self.numeros_generados_distribucion_data.append((u_val, None, generated_x)) # Store U1, U2 (None), X_val


            elif distribucion == "Geométrica":
                p = params['p']
                self.procedimiento_distribucion_texto += "Usando la Transformada Inversa para la distribución Geométrica(p = {:.2f}):\n".format(p)
                self.procedimiento_distribucion_texto += "Fórmula: $X = ⌊\\ln(1-U)/\\ln(1-p)⌋ + 1$\n"
                ln_one_minus_p = np.log(1 - p)
                self.procedimiento_distribucion_texto += f"ln(1-p) = ln(1-{p:.2f}) = {ln_one_minus_p:.4f}\n\n"

                if (1-p) <= 0: # This also covers p=1.0 which makes ln(1-p) undefined
                    messagebox.showerror("Error", "La probabilidad (P) no puede ser 1 para la distribución Geométrica al usar la transformada inversa.")
                    return

                for i in range(N_dist_samples):
                    if uniform_index >= cantidad_uniformes_disponibles:
                        self.procedimiento_distribucion_texto += "  No quedan números uniformes para completar la muestra. Deteniendo.\n"
                        break
                    u = self.numeros_generados_uniformes[uniform_index]
                    uniform_index += 1
                    if u == 1: u = 0.999999 # Avoid log(0) for ln(1-U)
                    val_ln_1_minus_u = np.log(1 - u)
                    x_val_float = val_ln_1_minus_u / ln_one_minus_p
                    x_val = np.floor(x_val_float) + 1
                    self.numeros_generados_distribucion_data.append((u, None, int(x_val))) # Store U1, U2 (None), X_val
                    self.procedimiento_distribucion_texto += f"R_{{{i+1}}}={u:.4f} -> $X_{{{i+1}}} = ⌊\\ln(1 - {u:.4f})/\\ln(1 - {p:.2f})⌋ + 1 = ⌊{val_ln_1_minus_u:.4f}/{ln_one_minus_p:.4f}⌋ + 1 = {int(x_val)}$\n"


            # Extract only the generated X values for plotting and summary statistics
            # This is created from numeros_generados_distribucion_data for convenience
            self.numeros_generados_distribucion = [item[2] for item in self.numeros_generados_distribucion_data]

            self.actualizar_tablas_y_graficos_distribucion(distribucion, params)
            self.notebook.select(self.tab_distribucion)

        except Exception as e:
            messagebox.showerror("Error de Generación", f"Ocurrió un error al generar la variable aleatoria: {e}")

    def mostrar_tabla_poisson_pmf_cdf(self, lam):
        poisson_window = tk.Toplevel(self.root)
        poisson_window.title(f"Tabla de Probabilidad Poisson (λ={lam:.2f})")
        poisson_window.geometry("500x600")
        poisson_window.configure(bg=self.bg_color)

        frame = ttk.Frame(poisson_window, style='TFrame')
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(frame, text=f"Tabla de Probabilidad para Poisson (λ={lam:.2f})", style='Subtitle.TLabel').pack(pady=(5, 10))

        table_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD, font=("Courier New", 10), bg="#f8f8f8", fg=self.text_color, relief=tk.FLAT)
        table_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        table_text.insert(tk.END, " k  | P(X=k) (PMF) | P(X<=k) (CDF)\n")
        table_text.insert(tk.END, "----|--------------|---------------\n")

        # Determine a reasonable range for k based on lambda
        # Go up to where CDF is close to 1 or k is far enough from lambda
        max_k = int(lam + 5 * np.sqrt(lam))
        if max_k < 10: max_k = 10 # Ensure at least a few values are shown
        if lam > 0 and max_k < 1: max_k = 1 # Handle very small lambda

        cumulative_prob = 0.0
        for k in range(max_k + 2): # +2 to ensure we get slightly beyond for lookup
            pk = poisson.pmf(k, mu=lam)
            cumulative_prob = poisson.cdf(k, mu=lam) # Get CDF directly to avoid floating point accumulation errors
            table_text.insert(tk.END, f"{k:^4} | {pk:^12.6f} | {cumulative_prob:^13.6f}\n")
            if cumulative_prob > 0.99999 and k > lam: # Stop if CDF is very close to 1
                break


    def actualizar_tablas_y_graficos_distribucion(self, distribucion, params):
        self.dist_title_label.config(text=f"Tabla de Resultados de Distribución {distribucion}")

        self.tabla_distribucion.delete(1.0, tk.END)
        
        # Adjust table header based on distribution type
        if distribucion == "Normal":
            self.tabla_distribucion.insert(tk.END, f" N° | Ri (U1)    | Ri (U2)    | Valor Generado ({distribucion})\n")
            self.tabla_distribucion.insert(tk.END, "----|------------|------------|--------------------------\n")
        elif distribucion == "Binomial":
            # For Binomial, we show the first Ri used and indicate it's from a group of 'n' uniforms
            self.tabla_distribucion.insert(tk.END, f" N° | Ri (1er Usado) | Valor Generado ({distribucion})\n")
            self.tabla_distribucion.insert(tk.END, "----|----------------|--------------------------\n")
        else: # For other distributions, still use one Ri per generated value (U1 and U2 are N/A)
            self.tabla_distribucion.insert(tk.END, f" N° |         Ri | Valor Generado ({distribucion})\n")
            self.tabla_distribucion.insert(tk.END, "----|------------|--------------------------\n")

        # Iterate through self.numeros_generados_distribucion_data to get the (U1, U2, Xi_dist) or (U1, None, Xi_dist) tuples
        for i, data_row in enumerate(self.numeros_generados_distribucion_data):
            
            dist_val = data_row[2] # The generated X value is always the 3rd element
            dist_val_str = f"{dist_val:.8f}" if isinstance(dist_val, float) else str(dist_val)

            if distribucion == "Normal":
                u1_val = data_row[0]
                u2_val = data_row[1]
                u1_str = f"{u1_val:.8f}"
                u2_str = f"{u2_val:.8f}"
                fila = f"{i+1:>3} | {u1_str:>10} | {u2_str:>10} | {dist_val_str:^24}\n"
            elif distribucion == "Binomial":
                u1_val = data_row[0] # This is the first uniform used for the sample
                u1_str = f"{u1_val:.8f}"
                fila = f"{i+1:>3} | {u1_str:>14} | {dist_val_str:^24}\n"
            else:
                u1_val = data_row[0]
                u1_str = f"{u1_val:.8f}"
                fila = f"{i+1:>3} | {u1_str:>10} | {dist_val_str:^24}\n"
            
            self.tabla_distribucion.insert(tk.END, fila)

        # Handle the case where the number of generated distribution values is less than original N
        original_N_dist_samples = int(self.entries_uniform_params["Cantidad (N)"].get())
        if len(self.numeros_generados_distribucion) < original_N_dist_samples:
             self.tabla_distribucion.insert(tk.END, "\n" + "-"*60 + "\n")
             self.tabla_distribucion.insert(tk.END, f"Nota: Se generaron {len(self.numeros_generados_distribucion)} valores de distribución (se solicitaron {original_N_dist_samples}). Para la Normal, cada par de uniformes genera 2 valores. Para Binomial, cada muestra usa múltiples uniformes.\n")
             self.tabla_distribucion.insert(tk.END, "-"*60 + "\n")


        if len(self.numeros_generados_distribucion) > 0:
            if distribucion in ["Normal", "Exponencial"]:
                mean_gen = np.mean(self.numeros_generados_distribucion)
                std_gen = np.std(self.numeros_generados_distribucion)
                resumen = f"\n{'='*40}\n"
                resumen += f"{'RESUMEN ESTADÍSTICO':^40}\n"
                resumen += f"{'='*40}\n"
                resumen += f"Total de valores generados: {len(self.numeros_generados_distribucion)}\n"
                resumen += f"Media generada: {mean_gen:.6f}\n"
                resumen += f"Desviación Estándar generada: {std_gen:.6f}\n"
                resumen += f"Mínimo: {min(self.numeros_generados_distribucion):.6f}\n"
                resumen += f"Máximo: {max(self.numeros_generados_distribucion):.6f}\n"
                resumen += f"{'='*40}\n"
            else: # Discrete distributions
                unique_values, counts = np.unique(self.numeros_generados_distribucion, return_counts=True)
                mode_val = unique_values[np.argmax(counts)] if unique_values.size > 0 else "N/A"
                resumen = f"\n{'='*40}\n"
                resumen += f"{'RESUMEN ESTADÍSTICO':^40}\n"
                resumen += f"{'='*40}\n"
                resumen += f"Total de valores generados: {len(self.numeros_generados_distribucion)}\n"
                resumen += f"Media generada: {np.mean(self.numeros_generados_distribucion):.4f}\n"
                resumen += f"Moda: {mode_val}\n"
                resumen += f"Mínimo: {min(self.numeros_generados_distribucion)}\n"
                resumen += f"Máximo: {max(self.numeros_generados_distribucion)}\n"
                resumen += f"{'='*40}\n"
            self.tabla_distribucion.insert(tk.END, resumen)

        self.procedimiento_distribucion_text_widget.delete(1.0, tk.END)
        self.procedimiento_distribucion_text_widget.insert(tk.END, self.procedimiento_distribucion_texto)

        self.ax_distribucion.clear()
        if self.numeros_generados_distribucion:
            self.ax_distribucion.set_title(f"Histograma de Distribución {distribucion}", color=self.text_color)
            self.ax_distribucion.set_xlabel("Valor", color=self.text_color)
            self.ax_distribucion.set_ylabel("Frecuencia Normalizada", color=self.text_color)
            self.ax_distribucion.set_facecolor(self.frame_bg)
            self.figure_distribucion.patch.set_facecolor(self.frame_bg)
            self.ax_distribucion.tick_params(colors=self.text_color)
            for spine in self.ax_distribucion.spines.values():
                spine.set_edgecolor(self.text_color)

            if distribucion in ["Normal", "Exponencial"]:
                count, bins, ignored = self.ax_distribucion.hist(self.numeros_generados_distribucion, bins=30, density=True, color=self.accent_color, edgecolor=self.primary_color, alpha=0.7)
                x_axis = np.linspace(min(self.numeros_generados_distribucion), max(self.numeros_generados_distribucion), 100)

                if distribucion == "Normal":
                    pdf = norm.pdf(x_axis, loc=params['loc'], scale=params['scale'])
                    self.ax_distribucion.plot(x_axis, pdf, color='red', linestyle='dashed', linewidth=2, label="PDF Teórica")
                elif distribucion == "Exponencial":
                    pdf = expon.pdf(x_axis, scale=params['scale'])
                    self.ax_distribucion.plot(x_axis, pdf, color='red', linestyle='dashed', linewidth=2, label="PDF Teórica")
            else: # Discrete distributions
                unique_vals = np.unique(self.numeros_generados_distribucion)
                if unique_vals.size > 0:
                    min_val = min(unique_vals)
                    max_val = max(unique_vals)
                    # Adjust bins for discrete histogram to center bars on integer values
                    bins = np.arange(min_val - 0.5, max_val + 1.5, 1)
                    self.ax_distribucion.hist(self.numeros_generados_distribucion, bins=bins, density=True, color=self.accent_color, edgecolor=self.primary_color, alpha=0.7, rwidth=0.8)
                    self.ax_distribucion.set_xticks(unique_vals) # Set x-ticks to actual integer values
                else:
                    self.ax_distribucion.text(0.5, 0.5, "No hay datos para mostrar", horizontalalignment='center', verticalalignment='center', transform=self.ax_distribucion.transAxes, color=self.text_color)
                
                if distribucion == "Binomial":
                    # Generate theoretical PMF for comparison
                    k_values = np.arange(0, params['n'] + 1)
                    pmf = binom.pmf(k_values, n=params['n'], p=params['p'])
                    # Plot PMF as discrete points with lines to guide
                    self.ax_distribucion.plot(k_values, pmf, 'ro', markersize=6, label="PMF Teórica")
                    self.ax_distribucion.vlines(k_values, 0, pmf, color='red', lw=1.5, alpha=0.7, linestyle='dashed') 
                elif distribucion == "Poisson":
                    max_k_poisson = max(self.numeros_generados_distribucion) if self.numeros_generados_distribucion else int(params['mu'] * 3) + 1
                    k_values = np.arange(0, max_k_poisson + 1)
                    pmf = poisson.pmf(k_values, mu=params['mu'])
                    self.ax_distribucion.plot(k_values, pmf, 'ro', markersize=6, label="PMF Teórica")
                    self.ax_distribucion.vlines(k_values, 0, pmf, color='red', lw=1.5, alpha=0.7, linestyle='dashed') 
                elif distribucion == "Geométrica":
                    max_k_geom = max(self.numeros_generados_distribucion) if self.numeros_generados_distribucion else int(1/params['p'] * 3) + 1
                    k_values = np.arange(1, max_k_geom + 1)
                    pmf = geom.pmf(k_values, p=params['p'])
                    self.ax_distribucion.plot(k_values, pmf, 'ro', markersize=6, label="PMF Teórica")
                    self.ax_distribucion.vlines(k_values, 0, pmf, color='red', lw=1.5, alpha=0.7, linestyle='dashed') 
                
                self.ax_distribucion.xaxis.set_major_locator(plt.MaxNLocator(integer=True))
                
            self.ax_distribucion.legend()
        else:
            self.ax_distribucion.text(0.5, 0.5, "No hay datos para mostrar", horizontalalignment='center', verticalalignment='center', transform=self.ax_distribucion.transAxes, color=self.text_color)

        self.canvas_distribucion.draw()


if __name__ == "__main__":
    root = tk.Tk()
    app = GeneradorPseudoaleatorio(root)
    root.mainloop()