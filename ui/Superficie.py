# energia.py
import os, math, tempfile
import pygame
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ------------------ Paleta y helpers ------------------
def hex_to_rgb(h):  # "#rrggbb" -> (r,g,b)
    h = h.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def hex_to_rgba01(h, a=0.45):  # matplotlib 0..1
    r,g,b = hex_to_rgb(h)
    return (r/255.0, g/255.0, b/255.0, a)

PALETTE = {
    "sand":  "#eee5ca",
    "mars":  "#df8a5d",
    "moon":  "#496ca8",
    "navy":  "#223149",
    "white": "#ffffff",
    "black": "#000000",
}

WHITE = hex_to_rgb(PALETTE["white"])
BLACK = hex_to_rgb(PALETTE["black"])
SAND  = hex_to_rgb(PALETTE["sand"])
MARS  = hex_to_rgb(PALETTE["mars"])
MOON  = hex_to_rgb(PALETTE["moon"])
NAVY  = hex_to_rgb(PALETTE["navy"])

AREA_MARTE = hex_to_rgba01(PALETTE["mars"], 0.55)
AREA_LUNA  = hex_to_rgba01(PALETTE["moon"], 0.55)

pygame.init()
W, H = 1280, 720
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Energía solar anual — Marte o Luna")
clock = pygame.time.Clock()

# Imagen de fondo por cuerpo (ajusta nombres/ubicación si quieres)
BODY_IMAGES = {
    "Marte": "marte.jpg",
    "Luna":  "luna.jpg",
}
_loaded_bg = {"Marte": None, "Luna": None}

