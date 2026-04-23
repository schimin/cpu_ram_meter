import tkinter as tk
import math
import psutil
import sys

# ── Configurações Iniciais ──────────────────────────────────
WIN_SIZE   = 220          # tamanho inicial
WIN_ALPHA  = 0.96         # transparência
UPDATE_MS  = 1000         # atualização
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
COLOR_DANGER = "#e74c3c"

# ── Variáveis Globais de Controle ───────────────────────────
current_size = WIN_SIZE
disk_labels = []
browser_val_id = None

# ── Funções de Métricas ──────────────────────────────────────

def get_browser_memory():
    browsers = ["chrome.exe", "firefox.exe", "msedge.exe", "brave.exe", "opera.exe", "browser.exe"]
    total_mem = 0
    found = False
    for proc in psutil.process_iter(['name', 'memory_info']):
        try:
            name = proc.info['name']
            if name and name.lower() in browsers:
                total_mem += proc.info['memory_info'].rss
                found = True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if not found:
        return "", 0
        
    mb = total_mem / (1024 * 1024)
    if mb < 1000:
        text = f"{int(mb)}Mb"
    else:
        text = f"{total_mem / (1024**3):.1f}Gb"
    
    total_system_ram = psutil.virtual_memory().total
    percent = (total_mem / total_system_ram) * 100
    return text, percent

# ── Funções de Desenho e Geometria ─────────────────────────

def polar(cx, cy, r, angle_deg):
    rad = math.radians(angle_deg)
    return cx + r * math.cos(rad), cy - r * math.sin(rad)

def draw_ticks(canvas, cx, cy, r_inner, r_outer, n, color, width=1):
    for i in range(n + 1):
        angle = 225 - (i / n) * 270
        x1, y1 = polar(cx, cy, r_inner, angle)
        x2, y2 = polar(cx, cy, r_outer, angle)
        canvas.create_line(x1, y1, x2, y2, fill=color, width=width, tags="static")

