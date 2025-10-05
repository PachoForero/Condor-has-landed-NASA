import os
import pygame
import sys

# Title / background color
TITLE_COLOR = (34, 49, 73)
PANEL_BG = (240, 240, 245)

# Module-level state for simplicity
_selected_module = 0
_hover_module = -1
_modules_cache = None
_last_modules = None


def load_modules_from_ui_dir():
    """Return a list of module dicts found in the ui/ folder or a fallback list."""
    global _modules_cache
    if _modules_cache is not None:
        return _modules_cache

    base_dir = os.path.dirname(__file__)
    modules = []
    try:
        for name in os.listdir(base_dir):
            low = name.lower()
            if low.startswith('mod') and low.endswith('.png'):
                modules.append({'name': os.path.splitext(name)[0], 'img': os.path.join(base_dir, name)})
    except Exception:
        modules = []

    if not modules:
        modules = [
            {'name': 'Modulo A', 'img': None},
            {'name': 'Modulo B', 'img': None},
            {'name': 'Modulo C', 'img': None},
            {'name': 'Canadarm', 'img': None},
            {'name': 'Dextre', 'img': None},
        ]

    _modules_cache = modules
    return modules


def draw_text(surface, text, pos, font, color=(20, 20, 20)):
    if font is None:
        return
    surf = font.render(text, True, color)
    surface.blit(surf, pos)


def cohete_screen(screen):
    """Draw the three-column UI on the provided pygame Surface."""
    global _hover_module, _last_modules

    if screen is None:
        return

    base_dir = os.path.dirname(__file__)
    rocket_path = os.path.join(base_dir, 'rocket.png')
    if not os.path.exists(rocket_path):
        alt = os.path.join(os.getcwd(), 'ui', 'rocket.png')
        if os.path.exists(alt):
            rocket_path = alt

    sw, sh = screen.get_size()
    screen.fill(TITLE_COLOR)

    # Columns
    left_w = max(220, int(sw * 0.22))
    right_w = max(220, int(sw * 0.22))
    center_w = max(200, sw - left_w - right_w)

    left_rect = pygame.Rect(8, 8, left_w - 16, sh - 16)
    center_rect = pygame.Rect(left_w + 8, 8, center_w - 16, sh - 16)
    right_rect = pygame.Rect(left_w + center_w + 8, 8, right_w - 16, sh - 16)

    # Panel backgrounds
    pygame.draw.rect(screen, PANEL_BG, left_rect, border_radius=6)
    pygame.draw.rect(screen, PANEL_BG, center_rect, border_radius=6)
    pygame.draw.rect(screen, PANEL_BG, right_rect, border_radius=6)

    # Fonts
    try:
        title_font = pygame.font.SysFont(None, 30)
        small_font = pygame.font.SysFont(None, 20)
    except Exception:
        title_font = None
        small_font = None

    # Left panel content
    if title_font:
        draw_text(screen, 'Mission', (left_rect.x + 12, left_rect.y + 12), title_font)

    info_lines = [
        'Tipo de misión: Asentamiento',
        'Mission #1 - Exploración',
        'Tripulación max: 4',
        'Costo total: $ --',
        '',
        'Volumen disp:  X m3',
        'Peso disp:     X kg',
        '',
        'Módulos añadidos:'
    ]

    y = left_rect.y + 48
    for ln in info_lines:
        draw_text(screen, ln, (left_rect.x + 12, y), small_font)
        if small_font:
            y += small_font.get_height() + 8
        else:
            y += 20

    # Center: rocket image or placeholder stacked modules
    rocket_img = None
    if os.path.exists(rocket_path):
        try:
            rocket_img = pygame.image.load(rocket_path).convert_alpha()
        except Exception:
            rocket_img = None

    margin = 24
    avail_w = center_rect.width - margin * 2
    avail_h = center_rect.height - margin * 2

    if rocket_img is not None:
        rw, rh = rocket_img.get_size()
        scale = min(avail_w / rw, avail_h / rh, 1.8)
        new_size = (max(1, int(rw * scale)), max(1, int(rh * scale)))
        rocket_draw = pygame.transform.smoothscale(rocket_img, new_size)
        rx = center_rect.x + (center_rect.width - new_size[0]) // 2
        ry = center_rect.y + (center_rect.height - new_size[1]) // 2
        screen.blit(rocket_draw, (rx, ry))
    else:
        stack_w = int(center_rect.width * 0.25)
        cx = center_rect.x + center_rect.width // 2
        base_h = int(center_rect.height * 0.6)
        bh = base_h // 4
        top = center_rect.y + (center_rect.height - base_h) // 2
        colors = [(200, 200, 200), (180, 180, 180), (160, 160, 160)]
        for i in range(3):
            rect_h = bh
            rect_w = stack_w - i * 12
            rx = cx - rect_w // 2
            ry = top + i * (bh + 6)
            pygame.draw.rect(screen, colors[i % len(colors)], (rx, ry, rect_w, rect_h), border_radius=8)

    # Modules list on the right
    modules = load_modules_from_ui_dir()

    item_h = 46
    padding = 12
    list_x = right_rect.x + padding
    list_y = right_rect.y + 12

    mouse_x, mouse_y = pygame.mouse.get_pos()
    _hover_module = -1

    for idx, m in enumerate(modules):
        iy = list_y + idx * (item_h + 8)
        item_rect = pygame.Rect(list_x, iy, right_rect.width - padding * 2, item_h)
        bg = (250, 250, 250)
        if item_rect.collidepoint(mouse_x, mouse_y):
            bg = (235, 242, 255)
            _hover_module = idx
        if idx == _selected_module:
            bg = (220, 235, 255)

        pygame.draw.rect(screen, bg, item_rect, border_radius=6)
        draw_text(screen, m['name'], (item_rect.x + 10, item_rect.y + 10), small_font)

    # Save hover/modules for main loop using module-level vars (Surface doesn't allow new attrs)
    _last_modules = modules

    # Right panel title
    draw_text(screen, 'Módulos', (right_rect.x + 12, right_rect.y + 12), title_font)

    # Selected module preview in center-bottom
    if 0 <= _selected_module < len(modules):
        m = modules[_selected_module]
        preview_h = int(center_rect.height * 0.25)
        preview_w = int(center_rect.width * 0.55)
        px = center_rect.x + (center_rect.width - preview_w) // 2
        py = center_rect.y + center_rect.height - preview_h - 20
        pygame.draw.rect(screen, (245, 245, 250), (px, py, preview_w, preview_h), border_radius=8)
        draw_text(screen, f'Seleccionado: {m["name"]}', (px + 10, py + 10), small_font)


def main():
    """Simple test runner for Cohete module."""
    global _selected_module

    pygame.init()
    info = pygame.display.Info()
    w, h = min(1280, info.current_w), min(900, info.current_h)
    screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    pygame.display.set_caption('Cohete preview')
    clock = pygame.time.Clock()

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((ev.w, ev.h), pygame.RESIZABLE)
            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # use module-level hover/modules saved by cohete_screen
                hover = _hover_module
                modules = _last_modules
                if modules is not None and 0 <= hover < len(modules):
                    _selected_module = hover

        cohete_screen(screen)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
