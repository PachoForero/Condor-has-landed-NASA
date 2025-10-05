# energia.py
import os
import math
import tempfile
import pygame
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ------------------ Colores y ventana ------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (210, 210, 210)
BLUE  = (30, 144, 255)
GREEN = (40, 180, 120)
RED   = (200, 60, 60)
DARK  = (34, 49, 73)

pygame.init()
W, H = 1280, 720
screen = pygame.display.set_mode((W, H), pygame.RESIZABLE)
pygame.display.set_caption("Energía solar anual — Marte o Luna")
clock = pygame.time.Clock()

# ------------------ Utilidades UI ------------------
def draw_text(surf, text, size, color, center=None, topleft=None):
    font = pygame.font.SysFont(None, size)
    txt = font.render(text, True, color)
    rect = txt.get_rect()
    if center: rect.center = center
    if topleft: rect.topleft = topleft
    surf.blit(txt, rect)
    return rect

def draw_button(surf, rect, label, fg=WHITE, bg=BLACK):
    pygame.draw.rect(surf, bg, rect, border_radius=10)
    draw_text(surf, label, 26, fg, center=rect.center)

def draw_slider(surf, rect, val_norm, active):
    pygame.draw.rect(surf, GRAY, rect, border_radius=6)
    x0, x1 = rect.left + 10, rect.right - 10
    y = rect.centery
    pygame.draw.line(surf, BLACK, (x0, y), (x1, y), 3)
    xh = int(x0 + (x1 - x0) * val_norm)
    handle = pygame.Rect(0, 0, 18, 18)
    handle.center = (xh, y)
    pygame.draw.rect(surf, BLUE if active else BLACK, handle, border_radius=9)
    return handle

def map_norm_to_lat(v): return -90.0 + 180.0 * max(0.0, min(1.0, v))
def map_lat_to_norm(lat): return (lat + 90.0) / 180.0

# ------------------ Física ------------------
def declination_series(n_days, obliquity):
    eps = math.radians(obliquity)
    return [math.asin(math.sin(eps) * math.sin(2 * math.pi * (d - 80) / n_days)) for d in range(n_days)]

def daily_insolation(lat, delta, S0, tau):
    phi = math.radians(lat)
    x = -math.tan(phi) * math.tan(delta)
    if x <= -1: omega = math.pi
    elif x >= 1: return 0.0
    else: omega = math.acos(x)
    H = (S0 / math.pi) * (omega * math.sin(phi) * math.sin(delta) + math.cos(phi) * math.cos(delta) * math.sin(omega))
    return max(0.0, H) * tau

def compute_series(body, lat):
    if body == "Marte":
        n, eps, S0, tau = 668, 25.19, 590, 0.72
    else:
        n, eps, S0, tau = 365, 1.54, 1361, 1.0
    deltas = declination_series(n, eps)
    y = [daily_insolation(lat, dlt, S0, tau) for dlt in deltas]
    return y, n  # serie y período (días)

# ------------------ Gráfica (sin grid y sin título) ------------------
def plot_series_to_png(x, y, ymax, width_px, height_px, path):
    dpi = 140
    fig_w = max(2, width_px / dpi)
    fig_h = max(2, height_px / dpi)
    plt.figure(figsize=(fig_w, fig_h), dpi=dpi)
    plt.plot(x, y)
    plt.ylim(0, ymax)             # Y fijo 0..ymax
    plt.xlim(x[0], x[-1])         # 0..periodo
    # Sin título ni grid
    P = x[-1]
    ticks = [0, P*0.25, P*0.5, P*0.75, P]
    plt.xticks([int(t) for t in ticks], [f"{int(t)}" for t in ticks])
    plt.xlabel("Día del periodo")
    plt.ylabel("Energía diaria (Wh/m²)")
    plt.tight_layout()
    plt.savefig(path, bbox_inches="tight", pad_inches=0.05)
    plt.close()

# ------------------ Main ------------------
def main():
    global screen  # <- imprescindible si reasignas screen al redimensionar
    lat_norm = 0.5
    dragging = False
    body = "Marte"
    graph_surf = None
    tmp_path = os.path.join(tempfile.gettempdir(), f"energia_{os.getpid()}.png")

    running = True
    while running:
        dt = clock.tick(60)

        # Superficie y layout actuales
        W, H = screen.get_size()
        top_y = 80
        slider_rect = pygame.Rect(100, 200, max(240, W - 200), 40)
        btn_calc   = pygame.Rect(100, 260, 200, 50)
        btn_body   = pygame.Rect(320, 260, 220, 50)
        btn_exit   = pygame.Rect(max(100, W - 260), 260, 160, 50)
        graph_rect = pygame.Rect(100, 340, max(240, W - 200), max(200, H - 380))

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((e.w, e.h), pygame.RESIZABLE)
                graph_surf = None  # forzar re-render al nuevo tamaño

            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if slider_rect.collidepoint(e.pos):
                    dragging = True

                elif btn_calc.collidepoint(e.pos):
                    lat = map_norm_to_lat(lat_norm)
                    y, period = compute_series(body, lat)

                    # Cerrar ciclo para que se vea el periodo completo [0..P]
                    y2 = y + [y[0]]
                    x2 = list(range(0, period + 1))

                    ymax = max(y2) if y2 else 1.0

                    # Render al tamaño exacto del rectángulo
                    plot_series_to_png(x2, y2, ymax, graph_rect.width, graph_rect.height, tmp_path)
                    if os.path.exists(tmp_path):
                        img = pygame.image.load(tmp_path)
                        if img.get_width() != graph_rect.width or img.get_height() != graph_rect.height:
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
                x0, x1 = slider_rect.left + 10, slider_rect.right - 10
                if x1 > x0:
                    lat_norm = (e.pos[0] - x0) / float(x1 - x0)
                    lat_norm = max(0, min(1, lat_norm))

        # Dibujo
        screen.fill(WHITE)
        draw_text(screen, "Herramienta de energía solar anual", 40, DARK, center=(W//2, top_y))
        draw_text(screen, f"Cuerpo: {body}", 28, DARK, topleft=(100, 140))
        draw_text(screen, f"Latitud: {map_norm_to_lat(lat_norm):+.1f}°", 28, DARK, topleft=(100, 170))

        draw_slider(screen, slider_rect, lat_norm, dragging)
        draw_button(screen, btn_calc, "Calcular", bg=BLACK)
        draw_button(screen, btn_body, f"Cambiar ({body})", bg=GREEN)
        draw_button(screen, btn_exit, "Salir", bg=RED)

        if graph_surf:
            # Reescala si el rect cambió desde el render
            if graph_surf.get_width() != graph_rect.width or graph_surf.get_height() != graph_rect.height:
                graph_surf = pygame.transform.smoothscale(graph_surf, (graph_rect.width, graph_rect.height))
            screen.blit(graph_surf, graph_rect.topleft)

        pygame.display.flip()

    # Limpieza
    try:
        if os.path.exists(tmp_path): os.remove(tmp_path)
    except Exception:
        pass
    pygame.quit()

if __name__ == "__main__":
    main()
