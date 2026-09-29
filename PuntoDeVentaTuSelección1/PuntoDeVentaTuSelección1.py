import os
import re
import tkinter as tk
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from tkinter import messagebox, ttk

# ----------------------------- CONFIGURACIÓN -----------------------------
NOMBRE_NEGOCIO = "Gasolinería El Sol"
IVA_TASA = Decimal("0.16")  # 16 %
PRODUCTOS = {
    "Magna": Decimal("22.50"),
    "Premium": Decimal("24.80"),
    "Diésel": Decimal("23.90"),
}
CARPETA = os.path.dirname(os.path.abspath(__file__))

# Colores típicos de gasolinera
ROJO = "#D32F2F"
AMARILLO = "#FFC107"
AZUL = "#0D2B55"
BLANCO = "#FFFFFF"
FONDO = "#F4F6F8"
GRIS = "#ECEFF1"
COLOR_PRODUCTO = {"Magna": "#2E7D32", "Premium": "#C62828", "Diésel": "#212121"}

FUENTE = "Arial"


# ------------------------------- UTILIDADES -------------------------------
def redondear(valor: Decimal) -> Decimal:
    return valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def dinero(valor: Decimal) -> str:
    return f"${valor:,.2f}"


def siguiente_folio() -> str:
    """Busca los archivos venta_XXXX.txt existentes y devuelve el siguiente folio."""
    mayor = 0
    for nombre in os.listdir(CARPETA):
        m = re.fullmatch(r"venta_(\d+)\.txt", nombre)
        if m:
            mayor = max(mayor, int(m.group(1)))
    return f"{mayor + 1:04d}"


def crear_icono() -> tk.PhotoImage:
    """Dibuja un pequeño icono de bomba de gasolina (sin archivos externos)."""
    img = tk.PhotoImage(width=64, height=64)
    img.put(ROJO, to=(0, 0, 64, 64))          # fondo
    img.put(AMARILLO, to=(14, 10, 42, 56))    # cuerpo de la bomba
    img.put(AZUL, to=(18, 14, 38, 28))        # pantalla
    img.put(BLANCO, to=(10, 56, 46, 60))      # base
    img.put(BLANCO, to=(42, 20, 50, 24))      # manguera (horizontal)
    img.put(BLANCO, to=(48, 20, 52, 46))      # manguera (vertical)
    img.put(AZUL, to=(46, 46, 54, 50))        # boquilla
    return img


