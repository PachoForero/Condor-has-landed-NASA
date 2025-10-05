
# ui/Energia.py
import os, math, tempfile
import pygame
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------- Paleta (coincide con main.py) ----------
PALETTE = {
    "sand":  "#eee5ca",
    "mars":  "#df8a5d",
    "moon":  "#496ca8",
    "navy":  "#223149",
    "white": "#ffffff",
    "black": "#000000",
}
def _hex_rgb(h): h=h.lstrip("#"); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def _hex_rgba01(h,a=0.55):
    r,g,b=_hex_rgb(h); return (r/255.0,g/255.0,b/255.0,a)

WHITE=_hex_rgb(PALETTE["white"])
BLACK=_hex_rgb(PALETTE["black"])
SAND =_hex_rgb(PALETTE["sand"])
MARS =_hex_rgb(PALETTE["mars"])
MOON =_hex_rgb(PALETTE["moon"])
NAVY =_hex_rgb(PALETTE["navy"])
AREA_MARTE=_hex_rgba01(PALETTE["mars"],0.55)
AREA_LUNA =_hex_rgba01(PALETTE["moon"],0.55)

# ---------- Estado exportado ----------
GLOBAL_YMAX = 1.0
GLOBAL_MIN_ENERGY = None

# ---------- Utilidades UI ----------
def _text(surf, txt, size, color, center=None, topleft=None):
    f = pygame.font.SysFont(None, size)
    r = f.render(txt, True, color)
    rect = r.get_rect()
    if center: rect.center = center
    if topleft: rect.topleft = topleft
    surf.blit(r, rect); return rect

def _btn(surf, rect, label, fg=WHITE, bg=NAVY, font_size=26):
    """Draw a button and center the label with given font size."""
    pygame.draw.rect(surf, bg, rect, border_radius=12)
    _text(surf, label, font_size, fg, center=rect.center)

def _slider(surf, rect, val_norm, active):
    pygame.draw.rect(surf, SAND, rect, border_radius=8)
    x0, x1 = rect.left+12, rect.right-12
    y = rect.centery
    pygame.draw.line(surf, NAVY, (x0,y),(x1,y),4)
    xh = int(x0 + (x1-x0)*val_norm)
    handle = pygame.Rect(0,0,20,20); handle.center=(xh,y)
    pygame.draw.rect(surf, MARS if active else NAVY, handle, border_radius=10)
    return handle

def _map_norm_to_lat(v): return -90.0 + 180.0*max(0.0, min(1.0, v))
def _map_norm_to_lon(v): return -180.0 + 360.0*max(0.0, min(1.0, v))

# ---------- Física ----------
def _decl_series(n_days, obliq_deg):
    eps = math.radians(obliq_deg)
    return [math.asin(math.sin(eps)*math.sin(2*math.pi*(d-80)/n_days)) for d in range(n_days)]

def _daily_ins(lat_deg, delta, S0, tau):
    phi = math.radians(lat_deg)
    x = -math.tan(phi)*math.tan(delta)
    if x <= -1: ws = math.pi
    elif x >= 1: return 0.0
    else: ws = math.acos(x)
    H = (S0/math.pi)*(ws*math.sin(phi)*math.sin(delta) + math.cos(phi)*math.cos(delta)*math.sin(ws))
    return max(0.0, H)*tau
def _series(body, lat_deg):
    if body == "Mars":
        n, eps, S0, tau = 668, 25.19, 590, 0.72
    else:
        n, eps, S0, tau = 365, 1.54, 1361, 1.0
    deltas = _decl_series(n, eps)
    y = [_daily_ins(lat_deg, d, S0, tau) for d in deltas]
    return y, n