def load_body_bg(body, size):
    path = BODY_IMAGES.get(body)
    if not path or not os.path.exists(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.smoothscale(img, size)
    except Exception:
        return None

# ------------------ Globals requeridos ------------------
GLOBAL_YMAX = 1.0
GLOBAL_MIN_ENERGY = None

# ------------------ UI ------------------
def draw_text(surf, text, size, color, center=None, topleft=None):
    font = pygame.font.SysFont(None, size)
    txt = font.render(text, True, color)
    rect = txt.get_rect()
    if center: rect.center = center
    if topleft: rect.topleft = topleft
    surf.blit(txt, rect); return rect

def draw_button(surf, rect, label, fg=WHITE, bg=NAVY):
    pygame.draw.rect(surf, bg, rect, border_radius=12)
    draw_text(surf, label, 26, fg, center=rect.center)

def draw_slider(surf, rect, val_norm, active):
    pygame.draw.rect(surf, SAND, rect, border_radius=8)
    x0, x1 = rect.left + 12, rect.right - 12
    y = rect.centery
    pygame.draw.line(surf, NAVY, (x0, y), (x1, y), 4)
    xh = int(x0 + (x1 - x0) * val_norm)
    handle = pygame.Rect(0, 0, 20, 20); handle.center = (xh, y)
    pygame.draw.rect(surf, MARS if active else NAVY, handle, border_radius=10)
    return handle

def map_norm_to_lat(v): return -90.0 + 180.0 * max(0.0, min(1.0, v))

# ------------------ Física ------------------
import math
def declination_series(n_days, obliquity):
    eps = math.radians(obliquity)
    return [math.asin(math.sin(eps)*math.sin(2*math.pi*(d-80)/n_days)) for d in range(n_days)]

def daily_insolation(lat, delta, S0, tau):
    phi = math.radians(lat)
    x = -math.tan(phi)*math.tan(delta)
    if x <= -1: omega = math.pi
    elif x >= 1: return 0.0
    else: omega = math.acos(x)
    H = (S0/math.pi)*(omega*math.sin(phi)*math.sin(delta) + math.cos(phi)*math.cos(delta)*math.sin(omega))
    return max(0.0, H)*tau

def compute_series(body, lat):
    if body == "Marte":
        n, eps, S0, tau = 668, 25.19, 590, 0.72
    else:
        n, eps, S0, tau = 365, 1.54, 1361, 1.0
    deltas = declination_series(n, eps)
    y = [daily_insolation(lat, dlt, S0, tau) for dlt in deltas]
    return y, n

# ------------------ Gráfica ------------------
def plot_series_area_to_png(x, y, y_max_global, width_px, height_px, path, rgba_fill):
    dpi = 140
    fig_w = max(2, width_px/dpi); fig_h = max(2, height_px/dpi)
    plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    plt.fill_between(x, y, 0.0, color=rgba_fill)
    plt.ylim(0, y_max_global)         # 0..máximo global con margen
    plt.xlim(x[0], x[-1])
    P = x[-1]
    ticks = [0, P*0.25, P*0.5, P*0.75, P]
    plt.xticks([int(t) for t in ticks], [f"{int(t)}" for t in ticks])
    plt.xlabel("Día del periodo")
    plt.ylabel("Energía diaria (Wh/m²)")
    plt.margins(x=0.01, y=0.0)
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", pad_inches=0.05)
    plt.close()

# ------------------ Main ------------------
def main():
    global GLOBAL_YMAX, GLOBAL_MIN_ENERGY
    lat_norm = 0.5
    dragging = False
    body = "Marte"
    graph_surf = None
    tmp_path = os.path.join(tempfile.gettempdir(), f"energia_{os.getpid()}.png")

    running = True
    while running:
        dt = clock.tick(60)
        W, H = screen.get_size()

        # Layout
        margin = 100
        slider_rect = pygame.Rect(margin, 200, max(300, W - 2*margin), 44)
        btn_calc   = pygame.Rect(margin, 260, 200, 52)
        btn_body   = pygame.Rect(margin + 220, 260, 220, 52)
        btn_exit   = pygame.Rect(W - margin - 160, 260, 160, 52)
        graph_rect = pygame.Rect(margin, 340, max(300, W - 2*margin), max(220, H - 380))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.VIDEORESIZE:
                pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                graph_surf = None
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if slider_rect.collidepoint(e.pos):
                    dragging = True
                elif btn_calc.collidepoint(e.pos):
                    lat = map_norm_to_lat(lat_norm)
                    y, period = compute_series(body, lat)
                    y2 = y + [y[0]]
                    x2 = list(range(0, period + 1))

                    serie_max = max(y2) if y2 else 1.0
                    GLOBAL_MIN_ENERGY = min(y2) if y2 else 0.0
                    GLOBAL_YMAX = max(GLOBAL_YMAX, serie_max * 1.05)  # margen 5%

                    fill = AREA_MARTE if body == "Marte" else AREA_LUNA
                    plot_series_area_to_png(x2, y2, GLOBAL_YMAX, graph_rect.width, graph_rect.height, tmp_path, fill)
                    if os.path.exists(tmp_path):
                        img = pygame.image.load(tmp_path)
                        if img.get_width()!=graph_rect.width or img.get_height()!=graph_rect.height:
                            img = pygame.transform.smoothscale(img, (graph_rect.width, graph_rect.height))
                        graph_surf = img
                elif btn_body.collidepoint(e.pos):
                    body = "Luna" if body == "Marte" else "Marte"
                    graph_surf = None
                elif btn_exit.collidepoint(e.pos):
                    running = False
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                dragging = False
            elif e.type == pygame.MOUSEMOTION and dragging:
                x0, x1 = slider_rect.left+12, slider_rect.right-12
                if x1 > x0:
                    lat_norm = max(0, min(1, (e.pos[0]-x0)/float(x1-x0)))

        # Fondo con imagen del cuerpo y velo para contraste
        bg = _loaded_bg.get(body)
        if not bg or bg.get_size() != (W, H):
            bg = load_body_bg(body, (W, H))
            _loaded_bg[body] = bg
        if bg: screen.blit(bg, (0,0))
        else: screen.fill(SAND)
        veil = pygame.Surface((W, H), pygame.SRCALPHA); veil.fill((*SAND, 80))
        screen.blit(veil, (0,0))

        # Encabezado
        draw_text(screen, "Herramienta de energía solar anual", 40, NAVY, center=(W//2, 90))
        draw_text(screen, f"Cuerpo: {body}", 28, NAVY, topleft=(margin, 140))
        draw_text(screen, f"Latitud: {map_norm_to_lat(lat_norm):+.1f}°", 28, NAVY, topleft=(margin, 170))
        if GLOBAL_MIN_ENERGY is not None:
            draw_text(screen, f"Energía mínima: {GLOBAL_MIN_ENERGY:.1f} Wh/m²", 22, NAVY, topleft=(margin, 310))

        # Controles
        draw_slider(screen, slider_rect, lat_norm, dragging)
        draw_button(screen, btn_calc, "Calcular", fg=WHITE, bg=NAVY)
        draw_button(screen, btn_body, f"Cambiar ({body})", fg=WHITE, bg=MARS if body=="Marte" else MOON)
        draw_button(screen, btn_exit, "Salir", fg=WHITE, bg=NAVY)

        # Gráfico
        if graph_surf:
            if graph_surf.get_width()!=graph_rect.width or graph_surf.get_height()!=graph_rect.height:
                graph_surf = pygame.transform.smoothscale(graph_surf, (graph_rect.width, graph_rect.height))
            # marco suave
            frame = pygame.Surface((graph_rect.width+12, graph_rect.height+12), pygame.SRCALPHA)
            pygame.draw.rect(frame, (*NAVY, 40), frame.get_rect(), border_radius=16)
            screen.blit(frame, (graph_rect.left-6, graph_rect.top-6))
            screen.blit(graph_surf, graph_rect.topleft)

        pygame.display.flip()

    try:
        if os.path.exists(tmp_path): os.remove(tmp_path)
    except: pass
    pygame.quit()

if __name__ == "__main__":
    main()

"ola"