# ------------------------------- APLICACIÓN -------------------------------
class GasolineriaApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title(f"{NOMBRE_NEGOCIO} - Registro de ventas")
        root.configure(bg=FONDO)
        ancho, alto = 760, 720
        x = (root.winfo_screenwidth() - ancho) // 2
        y = max((root.winfo_screenheight() - alto) // 2 - 20, 0)
        root.geometry(f"{ancho}x{alto}+{x}+{y}")
        root.resizable(False, False)

        self.icono = crear_icono()  # referencia para que no se elimine
        root.iconphoto(True, self.icono)

        # Variables del formulario
        self.folio = tk.StringVar()
        self.fecha = tk.StringVar()
        self.usuario = tk.StringVar()
        self.cliente = tk.StringVar()
        self.producto = tk.StringVar()
        self.precio = tk.StringVar()
        self.litros = tk.StringVar()
        self.subtotal = tk.StringVar()
        self.iva = tk.StringVar()
        self.total = tk.StringVar()

        self._construir_interfaz()

        # Cálculo automático al cambiar producto o litros
        self.producto.trace_add("write", self.calcular)
        self.litros.trace_add("write", self.calcular)

        self.limpiar()

    # ------------------------------ Interfaz ------------------------------
    def _construir_interfaz(self):
        # Encabezado
        encabezado = tk.Frame(self.root, bg=ROJO)
        encabezado.pack(fill="x")
        tk.Label(encabezado, text=NOMBRE_NEGOCIO.upper(), bg=ROJO, fg=AMARILLO,
                 font=(FUENTE, 26, "bold")).pack(pady=(14, 0))
        tk.Label(encabezado, text="Registro de ventas del día", bg=ROJO, fg=BLANCO,
                 font=(FUENTE, 13, "italic")).pack(pady=(0, 12))
        tk.Frame(self.root, bg=AMARILLO, height=6).pack(fill="x")

        # Panel de precios
        precios = tk.Frame(self.root, bg=FONDO)
        precios.pack(fill="x", padx=25, pady=(14, 4))
        for i, (nombre, precio) in enumerate(PRODUCTOS.items()):
            precios.columnconfigure(i, weight=1)
            tk.Label(precios, text=f"{nombre}\n{dinero(precio)} / L", bg=COLOR_PRODUCTO[nombre],
                     fg=BLANCO, font=(FUENTE, 12, "bold"), pady=6
                     ).grid(row=0, column=i, sticky="ew", padx=4)

        # Formulario
        tarjeta = tk.LabelFrame(self.root, text=" Datos de la venta ", bg=BLANCO, fg=AZUL,
                                font=(FUENTE, 13, "bold"), padx=20, pady=12, bd=2, relief="groove")
        tarjeta.pack(fill="x", padx=25, pady=10)
        tarjeta.columnconfigure(1, weight=1)
        self.tarjeta = tarjeta

        self._campo(0, "Folio de venta:", self.folio, solo_lectura=True)
        self._campo(1, "Fecha:", self.fecha, solo_lectura=True)
        self.entry_usuario = self._campo(2, "Usuario de venta:", self.usuario)
        self._campo(3, "Cliente:", self.cliente)

        # Producto (lista desplegable)
        self._etiqueta(4, "Producto:")
        estilo = ttk.Style()
        estilo.theme_use("clam")
        estilo.configure("TCombobox", fieldbackground=BLANCO, background=AMARILLO,
                         foreground=AZUL, arrowcolor=AZUL)
        self.combo = ttk.Combobox(tarjeta, textvariable=self.producto, values=list(PRODUCTOS),
                                  state="readonly", font=(FUENTE, 12))
        self.combo.grid(row=4, column=1, sticky="ew", pady=5, padx=(10, 0))

        self._campo(5, "Precio por litro:", self.precio, solo_lectura=True)
        self.entry_litros = self._campo(6, "Litros:", self.litros)
        self._campo(7, "Subtotal:", self.subtotal, solo_lectura=True)
        self._campo(8, f"IVA ({int(IVA_TASA * 100)} %):", self.iva, solo_lectura=True)
        self._campo(9, "TOTAL:", self.total, solo_lectura=True, negrita=True, color=ROJO)

        # Botones
        botones = tk.Frame(self.root, bg=FONDO)
        botones.pack(pady=8)
        tk.Button(botones, text="Limpiar", command=self.limpiar, bg=AZUL, fg=BLANCO,
                  activebackground="#173F7A", activeforeground=BLANCO,
                  font=(FUENTE, 13, "bold"), width=14, pady=6, relief="flat",
                  cursor="hand2").grid(row=0, column=0, padx=12)
        tk.Button(botones, text="Guardar venta", command=self.guardar, bg=ROJO, fg=BLANCO,
                  activebackground="#B71C1C", activeforeground=BLANCO,
                  font=(FUENTE, 13, "bold"), width=14, pady=6, relief="flat",
                  cursor="hand2").grid(row=0, column=1, padx=12)

    def _etiqueta(self, fila, texto):
        tk.Label(self.tarjeta, text=texto, bg=BLANCO, fg=AZUL, font=(FUENTE, 12, "bold"),
                 anchor="w").grid(row=fila, column=0, sticky="w", pady=5)

    def _campo(self, fila, texto, variable, solo_lectura=False, negrita=False, color=AZUL):
        self._etiqueta(fila, texto)
        entry = tk.Entry(self.tarjeta, textvariable=variable, font=(FUENTE, 13 if negrita else 12,
                         "bold" if negrita else "normal"), fg=color, relief="solid", bd=1,
                         readonlybackground=GRIS, state="readonly" if solo_lectura else "normal")
        entry.grid(row=fila, column=1, sticky="ew", pady=5, padx=(10, 0), ipady=3)
        return entry

    # ------------------------------ Lógica ------------------------------
    def _leer_litros(self):
        texto = self.litros.get().strip().replace(",", ".")
        if not texto:
            return None
        try:
            valor = Decimal(texto)
        except InvalidOperation:
            return None
        if not valor.is_finite() or valor <= 0 or valor > Decimal("100000"):
            return None
        return valor

    def _importes(self):
        """Devuelve (precio, litros, subtotal, iva, total) o None si faltan datos válidos."""
        precio = PRODUCTOS.get(self.producto.get())
        litros = self._leer_litros()
        if precio is None or litros is None:
            return None
        subtotal = redondear(precio * litros)
        iva = redondear(subtotal * IVA_TASA)
        return precio, litros, subtotal, iva, subtotal + iva

    def calcular(self, *_):
        precio = PRODUCTOS.get(self.producto.get())
        self.precio.set(dinero(precio) if precio is not None else "")
        datos = self._importes()
        if datos is None:
            self.subtotal.set(dinero(Decimal("0")))
            self.iva.set(dinero(Decimal("0")))
            self.total.set(dinero(Decimal("0")))
            return
        _, _, subtotal, iva, total = datos
        self.subtotal.set(dinero(subtotal))
        self.iva.set(dinero(iva))
        self.total.set(dinero(total))

    def limpiar(self):
        """Limpia el formulario y prepara una nueva venta."""
        self.usuario.set("")
        self.cliente.set("")
        self.producto.set("")
        self.litros.set("")
        self.folio.set(siguiente_folio())
        self.fecha.set(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
        self.calcular()
        self.entry_usuario.focus_set()

    def guardar(self):
        """Valida los datos y guarda la venta en un TXT independiente."""
        usuario = self.usuario.get().strip()
        cliente = self.cliente.get().strip()

        if not usuario:
            messagebox.showwarning("Dato faltante", "Escribe el usuario de venta.")
            self.entry_usuario.focus_set()
            return
        if not cliente:
            messagebox.showwarning("Dato faltante", "Escribe el nombre del cliente.")
            return
        if self.producto.get() not in PRODUCTOS:
            messagebox.showwarning("Dato faltante", "Selecciona un producto.")
            return
        datos = self._importes()
        if datos is None:
            messagebox.showwarning("Litros no válidos",
                                   "Escribe una cantidad de litros válida (mayor que 0).")
            self.entry_litros.focus_set()
            return

        precio, litros, subtotal, iva, total = datos
        folio = siguiente_folio()
        fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        self.folio.set(folio)
        self.fecha.set(fecha)

        ruta = os.path.join(CARPETA, f"venta_{folio}.txt")
        contenido = (
            f"{NOMBRE_NEGOCIO.upper()}\n"
            "COMPROBANTE DE VENTA\n"
            "========================================\n"
            f"Folio de venta   : {folio}\n"
            f"Fecha            : {fecha}\n"
            f"Usuario de venta : {usuario}\n"
            f"Cliente          : {cliente}\n"
            "----------------------------------------\n"
            f"Producto         : {self.producto.get()}\n"
            f"Precio por litro : {dinero(precio)}\n"
            f"Litros           : {litros.normalize():f}\n"
            "----------------------------------------\n"
            f"Subtotal         : {dinero(subtotal)}\n"
            f"IVA ({int(IVA_TASA * 100)} %)        : {dinero(iva)}\n"
            f"TOTAL            : {dinero(total)}\n"
            "========================================\n"
        )

        try:
            with open(ruta, "x", encoding="utf-8") as archivo:  # "x": nunca sobrescribe
                archivo.write(contenido)
        except FileExistsError:
            messagebox.showerror("Error", "Ya existe un archivo con ese folio. Intenta de nuevo.")
            self.limpiar()
            return
        except OSError as error:
            messagebox.showerror("Error al guardar", f"No se pudo guardar la venta:\n{error}")
            return

        messagebox.showinfo("Venta guardada",
                            f"Folio: {folio}\nTotal: {dinero(total)}\n\nArchivo: {os.path.basename(ruta)}")
        self.limpiar()


if __name__ == "__main__":
    ventana = tk.Tk()
    GasolineriaApp(ventana)
    ventana.mainloop()
