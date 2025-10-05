import sys, math, os
import pygame

# -------------------- Config --------------------
APP_NAME = "Hex Habitat — Pan, Zoom, UI"
PALETTE = {
    "bg": (20, 20, 24),
    "stroke": (40, 40, 48),
    "prefab": (60, 130, 200),
    "built":  (230, 160, 60),
    "green": (30, 200, 90),
    "red": (220, 60, 60),
    "white": (240, 240, 240),
    "ui": (28, 28, 34),
    "ui_border": (120, 120, 135),
}
HEX_SIZE = 45
DOT_R = 9
LINE_W = 2
FPS = 60

PAN_STEP_SCR = 90
ZOOM_STEP   = 1.12

# Axial pointy-top
NEI = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
SQRT3 = math.sqrt(3.0)
APOTHEM = HEX_SIZE * SQRT3 / 2.0

SPRITE_CANDIDATES = ["Modulo.png", "Modulo.jpg"]

def _find_sprite_path():
    here = os.path.dirname(__file__)
    for name in SPRITE_CANDIDATES:
        p1 = os.path.join(here, name)
        p2 = os.path.join(os.getcwd(), name)
        if os.path.exists(p1): return p1
        if os.path.exists(p2): return p2
    return None

def _tinted_copy(src, rgb):
    s = src.copy().convert_alpha()
    tint = pygame.Surface(s.get_size(), pygame.SRCALPHA)
    tint.fill((*rgb, 255))
    s.blit(tint, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
    return s

# -------------------- Geometry --------------------
def axial_to_world(q, r):
    x = HEX_SIZE * SQRT3 * (q + r/2)
    y = HEX_SIZE * 1.5 * r
    return (x, y)

def hex_points_world(center_w):
    # pointy-top: vertices at -30° + k*60°
    cx, cy = center_w
    pts = []
    for i in range(6):
        ang = math.radians(60 * i - 30)
        pts.append((cx + HEX_SIZE * math.cos(ang),
                    cy + HEX_SIZE * math.sin(ang)))
    return pts

def point_in_polygon(pt, poly):
    x, y = pt
    inside = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xinters = (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1
            if x < xinters: inside = not inside
    return inside

# -------------------- Camera --------------------
class Camera:
    def __init__(self, screen):
        self.screen = screen
        self.zoom = 1.0
        self.min_zoom = 0.3
        self.max_zoom = 3.5
        self.pos = (0.0, 0.0)
    def set_screen(self, screen): self.screen = screen
    @property
    def sw(self): return self.screen.get_width()
    @property
    def sh(self): return self.screen.get_height()
    def world_to_screen(self, p):
        return ((p[0] - self.pos[0]) * self.zoom + self.sw * 0.5,
                (p[1] - self.pos[1]) * self.zoom + self.sh * 0.5)
    def screen_to_world(self, s):
        return ((s[0] - self.sw * 0.5) / self.zoom + self.pos[0],
                (s[1] - self.sh * 0.5) / self.zoom + self.pos[1])
    def apply_poly(self, poly_world):
        return [self.world_to_screen(p) for p in poly_world]
    def zoom_at(self, mouse_screen, zf):
        before = self.screen_to_world(mouse_screen)
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * zf))
        after = self.screen_to_world(mouse_screen)
        self.pos = (self.pos[0] + (before[0] - after[0]),
                    self.pos[1] + (before[1] - after[1]))

# -------------------- Module --------------------
class Modulo:
    __slots__ = ("q","r","style","equip")
    def __init__(self, q, r, style=0):
        self.q=q; self.r=r; self.style=style   # 0=prefab, 1=built
        self.equip = [0]*6                     # 6 slots, 0/1 -> Item 1/2
    def axial(self): return (self.q, self.r)
    def neighbors_axial(self):
        q, r = self.q, self.r
        for dq, dr in NEI:
            yield (q + dq, r + dr)