def redraw_ui():
    """Redesenha toda a interface baseada no tamanho atual."""
    global CX, CY, RADIUS, ARC_START, ARC_EXTENT
    canvas.delete("all")
    
    CX, CY = current_size // 2, current_size // 2
    RADIUS = int(85 * (current_size / 220))
    ARC_START = 225
    ARC_EXTENT = 270
    
    scale = current_size / 220

    # Círculo externo
    m = 4 * scale
    canvas.create_oval(m, m, current_size - m, current_size - m,
                       fill=BG_OUTER, outline="#b0b0b0", width=2*scale, tags="static")

    # Círculo interno
    pad = 18 * scale
    canvas.create_oval(pad, pad, current_size - pad, current_size - pad,
                       fill=BG_INNER, outline="#c8c8c8", width=1*scale, tags="static")

    # Ticks
    draw_ticks(canvas, CX, CY, RADIUS + (4*scale), RADIUS + (9*scale),  50, TICK_MINOR, 1)
    draw_ticks(canvas, CX, CY, RADIUS + (4*scale), RADIUS + (13*scale), 10, TICK_MAJOR, max(1, int(2*scale)))

    # Elementos dinâmicos
    global arc_cpu_id, arc_ram_id, arc_ram_browser_id, val_cpu_id, lbl_ram_id, browser_val_id, disk_labels
    
    # ── Indicador CPU (Grande) ──────────────────────────────
    # Arco fundo
    canvas.create_arc(CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS,
                      start=ARC_START - ARC_EXTENT, extent=ARC_EXTENT,
                      style=tk.ARC, outline=ARC_BG, width=6*scale)

    # Arco CPU
    arc_cpu_id = canvas.create_arc(CX - RADIUS, CY - RADIUS, CX + RADIUS, CY + RADIUS,
                                   start=ARC_START - ARC_EXTENT, extent=1,
                                   style=tk.ARC, outline=ARC_CPU, width=6*scale)

    canvas.create_text(CX, CY - (52*scale), text="CPU %",
                       font=("Segoe UI", int(11*scale), "normal"), fill=TEXT_LABEL)

    val_cpu_id = canvas.create_text(CX, CY - (22*scale), text="0",
                                   font=("Segoe UI", int(40*scale), "bold"), fill=TEXT_VALUE)

    # ── Indicador RAM (Aumentado) ───────────────────────────
    R_RADIUS = 30 * scale
    R_CX, R_CY = CX, CY + (48 * scale)
    
    # Arco fundo RAM
    canvas.create_arc(R_CX - R_RADIUS, R_CY - R_RADIUS, R_CX + R_RADIUS, R_CY + R_RADIUS,
                      start=ARC_START - ARC_EXTENT, extent=ARC_EXTENT,
                      style=tk.ARC, outline=ARC_BG, width=5*scale)

    # Arco RAM Dinâmico (Sistema/Base)
    arc_ram_id = canvas.create_arc(R_CX - R_RADIUS, R_CY - R_RADIUS, R_CX + R_RADIUS, R_CY + R_RADIUS,
                                   start=ARC_START - ARC_EXTENT, extent=1,
                                   style=tk.ARC, outline=TEXT_RAM, width=5*scale)
    
    # Arco RAM Dinâmico (Navegador - em Vermelho)
    arc_ram_browser_id = canvas.create_arc(R_CX - R_RADIUS, R_CY - R_RADIUS, R_CX + R_RADIUS, R_CY + R_RADIUS,
                                   start=ARC_START - ARC_EXTENT, extent=1,
                                   style=tk.ARC, outline=COLOR_DANGER, width=5*scale)

    canvas.create_text(R_CX, R_CY - (14*scale), text="RAM %",
                       font=("Segoe UI", int(8*scale), "normal"), fill=TEXT_LABEL)

    lbl_ram_id = canvas.create_text(R_CX, R_CY - (1*scale), text="0",
                                   font=("Segoe UI", int(18*scale), "bold"), fill=TEXT_RAM)

    # UI do Navegador embutida na RAM (ícone pequeno + valor)
    ix_emb = R_CX - (15 * scale)
    iy_emb = R_CY + (14 * scale)
    ir_emb = 4 * scale
    
    # Desenho do ícone (tag 'browser_ui' para controle de visibilidade)
    canvas.create_arc(ix_emb-ir_emb, iy_emb-ir_emb, ix_emb+ir_emb, iy_emb+ir_emb, start=90, extent=120, fill="#DB4437", outline="", tags="browser_ui")
    canvas.create_arc(ix_emb-ir_emb, iy_emb-ir_emb, ix_emb+ir_emb, iy_emb+ir_emb, start=210, extent=120, fill="#0F9D58", outline="", tags="browser_ui")
    canvas.create_arc(ix_emb-ir_emb, iy_emb-ir_emb, ix_emb+ir_emb, iy_emb+ir_emb, start=330, extent=120, fill="#F4B400", outline="", tags="browser_ui")
    cr_emb = ir_emb * 0.4
    canvas.create_oval(ix_emb-cr_emb, iy_emb-cr_emb, ix_emb+cr_emb, iy_emb+cr_emb, fill="#4285F4", outline="#f0f0f0", width=1, tags="browser_ui")

    browser_val_id = canvas.create_text(ix_emb + ir_emb + (2*scale), iy_emb, text="",
                                       font=("Segoe UI", int(7*scale), "bold"), 
                                       fill=COLOR_DANGER, anchor="w", tags="browser_ui")

    # Discos na horizontal (Ajustado para o limite inferior)
    disk_labels = []
    try:
        partitions = []
        seen = set()
        for p in psutil.disk_partitions():
            if 'fixed' in p.opts and p.mountpoint not in seen:
                partitions.append(p.mountpoint)
                seen.add(p.mountpoint)
        if not partitions: partitions = ['C:\\']
    except:
        partitions = ['C:\\']
    
    n_disks = len(partitions)
    y_pos = current_size - (10 * scale)
    
    for i, p in enumerate(partitions):
        # Distribui horizontalmente
        x_pos = (current_size / (n_disks + 1)) * (i + 1)
        lbl_id = canvas.create_text(x_pos, y_pos, text=f"HD{i+1} 0%",
                                     font=("Segoe UI", int(8*scale), "bold"),
                                     fill=TEXT_RAM)
        disk_labels.append((lbl_id, p))

