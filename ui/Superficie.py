import os
import math
import tempfile
import pygame
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# -----------------------------------------------
# CONFIGURACIÓN
# -----------------------------------------------
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (210, 210, 210)
BLUE  = (30, 144, 255)
GREEN = (40, 180, 120)
RED   = (200, 60, 60)
DARK  = (34, 49, 73)

pygame.init()
W, H = 1280, 720
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Energía solar anual — Marte o Luna")
clock = pygame.time.Clock()

# -----------------------------------------------
# FUNCIONES AUXILIARES
# -----------------------------------------------
def draw_text(surf, text, size, color, center=None, topleft=None):
    font = pygame.font.SysFont(None, size)
    txt = font.render(text, True, color)
    rect = txt.get_rect()
    if center:
        rect.center = center
    if topleft:
        rect.topleft = topleft
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

# -----------------------------------------------
# FÍSICA: insolación anual simplificada
# -----------------------------------------------
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
    return [daily_insolation(lat, dlt, S0, tau) for dlt in deltas]

def plot_series(x, y, title, path):
    plt.figure(figsize=(8,4), dpi=140)
    plt.plot(x, y)
    plt.title(title)
    plt.xlabel("Día del año")
    plt.ylabel("Energía diaria (Wh/m²)")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(path)
    plt.close()

# -----------------------------------------------
# PANTALLA PRINCIPAL
# -----------------------------------------------
def main():
    lat_norm = 0.5
    dragging = False
    body = "Marte"
    graph_surf = None

    slider_rect = pygame.Rect(100, 200, W - 200, 40)
    btn_calc = pygame.Rect(100, 280, 200, 50)
    btn_body = pygame.Rect(320, 280, 200, 50)
    btn_exit = pygame.Rect(W - 300, 280, 200, 50)
    graph_rect = pygame.Rect(100, 360, W - 200, 320)

    running = True
    while running:
        dt = clock.tick(60)
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if slider_rect.collidepoint(e.pos):
                    dragging = True
                elif btn_calc.collidepoint(e.pos):
                    lat = map_norm_to_lat(lat_norm)
                    y = compute_series(body, lat)
                    x = list(range(1, len(y)+1))
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
                        plot_series(x, y, f"{body} — lat={lat:.1f}°", tmp.name)
                        img = pygame.image.load(tmp.name)
                        graph_surf = pygame.transform.smoothscale(img, (graph_rect.width, graph_rect.height))
                elif btn_body.collidepoint(e.pos):
                    body = "Luna" if body == "Marte" else "Marte"
                elif btn_exit.collidepoint(e.pos):
                    running = False
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                dragging = False
            elif e.type == pygame.MOUSEMOTION and dragging:
                x0, x1 = slider_rect.left + 10, slider_rect.right - 10
                lat_norm = (e.pos[0] - x0) / float(x1 - x0)
                lat_norm = max(0, min(1, lat_norm))

        screen.fill(WHITE)
        draw_text(screen, "Herramienta de energía solar anual", 40, DARK, center=(W//2, 80))
        draw_text(screen, f"Cuerpo: {body}", 28, DARK, topleft=(100, 140))
        draw_text(screen, f"Latitud: {map_norm_to_lat(lat_norm):+.1f}°", 28, DARK, topleft=(100, 170))

        draw_slider(screen, slider_rect, lat_norm, dragging)
        draw_button(screen, btn_calc, "Calcular", bg=BLACK)
        draw_button(screen, btn_body, f"Cambiar ({body})", bg=GREEN)
        draw_button(screen, btn_exit, "Salir", bg=RED)

        if graph_surf:
            screen.blit(graph_surf, graph_rect.topleft)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