# -------------------- World --------------------
class Mundo:
    def __init__(self, camera):
        self.cam = camera
        self.screen = camera.screen
        self.modulos = {}
        self.base_ax = (0, 0)
        self.selected = None
        self.green_dots_screen = []    # [(axial, (sx,sy))]
        self.red_dot_screen = None
        self.style_next = 0  # default for new modules
        self.modulos[(0,0)] = Modulo(0, 0, style=0)

        # Sprite + tinted versions
        self.sprite_path = _find_sprite_path()
        self.sprite_base = None
        self.sprite_tinted = {0: None, 1: None}
        self.sprite_scaled = {0: None, 1: None}
        self._scaled_px = None
        if self.sprite_path:
            try:
                self.sprite_base = pygame.image.load(self.sprite_path).convert_alpha()
                self.sprite_tinted[0] = _tinted_copy(self.sprite_base, PALETTE["prefab"])
                self.sprite_tinted[1] = _tinted_copy(self.sprite_base, PALETTE["built"])
            except: self.sprite_base = None

        # Style popup
        self.selecting_style = False
        self.selector_rect = None
        self.pref_rect = None
        self.built_rect = None
        self.pending_ax = None
        self.font_popup = pygame.font.SysFont(None, 22)
        self._pref_text = self.font_popup.render("Prefabricated", True, PALETTE["white"])
        self._built_text = self.font_popup.render("Manufactured",  True, PALETTE["white"])

        # Equipment panel
        self.equip_open = False
        self.equip_rect = None
        self.equip_slot_rects = []     # [(slot_idx, left_arrow_rect, right_arrow_rect, label_rect)]

    # ---- helpers ----
    def center_world_of(self, axial): return axial_to_world(axial[0], axial[1])
    def poly_world_of(self, axial): return hex_points_world(self.center_world_of(axial))

    def pick_modulo(self, mouse_screen):
        mw = self.cam.screen_to_world(mouse_screen)
        for ax in self.modulos:
            if point_in_polygon(mw, self.poly_world_of(ax)): return ax
        return None

    def refresh_dots(self):
        self.green_dots_screen.clear(); self.red_dot_screen = None
        if self.selected is None: return
        c_w = self.center_world_of(self.selected)
        self.red_dot_screen = self.cam.world_to_screen(c_w)
        for nb in Modulo(*self.selected).neighbors_axial():
            v = (axial_to_world(nb[0]-self.selected[0], nb[1]-self.selected[1]))
            mag = math.hypot(v[0], v[1]); 
            if mag < 1e-6: continue
            u = (v[0]/mag, v[1]/mag)
            face_w = (c_w[0] + u[0]*APOTHEM, c_w[1] + u[1]*APOTHEM)
            self.green_dots_screen.append((nb, self.cam.world_to_screen(face_w)))

    def green_hit(self, mouse_screen):
        r2 = DOT_R * DOT_R
        for nb, pos_s in self.green_dots_screen:
            dx = mouse_screen[0] - pos_s[0]; dy = mouse_screen[1] - pos_s[1]
            if dx*dx + dy*dy <= r2: return nb, pos_s
        return None

    def place_with_style(self, axial, style):
        if axial not in self.modulos: self.modulos[axial] = Modulo(axial[0], axial[1], style=style)
        self.selected = axial; self.refresh_dots(); self.open_equip_panel()

    def try_delete_from_red(self, mouse_screen):
        if self.selected is None or self.red_dot_screen is None: return False
        if self.selected == self.base_ax: return False
        dx = mouse_screen[0] - self.red_dot_screen[0]; dy = mouse_screen[1] - self.red_dot_screen[1]
        if dx*dx + dy*dy <= DOT_R * DOT_R:
            del self.modulos[self.selected]; self.selected = None
            self.refresh_dots(); self.close_equip_panel(); return True
        return False

    def try_place_from_green(self, mouse_screen):
        hit = self.green_hit(mouse_screen)
        if not hit: return False
        axial, anchor = hit
        self.pending_ax = axial
        self.open_style_selector(anchor)
        return True

    def select_or_toggle(self, mouse_screen):
        picked = self.pick_modulo(mouse_screen)
        if picked is None or self.selected == picked:
            self.selected = None; self.close_equip_panel()
        else:
            self.selected = picked; self.open_equip_panel()
        self.refresh_dots()

    def set_screen(self, screen):
        self.screen = screen; self.refresh_dots()
        if self.selected: self.open_equip_panel()

    def _get_scaled_sprite(self, style):
        if self.sprite_base is None: return None
        target = max(1, int(2 * HEX_SIZE * self.cam.zoom))
        if self._scaled_px != target:
            for s in (0,1):
                self.sprite_scaled[s] = pygame.transform.smoothscale(self.sprite_tinted[s], (target, target))
            self._scaled_px = target
        return self.sprite_scaled[style]

    # ----- style selector (auto-size to text) -----
    def open_style_selector(self, anchor_screen_pos):
        self.selecting_style = True
        pad = 12; gap = 10
        t1 = self._pref_text; t2 = self._built_text
        bw1 = t1.get_width() + 2*pad; bw2 = t2.get_width() + 2*pad
        bh  = max(t1.get_height(), t2.get_height()) + 2*pad
        w   = bw1 + bw2 + gap + 2*pad; h = bh + 2*pad
        ax, ay = int(anchor_screen_pos[0]), int(anchor_screen_pos[1])
        x = min(max(10, ax - w//2), self.screen.get_width() - w - 10)
        y = min(max(10, ay - h - 14), self.screen.get_height() - h - 10)
        self.selector_rect = pygame.Rect(x, y, w, h)
        self.pref_rect  = pygame.Rect(x + pad, y + pad, bw1, bh)
        self.built_rect = pygame.Rect(self.pref_rect.right + gap, y + pad, bw2, bh)

    def close_style_selector(self):
        self.selecting_style = False
        self.selector_rect = self.pref_rect = self.built_rect = None
        self.pending_ax = None

    # ----- equipment panel (3x2) -----
    def open_equip_panel(self):
        self.equip_open = True
        if not self.selected:
            self.equip_rect = None; self.equip_slot_rects = []; return
        # place panel to the right of selected hex
        cx, cy = self.cam.world_to_screen(self.center_world_of(self.selected))
        cell_w, cell_h = 120, 44
        cols, rows = 3, 2
        pad = 10
        w = cols*cell_w + (cols+1)*pad
        h = rows*cell_h + (rows+1)*pad + 24
        x = int(min(max(10, cx + 2*APOTHEM*self.cam.zoom + 12), self.screen.get_width()-w-10))
        y = int(min(max(10, cy - h//2), self.screen.get_height()-h-10))
        self.equip_rect = pygame.Rect(x, y, w, h)

        # slots
        self.equip_slot_rects = []
        y0 = y + pad + 24
        idx = 0
        for r in range(rows):
            x0 = x + pad
            for c in range(cols):
                cell = pygame.Rect(x0, y0, cell_w, cell_h)
                # arrow zones
                ar = cell.inflate(-cell_w*0.6, -cell_h*0.4)  # right
                al = ar.move(-(cell_w*0.6), 0)               # left
                label = cell.inflate(-cell_w*0.35, -cell_h*0.35)
                self.equip_slot_rects.append((idx, al, ar, label, cell))
                x0 += cell_w + pad
                idx += 1
            y0 += cell_h + pad

    def close_equip_panel(self):
        self.equip_open = False
        self.equip_rect = None
        self.equip_slot_rects = []

    # ---- Draw ----
    def draw(self):
        surf = self.screen
        surf.fill(PALETTE["bg"])
        for ax, mod in self.modulos.items():
            poly_s = self.cam.apply_poly(self.poly_world_of(ax))
            spr = self._get_scaled_sprite(mod.style)
            if spr:
                cx, cy = self.cam.world_to_screen(self.center_world_of(ax))
                rect = spr.get_rect(center=(int(cx), int(cy)))
                surf.blit(spr, rect)
                pygame.draw.polygon(surf, PALETTE["stroke"], poly_s, LINE_W)
            else:
                color = PALETTE["prefab"] if mod.style == 0 else PALETTE["built"]
                pygame.draw.polygon(surf, color, poly_s)
                pygame.draw.polygon(surf, PALETTE["stroke"], poly_s, LINE_W)

        if self.selected is not None:
            for _, pos_s in self.green_dots_screen:
                pygame.draw.circle(surf, PALETTE["green"], (int(pos_s[0]), int(pos_s[1])), DOT_R)
                pygame.draw.circle(surf, PALETTE["white"], (int(pos_s[0]), int(pos_s[1])), DOT_R, 2)
            if self.selected != self.base_ax and self.red_dot_screen is not None:
                rx, ry = self.red_dot_screen
                pygame.draw.circle(surf, PALETTE["red"], (int(rx), int(ry)), DOT_R)
                pygame.draw.circle(surf, PALETTE["white"], (int(rx), int(ry)), DOT_R, 2)

        # style popup
        if self.selecting_style and self.selector_rect:
            pygame.draw.rect(surf, PALETTE["ui"], self.selector_rect, border_radius=10)
            pygame.draw.rect(surf, PALETTE["ui_border"], self.selector_rect, 2, border_radius=10)
            pygame.draw.rect(surf, PALETTE["prefab"], self.pref_rect, border_radius=8)
            pygame.draw.rect(surf, PALETTE["built"],  self.built_rect, border_radius=8)
            surf.blit(self._pref_text, self._pref_text.get_rect(center=self.pref_rect.center))
            surf.blit(self._built_text, self._built_text.get_rect(center=self.built_rect.center))

        # equipment panel
        if self.equip_open and self.equip_rect and self.selected:
            pygame.draw.rect(surf, PALETTE["ui"], self.equip_rect, border_radius=10)
            pygame.draw.rect(surf, PALETTE["ui_border"], self.equip_rect, 2, border_radius=10)
            title = pygame.font.SysFont(None, 22).render("Equipment", True, PALETTE["white"])
            surf.blit(title, (self.equip_rect.x + 10, self.equip_rect.y + 6))

            item_names = ["Item 1", "Item 2"]
            for idx, al, ar, label, cell in self.equip_slot_rects:
                pygame.draw.rect(surf, PALETTE["ui_border"], cell, 1, border_radius=6)
                # arrows
                def draw_arrow(rr, dir_):
                    cx, cy = rr.center; s = min(rr.w, rr.h) * 0.38
                    if dir_=="left":
                        pts=[(cx-s,cy),(cx+s,cy-s),(cx+s,cy+s)]
                    else:
                        pts=[(cx+s,cy),(cx-s,cy-s),(cx-s,cy+s)]
                    pygame.draw.polygon(surf, PALETTE["white"], pts)
                draw_arrow(al, "left"); draw_arrow(ar, "right")
                # label
                mod = self.modulos[self.selected]
                text = item_names[mod.equip[idx] % len(item_names)]
                lab = pygame.font.SysFont(None, 22).render(text, True, PALETTE["white"])
                surf.blit(lab, lab.get_rect(center=label.center))

# -------------------- App base --------------------
def create_window():
    pygame.init()
    pygame.display.set_caption(APP_NAME)
    info = pygame.display.Info()
    pygame.display.set_mode((int(info.current_w*0.9), int(info.current_h*0.9)), pygame.RESIZABLE)
    return pygame.display.get_surface()

def toggle_fullscreen():
    surf = pygame.display.get_surface(); info = pygame.display.Info()
    if surf.get_flags() & pygame.FULLSCREEN:
        pygame.display.set_mode((int(info.current_w*0.9), int(info.current_h*0.9)), pygame.RESIZABLE)
    else:
        pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)

# ---------- Nav controls 3×2 ----------
def _make_nav_buttons(sw, sh):
    pad = 16; size = 52; gap = 8
    origin = (pad, sh - pad - size*2)
    x0, y0 = origin
    r_plus  = pygame.Rect(x0 + 0*(size+gap), y0 + 0*(size+gap), size, size)
    r_up    = pygame.Rect(x0 + 1*(size+gap), y0 + 0*(size+gap), size, size)
    r_minus = pygame.Rect(x0 + 2*(size+gap), y0 + 0*(size+gap), size, size)
    r_left  = pygame.Rect(x0 + 0*(size+gap), y0 + 1*(size+gap), size, size)
    r_down  = pygame.Rect(x0 + 1*(size+gap), y0 + 1*(size+gap), size, size)
    r_right = pygame.Rect(x0 + 2*(size+gap), y0 + 1*(size+gap), size, size)
    return r_plus, r_up, r_minus, r_left, r_down, r_right

def _draw_round_button(screen, rect):
    pygame.draw.rect(screen, PALETTE["ui"], rect, border_radius=10)
    pygame.draw.rect(screen, PALETTE["ui_border"], rect.inflate(6,6), 3, border_radius=12)

def _draw_arrow(screen, rect, dir_):
    cx, cy = rect.center; w, h = rect.size
    s = min(w, h) * 0.32
    if dir_ == "up":
        pts = [(cx, cy - s), (cx - s, cy + s), (cx + s, cy + s)]
    elif dir_ == "down":
        pts = [(cx, cy + s), (cx - s, cy - s), (cx + s, cy - s)]
    elif dir_ == "left":
        pts = [(cx - s, cy), (cx + s, cy - s), (cx + s, cy + s)]
    else:
        pts = [(cx + s, cy), (cx - s, cy - s), (cx - s, cy + s)]
    pygame.draw.polygon(screen, PALETTE["white"], pts, 0)
    pygame.draw.polygon(screen, PALETTE["ui_border"], pts, 3)

def _draw_plusminus(screen, rect, sign):
    _draw_round_button(screen, rect)
    cx, cy = rect.center; w = rect.width*0.3
    pygame.draw.line(screen, PALETTE["white"], (cx - w, cy), (cx + w, cy), 3)
    if sign == "+": pygame.draw.line(screen, PALETTE["white"], (cx, cy - w), (cx, cy + w), 3)

def _draw_nav_grid(screen, rects):
    plus, up, minus, left, down, right = rects
    for r in rects: _draw_round_button(screen, r)
    _draw_plusminus(screen, plus, "+"); _draw_plusminus(screen, minus, "-")
    _draw_arrow(screen, up, "up"); _draw_arrow(screen, down, "down")
    _draw_arrow(screen, left, "left"); _draw_arrow(screen, right, "right")

# ---------- Metrics panel ----------
DEFAULT_METRICS = {
    "Energy": 0,
    "O2": 0,
    "Waste": 0,
    "Food": 0,
    "Crew": 0,
    "Total volume": 0,
}
def _draw_metrics_panel(screen, values, x=12, top=12, width=210):
    h = 28 * (len(values) + 1) + 16
    panel = pygame.Rect(x, top, width, h)
    pygame.draw.rect(screen, PALETTE["ui"], panel, border_radius=10)
    pygame.draw.rect(screen, PALETTE["ui_border"], panel, 2, border_radius=10)
    font_t = pygame.font.SysFont(None, 22)
    y = top + 12
    title = pygame.font.SysFont(None, 24).render("Totals", True, PALETTE["white"])
    screen.blit(title, (x + 12, y)); y += 28
    for k, v in values.items():
        txt = f"{k}: {v}"
        surf = font_t.render(txt, True, PALETTE["white"])
        screen.blit(surf, (x + 12, y)); y += 24

# -------------------- Main screen --------------------
def modulos_screen(screen):
    clock = pygame.time.Clock()
    cam = Camera(screen)
    world = Mundo(cam)

    sw, sh = screen.get_size()
    btn_h = max(36, int(sh * 0.06))
    pad = 20; gap = 12
    btn_w = max(120, int(sw * 0.14))
    back_rect = pygame.Rect(sw - btn_w - pad, sh - btn_h - pad, btn_w, btn_h)
    save_rect = pygame.Rect(back_rect.left - gap - btn_w, sh - btn_h - pad, btn_w, btn_h)

    nav_rects = _make_nav_buttons(sw, sh)

    font_title = pygame.font.SysFont(None, 32)
    font_button = pygame.font.SysFont(None, 26)

    totals = DEFAULT_METRICS.copy()

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            elif e.type == pygame.VIDEORESIZE:
                screen = pygame.display.get_surface()
                cam.set_screen(screen); world.set_screen(screen)
                sw, sh = screen.get_size()
                btn_h = max(36, int(sh * 0.06))
                btn_w = max(120, int(sw * 0.14))
                back_rect = pygame.Rect(sw - btn_w - pad, sh - btn_h - pad, btn_w, btn_h)
                save_rect = pygame.Rect(back_rect.left - gap - btn_w, sh - btn_h - pad, btn_w, btn_h)
                nav_rects = _make_nav_buttons(sw, sh)
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if   world.selecting_style: world.close_style_selector()
                    elif world.equip_open:      world.close_equip_panel()
                    else: running = False
                elif e.key == pygame.K_F11:
                    toggle_fullscreen()
                    cam.set_screen(pygame.display.get_surface())
                    world.set_screen(pygame.display.get_surface())
                    sw, sh = cam.sw, cam.sh
                    back_rect = pygame.Rect(sw - btn_w - pad, sh - btn_h - pad, btn_w, btn_h)
                    save_rect = pygame.Rect(back_rect.left - gap - btn_w, sh - btn_h - pad, btn_w, btn_h)
                    nav_rects = _make_nav_buttons(sw, sh)
                elif e.key == pygame.K_r and world.selected is not None:
                    world.modulos[world.selected].style ^= 1
            elif e.type == pygame.MOUSEWHEEL:
                cam.zoom_at(pygame.mouse.get_pos(), ZOOM_STEP if e.y>0 else 1/ZOOM_STEP)
                world.refresh_dots()
            elif e.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()

                # nav grid
                plus, up, minus, left, down, right = nav_rects
                if   plus.collidepoint(mouse):  cam.zoom_at((sw//2, sh//2), ZOOM_STEP)
                elif minus.collidepoint(mouse): cam.zoom_at((sw//2, sh//2), 1/ZOOM_STEP)
                elif up.collidepoint(mouse):    cam.pos = (cam.pos[0], cam.pos[1] - PAN_STEP_SCR/cam.zoom)
                elif down.collidepoint(mouse):  cam.pos = (cam.pos[0], cam.pos[1] + PAN_STEP_SCR/cam.zoom)
                elif left.collidepoint(mouse):  cam.pos = (cam.pos[0] - PAN_STEP_SCR/cam.zoom, cam.pos[1])
                elif right.collidepoint(mouse): cam.pos = (cam.pos[0] + PAN_STEP_SCR/cam.zoom, cam.pos[1])

                # style popup
                if world.selecting_style and world.selector_rect and world.selector_rect.collidepoint(mouse):
                    if world.pref_rect.collidepoint(mouse):
                        world.style_next = 0; world.place_with_style(world.pending_ax, 0); world.close_style_selector()
                    elif world.built_rect.collidepoint(mouse):
                        world.style_next = 1; world.place_with_style(world.pending_ax, 1); world.close_style_selector()
                    continue
                elif world.selecting_style:
                    world.close_style_selector()

                # equipment arrows
                if world.equip_open and world.equip_rect and world.equip_rect.collidepoint(mouse) and world.selected:
                    mod = world.modulos[world.selected]
                    for idx, al, ar, label, cell in world.equip_slot_rects:
                        if al.collidepoint(mouse): mod.equip[idx] = (mod.equip[idx]-1) % 2
                        elif ar.collidepoint(mouse): mod.equip[idx] = (mod.equip[idx]+1) % 2
                    continue

                # place/delete/select
                if world.try_delete_from_red(mouse):
                    pass
                elif world.try_place_from_green(mouse):
                    pass  # style popup opens
                else:
                    world.select_or_toggle(mouse)

                if back_rect.collidepoint(mouse): running = False

        world.draw()

        # HUD title
        sw, sh = screen.get_size()
        count = len(world.modulos)
        txt = f'Modules: {count}'
        txt_surf = font_title.render(txt, True, PALETTE['white'])
        screen.blit(txt_surf, txt_surf.get_rect(center=(sw//2, 20 + txt_surf.get_height()//2)))

        # metrics left panel
        _draw_metrics_panel(screen, totals, x=12, top=12, width=210)

        # save/back
        pygame.draw.rect(screen, PALETTE['ui'], save_rect, border_radius=8)
        pygame.draw.rect(screen, PALETTE['ui_border'], save_rect.inflate(6,6), 3, border_radius=10)
        screen.blit(font_button.render('Save', True, PALETTE['white']),
                    font_button.render('Save', True, PALETTE['white']).get_rect(center=save_rect.center))
        pygame.draw.rect(screen, PALETTE['ui'], back_rect, border_radius=8)
        pygame.draw.rect(screen, PALETTE['ui_border'], back_rect.inflate(6,6), 3, border_radius=10)
        screen.blit(font_button.render('Back', True, PALETTE['white']),
                    font_button.render('Back', True, PALETTE['white']).get_rect(center=back_rect.center))

        # nav grid
        _draw_nav_grid(screen, nav_rects)

        pygame.display.flip()
        clock.tick(FPS)

    return

if __name__ == "__main__":
    screen = create_window()
    modulos_screen(screen)
