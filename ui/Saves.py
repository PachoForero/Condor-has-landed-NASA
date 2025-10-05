# ui/saves.py
import os, json, time, math, sys, pygame, importlib, importlib.util

APP_NAME = "Saved Configurations"
PALETTE = {
    "bg": (20, 20, 24),
    "card": (28, 28, 34),
    "card_border": (120, 120, 135),
    "accent": (60, 130, 200),
    "text": (235, 235, 240),
    "muted": (170, 175, 185),
    "back": (60, 140, 110),
}

GRID_COLS = 5
GRID_ROWS = 3
MAX_SHOW  = GRID_COLS * GRID_ROWS

# --- asegurar que el directorio del proyecto esté disponible ---
HERE = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(HERE, ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# ---------------- utilidades básicas ----------------
def _saves_dir():
    return os.path.join(HERE, "saves")

def _human_time(ts):
    try:
        now = time.time()
        diff = max(0, now - float(ts))
        if diff < 90:
            return "just now"
        mins = diff / 60.0
        hours = mins / 60.0
        days = hours / 24.0
        if mins < 60:
            return f"{int(mins)} min ago"
        if hours < 24:
            return f"{int(hours)} h ago"
        if days < 7:
            return f"{int(days)} d ago"
        t = time.localtime(ts)
        return time.strftime("%Y-%m-%d %H:%M", t)
    except Exception:
        return "unknown"

def _load_summaries(limit=MAX_SHOW):
    d = _saves_dir()
    if not os.path.isdir(d):
        return []
    items = []
    for name in os.listdir(d):
        if not name.lower().endswith(".json"):
            continue
        path = os.path.join(d, name)
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            ts = data.get("timestamp", os.path.getmtime(path))
            mods = len(data.get("modules", []))
            totals = data.get("totals", {})
            items.append({
                "path": path,
                "timestamp": ts,
                "when": _human_time(ts),
                "modules": mods,
                "energy": totals.get("Energy", 0),
                "o2": totals.get("O2", 0),
                "waste": totals.get("Waste", 0),
                "food": totals.get("Food", 0),
                "crew": totals.get("Crew", 0),
                "volume": totals.get("Volume", 0),
            })
        except Exception:
            continue
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return items[:limit]

# ---------------- dibujado ----------------
def _draw_back_button(screen, rect, font):
    pygame.draw.rect(screen, PALETTE["back"], rect, border_radius=10)
    label = font.render("Back", True, (255, 255, 255))
    screen.blit(label, label.get_rect(center=rect.center))

def _draw_card(screen, rect, item, fonts):
    f_title, f_line, f_small = fonts
    pygame.draw.rect(screen, PALETTE["card"], rect, border_radius=12)
    pygame.draw.rect(screen, PALETTE["card_border"], rect, 2, border_radius=12)

    when = item["when"]
    title = f_title.render(when, True, PALETTE["text"])
    screen.blit(title, (rect.x + 12, rect.y + 10))

    base = os.path.basename(item["path"])
    tpath = f_small.render(base, True, PALETTE["muted"])
    screen.blit(tpath, (rect.x + 12, rect.y + 10 + title.get_height() + 4))

    y_sep = rect.y + 10 + title.get_height() + 8 + tpath.get_height()
    pygame.draw.line(screen, PALETTE["card_border"], (rect.x + 10, y_sep), (rect.right - 10, y_sep), 1)

    lines = [
        ("Modules", f"{item['modules']}"),
        ("Crew",    f"{int(item['crew'])}"),
        ("Energy",  f"{int(item['energy'])} W"),
        ("O2",      f"{item['o2']:.2f} kg/d"),
        ("Waste",   f"{item['waste']:.2f} kg/d"),
        ("Food",    f"{item['food']:.2f} kg/d"),
        ("Volume",  f"{item['volume']:.2f} m³"),
    ]
    y = y_sep + 8
    for k, v in lines:
        text = f_line.render(f"{k}: ", True, PALETTE["muted"])
        val  = f_line.render(v, True, PALETTE["text"])
        screen.blit(text, (rect.x + 12, y))
        screen.blit(val,  (rect.x + 12 + text.get_width(), y))
        y += text.get_height() + 6
        if y > rect.bottom - 10 - f_small.get_height():
            break

def _grid_layout(sw, sh):
    margin_x = max(16, int(sw * 0.02))
    margin_y = max(16, int(sh * 0.12))
    spacing_x = max(12, int(sw * 0.01))
    spacing_y = max(12, int(sh * 0.02))

    usable_w = sw - margin_x * 2 - spacing_x * (GRID_COLS - 1)
    usable_h = sh - margin_y - margin_x - spacing_y * (GRID_ROWS - 1)

    card_w = max(180, usable_w // GRID_COLS)
    card_h = max(150, usable_h // GRID_ROWS)

    rects = []
    y = margin_y
    for r in range(GRID_ROWS):
        x = margin_x
        for c in range(GRID_COLS):
            rects.append(pygame.Rect(x, y, card_w, card_h))
            x += card_w + spacing_x
        y += card_h + spacing_y

    back_w = max(120, int(sw * 0.12))
    back_h = max(36,  int(sh * 0.06))
    back_rect = pygame.Rect(margin_x, sh - back_h - margin_x, back_w, back_h)
    return rects, back_rect

def _fonts_for_screen(sw, sh):
    base = max(12, int(min(sw, sh) * 0.018))
    f_title = pygame.font.SysFont(None, base + 4)
    f_line  = pygame.font.SysFont(None, base)
    f_small = pygame.font.SysFont(None, max(12, base - 2))
    f_h1    = pygame.font.SysFont(None, base + 10)
    return f_h1, f_title, f_line, f_small

# ---------------- pantalla de saves ----------------
def saves_screen(screen):
    clock = pygame.time.Clock()
    pygame.display.set_caption(APP_NAME)

    items = _load_summaries()
    sw, sh = screen.get_size()
    rects, back_rect = _grid_layout(sw, sh)
    f_h1, f_title, f_line, f_small = _fonts_for_screen(sw, sh)

    running = True
    selected_path = None

    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return None
            elif e.type == pygame.VIDEORESIZE:
                screen = pygame.display.get_surface()
                sw, sh = screen.get_size()
                rects, back_rect = _grid_layout(sw, sh)
                f_h1, f_title, f_line, f_small = _fonts_for_screen(sw, sh)
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                mouse = pygame.mouse.get_pos()
                if back_rect.collidepoint(mouse):
                    return None
                for i, r in enumerate(rects):
                    if i < len(items) and r.collidepoint(mouse):
                        selected_path = items[i]["path"]
                        return selected_path

        screen.fill(PALETTE["bg"])
        title = f_h1.render("Saved configurations", True, PALETTE["text"])
        screen.blit(title, (max(16, int(sw*0.02)), max(10, int(sh*0.03))))

        fonts_card = (f_title, f_line, f_small)
        for i, r in enumerate(rects):
            if i < len(items):
                _draw_card(screen, r, items[i], fonts_card)
            else:
                pygame.draw.rect(screen, PALETTE["card"], r, border_radius=12)
                pygame.draw.rect(screen, (80, 80, 90), r, 1, border_radius=12)
                hint = f_small.render("Empty", True, (120, 120, 130))
                screen.blit(hint, hint.get_rect(center=r.center))

        _draw_back_button(screen, back_rect, f_title)
        pygame.display.flip()
        clock.tick(60)

# ---------------- lanzador principal ----------------
def _load_module_by_path(module_name: str, file_path: str):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot create spec for {file_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def open_saves_and_launch(launch_module: str = os.environ.get("HAB_LAUNCH_MOD", "inicio"),
                          launch_func: str = "modulos_screen",
                          window_func: str = "create_window"):
    pygame.init()
    info = pygame.display.Info()
    pygame.display.set_mode((int(info.current_w*0.9), int(info.current_h*0.9)), pygame.RESIZABLE)
    screen = pygame.display.get_surface()

    selected = saves_screen(screen)
    if not selected:
        pygame.quit()
        return

    mod = None
    try:
        mod = importlib.import_module(launch_module)
    except Exception:
        candidate = os.path.join(PROJECT_ROOT, f"{launch_module}.py")
        if not os.path.isfile(candidate):
            pygame.quit()
            raise RuntimeError(f"No encuentro {candidate} para cargar '{launch_module}'.")
        mod = _load_module_by_path(launch_module, candidate)

    try:
        create_window = getattr(mod, window_func)
        modulos_screen = getattr(mod, launch_func)
    except AttributeError as e:
        pygame.quit()
        raise RuntimeError(f"Falta función en {launch_module}: {e}")

    pygame.quit()
    screen2 = create_window()
    modulos_screen(screen2, config=selected)

# -------------- ejecutable directo --------------
if __name__ == "__main__":
    open_saves_and_launch()