# ---------- Matplotlib (área, sin grid/título) ----------
def _plot_area(x, y, y_max_global, w_px, h_px, path, rgba_fill):
    dpi=140
    fig_w=max(2, w_px/dpi); fig_h=max(2, h_px/dpi)
    plt.figure(figsize=(fig_w,fig_h), dpi=dpi)
    plt.fill_between(x, y, 0.0, color=rgba_fill)
    plt.ylim(0, y_max_global)
    plt.xlim(x[0], x[-1])
    P = x[-1]; ticks=[0,P*0.25,P*0.5,P*0.75,P]
    plt.xticks([int(t) for t in ticks], [f"{int(t)}" for t in ticks])
    plt.xlabel("Day of period"); plt.ylabel("Daily energy (Wh/m²)")
    plt.margins(x=0.01, y=0.0)
    plt.tight_layout(); plt.savefig(path, bbox_inches="tight", pad_inches=0.05); plt.close()

# ---------- Recursos ----------
_BASE_DIR = os.path.dirname(__file__)
_BODY_IMAGES = {"Mars": os.path.join(_BASE_DIR, "marte.jpg"),
                "Moon":  os.path.join(_BASE_DIR, "luna.jpg")}
_cache_bg = {"Mars": None, "Moon": None}

def _load_bg(body, size):
    p = _BODY_IMAGES.get(body)
    if not (p and os.path.exists(p)): return None
    try:
        img = pygame.image.load(p).convert()
        return pygame.transform.smoothscale(img, size)
    except: return None

