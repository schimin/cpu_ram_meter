import tkinter as tk
import math
import psutil
import sys

# ── Configurações ──────────────────────────────────────────
WIN_SIZE   = 220          # tamanho da janela (quadrado)
WIN_ALPHA  = 0.96         # transparência (0.0 – 1.0)
UPDATE_MS  = 1000         # atualização em milissegundos
DRAG_BTN   = "<B1-Motion>"

# Cores
BG_OUTER   = "#d0d0d0"
BG_INNER   = "#f0f0f0"
TICK_MAJOR = "#888888"
TICK_MINOR = "#bbbbbb"
ARC_BG     = "#c8c8c8"
ARC_CPU    = "#333333"
TEXT_LABEL = "#777777"
TEXT_VALUE = "#222222"
TEXT_RAM   = "#555555"

# Geometria do gauge
CX, CY     = WIN_SIZE // 2, WIN_SIZE // 2
RADIUS     = 85
ARC_START  = 225          # graus (sentido Tkinter: 0=leste, anti-horário)
ARC_EXTENT = 270          # varredura total

# ── Funções auxiliares ─────────────────────────────────────

def deg_to_tk(deg):
    """Converte grau 'matemático' para grau Tkinter (anti-horário a partir do leste)."""
    return deg  # já estamos usando sistema Tkinter

def value_to_angle(value, min_v=0, max_v=100):
    """Converte 0-100 para ângulo dentro do arco."""
    fraction = max(0.0, min(1.0, value / (max_v - min_v)))
    return ARC_START - fraction * ARC_EXTENT   # decresce (anti-horário = aumenta no Tkinter)

def polar(cx, cy, r, angle_deg):
    """Ponto na circunferência dado ângulo em graus (0=leste, anti-horário)."""
    rad = math.radians(angle_deg)
    return cx + r * math.cos(rad), cy - r * math.sin(rad)

def draw_ticks(canvas, cx, cy, r_inner, r_outer, n, color, width=1):
    for i in range(n + 1):
        angle = ARC_START - (i / n) * ARC_EXTENT
        x1, y1 = polar(cx, cy, r_inner, angle)
        x2, y2 = polar(cx, cy, r_outer, angle)
        canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

# ── Janela e canvas ────────────────────────────────────────

root = tk.Tk()
root.title("Monitor")
root.geometry(f"{WIN_SIZE}x{WIN_SIZE}+100+100")
root.resizable(False, False)
root.overrideredirect(True)          # sem borda
root.attributes("-topmost", True)    # sempre no topo
root.attributes("-alpha", WIN_ALPHA)

# Fundo transparente (Windows)
if sys.platform == "win32":
    root.attributes("-transparentcolor", "")

canvas = tk.Canvas(root, width=WIN_SIZE, height=WIN_SIZE,
                   bg=BG_OUTER, highlightthickness=0)
canvas.pack()

# ── Arrastar janela ────────────────────────────────────────
_drag = {"x": 0, "y": 0}

def on_press(e):
    _drag["x"] = e.x
    _drag["y"] = e.y

def on_drag(e):
    dx = e.x - _drag["x"]
    dy = e.y - _drag["y"]
    x  = root.winfo_x() + dx
    y  = root.winfo_y() + dy
    root.geometry(f"+{x}+{y}")

canvas.bind("<ButtonPress-1>", on_press)
canvas.bind(DRAG_BTN, on_drag)

# Fechar com duplo-clique
canvas.bind("<Double-Button-1>", lambda e: root.destroy())

# ── Desenho estático (fundo, ticks, círculos) ──────────────

def draw_static():
    canvas.delete("static")

    # Círculo externo (moldura)
    m = 4
    canvas.create_oval(m, m, WIN_SIZE - m, WIN_SIZE - m,
                       fill=BG_OUTER, outline="#b0b0b0", width=2, tags="static")

    # Círculo interno (face)
    pad = 18
    canvas.create_oval(pad, pad, WIN_SIZE - pad, WIN_SIZE - pad,
                       fill=BG_INNER, outline="#c8c8c8", width=1, tags="static")

    # Ticks menores
    draw_ticks(canvas, CX, CY, RADIUS + 4, RADIUS + 9,  50, TICK_MINOR, 1)
    # Ticks maiores
    draw_ticks(canvas, CX, CY, RADIUS + 4, RADIUS + 13, 10, TICK_MAJOR, 2)

draw_static()

# ── Elementos dinâmicos ────────────────────────────────────

# IDs dos items dinâmicos
arc_bg_id  = canvas.create_arc(CX - RADIUS, CY - RADIUS,
                                CX + RADIUS, CY + RADIUS,
                                start=ARC_START - ARC_EXTENT,
                                extent=ARC_EXTENT,
                                style=tk.ARC,
                                outline=ARC_BG, width=6)

arc_cpu_id = canvas.create_arc(CX - RADIUS, CY - RADIUS,
                                CX + RADIUS, CY + RADIUS,
                                start=ARC_START - ARC_EXTENT,
                                extent=1,
                                style=tk.ARC,
                                outline=ARC_CPU, width=6)

lbl_cpu_id = canvas.create_text(CX, CY - 22, text="CPU %",
                                 font=("Segoe UI", 11, "normal"),
                                 fill=TEXT_LABEL)

val_cpu_id = canvas.create_text(CX, CY + 8,  text="0",
                                 font=("Segoe UI", 36, "bold"),
                                 fill=TEXT_VALUE)

lbl_ram_id = canvas.create_text(CX, CY + 38, text="RAM 0 %",
                                 font=("Segoe UI", 11, "normal"),
                                 fill=TEXT_RAM)

# ── Loop de atualização ────────────────────────────────────

def update():
    cpu = psutil.cpu_percent(interval=None)
    ram = psutil.virtual_memory().percent

    # Arco CPU
    extent = (cpu / 100) * ARC_EXTENT
    if extent < 1:
        extent = 1   # evita bug de arco "cheio" com extent=0
    canvas.itemconfig(arc_cpu_id, extent=extent)

    # Textos
    canvas.itemconfig(val_cpu_id, text=str(int(cpu)))
    canvas.itemconfig(lbl_ram_id, text=f"RAM {int(ram)} %")

    root.after(UPDATE_MS, update)

update()
root.mainloop()