# ── Janela e Eventos ────────────────────────────────────────

root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)
root.attributes("-alpha", WIN_ALPHA)

canvas = tk.Canvas(root, bg=BG_OUTER, highlightthickness=0)
canvas.pack(fill=tk.BOTH, expand=True)

def on_mouse_wheel(event):
    global current_size
    # No Windows, event.delta é 120 ou -120
    if event.delta > 0:
        current_size = min(600, current_size + 20)
    else:
        current_size = max(120, current_size - 20)
    
    root.geometry(f"{current_size}x{current_size}")
    redraw_ui()
    # update() removido daqui para evitar múltiplos loops

root.bind("<MouseWheel>", on_mouse_wheel)

# Arrastar
_drag = {"x": 0, "y": 0}
def on_press(e):
    _drag["x"] = e.x
    _drag["y"] = e.y
def on_drag(e):
    dx, dy = e.x - _drag["x"], e.y - _drag["y"]
    root.geometry(f"+{root.winfo_x() + dx}+{root.winfo_y() + dy}")

canvas.bind("<ButtonPress-1>", on_press)
canvas.bind(DRAG_BTN, on_drag)
canvas.bind("<Double-Button-1>", lambda e: root.destroy())

# ── Loop de Atualização ────────────────────────────────────

def update():
    try:
        cpu = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory().percent

        cpu_color = COLOR_DANGER if cpu > 90 else ARC_CPU
        extent = max(1, (cpu / 100) * 270)
        
        canvas.itemconfig(arc_cpu_id, extent=extent, outline=cpu_color)
        canvas.itemconfig(val_cpu_id, text=str(int(cpu)), fill=cpu_color)
        
        # Update RAM Indicator (Merged System + Browser)
        browser_text, b_percent = get_browser_memory()
        
        # total_ram = ram
        # s_percent = RAM do sistema (Total - Navegador)
        s_percent = max(0, ram - b_percent)
        
        ext_s = (s_percent / 100) * 270
        ext_b = (b_percent / 100) * 270
        
        # Cor de perigo se o TOTAL passar de 90%
        main_ram_color = COLOR_DANGER if ram > 90 else TEXT_RAM
        
        # Atualiza Arco Sistema (Preto/Base)
        canvas.itemconfig(arc_ram_id, extent=max(0.1, ext_s), outline=main_ram_color)
        
        # Atualiza Arco Navegador (Vermelho) - começa onde o do sistema termina
        start_b = (ARC_START - ARC_EXTENT) + ext_s
        canvas.itemconfig(arc_ram_browser_id, start=start_b, extent=max(0.1, ext_b) if b_percent > 0 else 0)
        
        canvas.itemconfig(lbl_ram_id, text=str(int(ram)), fill=main_ram_color)

        # Update Browser Icon & Mini-Text
        if browser_text:
            canvas.itemconfig(browser_val_id, text=f"{int(b_percent)}%")
            canvas.itemconfig("browser_ui", state="normal")
        else:
            canvas.itemconfig("browser_ui", state="hidden")

        for lbl_id, path in disk_labels:
            try:
                usage = psutil.disk_usage(path).percent
                color = COLOR_DANGER if usage > 95 else TEXT_RAM
                idx = [x[0] for x in disk_labels].index(lbl_id)
                canvas.itemconfig(lbl_id, text=f"HD{idx+1} {int(usage)} %", fill=color)
            except: pass
    except: pass

    root.after(UPDATE_MS, update)

# Inicialização
root.geometry(f"{current_size}x{current_size}+100+100")
redraw_ui()
update()
root.mainloop()