# ---------- Pantalla pública ----------
def energia_screen(screen):
    """Annual energy screen. Returns dict with {'body','lat'} or None when returning to the menu."""
    global GLOBAL_YMAX, GLOBAL_MIN_ENERGY

    clock = pygame.time.Clock()
    running = True
    lat_norm = 0.5
    dragging = False
    body = "Marte"
    graph_surf = None
    tmp_path = os.path.join(tempfile.gettempdir(), f"energia_{os.getpid()}.png")

    while running:
        dt = clock.tick(60)
        W, H = screen.get_size()
        # Relative, more compact layout for small screens
        m = max(8, int(min(W, H) * 0.03))           # horizontal margin (3% of the smaller dimension)
        top = max(12, int(H * 0.06))                # reduced top margin
        slider_h = max(20, int(H * 0.035))
        slider = pygame.Rect(m, top + int(H * 0.02), max(160, W - 2 * m), slider_h)

        btn_h = max(28, int(H * 0.045))
        btn_w = max(90, int(W * 0.14))
        gap_x = max(6, int(W * 0.015))

        b_calc = pygame.Rect(m, slider.bottom + int(H * 0.02), btn_w, btn_h)
        b_body = pygame.Rect(b_calc.right + gap_x, b_calc.top, btn_w, btn_h)
        b_back = pygame.Rect(W - m - btn_w, b_calc.top, btn_w, btn_h)   # Volver a menú

        graph_top = b_calc.bottom + int(H * 0.025)
        # Reduce max height of the graph to ensure it fits
        graph_h = max(100, min(int(H * 0.45), H - graph_top - m))
        graph = pygame.Rect(m, graph_top, max(160, W - 2 * m), graph_h)

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return None
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if slider.collidepoint(e.pos): dragging = True
                elif b_calc.collidepoint(e.pos):
                    lat = _map_norm_to_lat(lat_norm)
                    y, P = _series(body, lat)
                    y2 = y + [y[0]]
                    x2 = list(range(0, P+1))
                    serie_max = max(y2) if y2 else 1.0
                    GLOBAL_MIN_ENERGY = min(y2) if y2 else 0.0
                    GLOBAL_YMAX = max(GLOBAL_YMAX, serie_max*1.05)  # 5% holgura
                    fill = AREA_MARTE if body == "Mars" else AREA_LUNA
                    _plot_area(x2, y2, GLOBAL_YMAX, graph.width, graph.height, tmp_path, fill)
                    if os.path.exists(tmp_path):
                        img = pygame.image.load(tmp_path)
                        if (img.get_width(),img.get_height()) != (graph.width,graph.height):
                            img = pygame.transform.smoothscale(img, (graph.width,graph.height))
                        graph_surf = img
                elif b_body.collidepoint(e.pos):
                    body = "Moon" if body == "Mars" else "Mars"
                    graph_surf = None
                elif b_back.collidepoint(e.pos):
                    return {"body": body, "lat": _map_norm_to_lat(lat_norm)}
            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                dragging = False
            elif e.type == pygame.MOUSEMOTION and dragging:
                x0, x1 = slider.left+12, slider.right-12
                if x1 > x0:
                    lat_norm = max(0, min(1, (e.pos[0]-x0)/float(x1-x0)))

        # Background with body image + veil
        bg = _cache_bg.get(body)
        if not bg or bg.get_size() != (W, H):
            bg = _load_bg(body, (W,H)); _cache_bg[body]=bg
        if bg: screen.blit(bg,(0,0))
        else: screen.fill(SAND)
        veil = pygame.Surface((W,H), pygame.SRCALPHA); veil.fill((*SAND,80)); screen.blit(veil,(0,0))

        # UI (relative positions and more compact)
        title_y = max(28, int(H * 0.05))
        _text(screen, "Annual solar energy tool", max(14, int(H * 0.03)), NAVY, center=(W // 2, title_y))
        _text(screen, f"Body: {body}", max(10, int(H * 0.025)), NAVY, topleft=(m, top))
        _text(screen, f"Latitude: {_map_norm_to_lat(lat_norm):+.1f}°", max(10, int(H * 0.025)), NAVY, topleft=(m, top + int(H * 0.03)))
        if GLOBAL_MIN_ENERGY is not None:
            _text(screen, f"Min energy: {GLOBAL_MIN_ENERGY:.1f} Wh/m²", max(9, int(H * 0.018)), NAVY, topleft=(m, top + int(H * 0.055)))
            # Show longitude under the min energy label (derived from the slider position)
            _text(screen, f"Longitude: {_map_norm_to_lon(lat_norm):+.1f}°", max(9, int(H * 0.018)), NAVY, topleft=(m, top + int(H * 0.08)))

        _slider(screen, slider, lat_norm, dragging)
        _btn(screen, b_calc, "Calculate", fg=WHITE, bg=NAVY, font_size=max(10, int(H * 0.025)))
        _btn(screen, b_body, f"Switch ({body})", fg=WHITE, bg=MARS if body == "Mars" else MOON, font_size=max(10, int(H * 0.025)))
        _btn(screen, b_back, "Back", fg=WHITE, bg=NAVY, font_size=max(10, int(H * 0.025)))

        if graph_surf:
            if (graph_surf.get_width(),graph_surf.get_height()) != (graph.width,graph.height):
                graph_surf = pygame.transform.smoothscale(graph_surf, (graph.width,graph.height))
            frame = pygame.Surface((graph.width+12, graph.height+12), pygame.SRCALPHA)
            pygame.draw.rect(frame, (*NAVY, 40), frame.get_rect(), border_radius=16)
            screen.blit(frame, (graph.left-6, graph.top-6))
            screen.blit(graph_surf, graph.topleft)

        pygame.display.flip()

    # nunca llega


def main(screen=None, width=400, height=200, fullscreen=False):
    """Entry point compatible with being called from another module.

    If `screen` is provided, it will be used. Otherwise a new pygame
    display will be created with the given width/height. If `fullscreen`
    is True the display will be created in fullscreen mode using the
    current display resolution.

    Returns the same value as `energia_screen`.
    """
    created_screen = False
    if screen is None:
        pygame.init()
        created_screen = True
        if fullscreen:
            # Create a fullscreen window at the current desktop resolution
            info = pygame.display.Info()
            # Use SCALED when available so the UI is correctly scaled on high-DPI displays
            flags = pygame.FULLSCREEN
            if hasattr(pygame, 'SCALED'):
                flags |= pygame.SCALED
            screen = pygame.display.set_mode((info.current_w, info.current_h), flags)
        else:
            # In windowed mode, use SCALED if available to account for display scaling
            flags = 0
            if hasattr(pygame, 'SCALED'):
                flags |= pygame.SCALED
            screen = pygame.display.set_mode((width, height), flags)

    try:
        return energia_screen(screen)
    finally:
        if created_screen:
            pygame.quit()


if __name__ == '__main__':
    # Start the tool in fullscreen so the user sees it occupying the
    # entire screen. Call main() to ensure proper initialization and
    # cleanup of pygame.
    main(fullscreen=True)
