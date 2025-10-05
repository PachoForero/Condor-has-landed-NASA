import sys
import math
import pygame
import os

# -------------------- Config --------------------
APP_NAME = "Hábitat Hexagonal — Pan, Zoom y UI"
PALETTE = {
    "fondo": (20, 20, 24),
    "borde": (40, 40, 48),
    "estilo_a": (60, 130, 200),
    "estilo_b": (230, 160, 60),
    "verde": (30, 200, 90),
    "rojo": (220, 60, 60),
    "blanco": (240, 240, 240),
    "btn_back": (70, 75, 90),
    "btn_save": (60, 140, 110),
    "ui_panel": (28, 28, 34),
    "ui_border": (90, 90, 100),
}
HEX_SIZE = 45      # tamaño en coordenadas de mundo (no pantalla)
DOT_R = 9          # radio de puntos en pixeles de pantalla
LINE_W = 2
FPS = 60

# Axial neighbors (pointy-top)
NEI = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
SQRT3 = math.sqrt(3.0)

# -------------------- Geometría mundo --------------------
def axial_to_world(q, r):
    x = HEX_SIZE * SQRT3 * (q + r/2)
    y = HEX_SIZE * 1.5 * r
    return (x, y)

def hex_points_world(center_w):
    cx, cy = center_w
    pts = []
    for i in range(6):
        ang = math.radians(60 * i - 30)  # pointy-top
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
            if x < xinters:
                inside = not inside
    return inside

# -------------------- Cámara --------------------
class Camera:
    def __init__(self, screen):
        self.screen = screen
        self.zoom = 1.0
        self.min_zoom = 0.3
        self.max_zoom = 3.0
        self.pos = (0.0, 0.0)  # centro de la pantalla en coords mundo
        self._dragging = False
        self._last_mouse = (0, 0)

    def set_screen(self, screen):
        self.screen = screen

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

    def start_drag(self, mouse_pos):
        self._dragging = True
        self._last_mouse = mouse_pos

    def stop_drag(self):
        self._dragging = False

    def drag_update(self, mouse_pos):
        if not self._dragging: return
        dx = mouse_pos[0] - self._last_mouse[0]
        dy = mouse_pos[1] - self._last_mouse[1]
        self.pos = (self.pos[0] - dx / self.zoom, self.pos[1] - dy / self.zoom)
        self._last_mouse = mouse_pos

    def zoom_at(self, mouse_screen, zoom_factor):
        before = self.screen_to_world(mouse_screen)
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * zoom_factor))
        after = self.screen_to_world(mouse_screen)
        self.pos = (self.pos[0] + (before[0] - after[0]),
                    self.pos[1] + (before[1] - after[1]))

# -------------------- Clase Módulo --------------------
class Modulo:
    __slots__ = ("q", "r", "style")
    def __init__(self, q, r, style=0):
        self.q = q
        self.r = r
        self.style = style  # 0 o 1

    def axial(self): return (self.q, self.r)
    def color(self):
        return PALETTE["estilo_a"] if self.style == 0 else PALETTE["estilo_b"]

    def neighbors_axial(self):
        q, r = self.q, self.r
        for dq, dr in NEI:
            yield (q + dq, r + dr)

# -------------------- Mundo --------------------
class Mundo:
    def __init__(self, camera):
        self.cam = camera
        self.screen = camera.screen
        self.modulos = {}              # (q,r) -> Modulo
        self.base_ax = (0, 0)
        self.selected = None
        self.green_dots_screen = []    # [(axial, (sx,sy))]
        self.red_dot_screen = None
        self.style_next = 1

        # base
        self.modulos[(0,0)] = Modulo(0, 0, style=0)

    # centros y polígonos en mundo
    def center_world_of(self, axial):
        return axial_to_world(axial[0], axial[1])

    def poly_world_of(self, axial):
        return hex_points_world(self.center_world_of(axial))

    # picking
    def pick_modulo(self, mouse_screen):
        mouse_world = self.cam.screen_to_world(mouse_screen)
        for ax in self.modulos:
            poly_w = self.poly_world_of(ax)
            if point_in_polygon(mouse_world, poly_w):
                return ax
        return None

    # UI dots
    def refresh_dots(self):
        self.green_dots_screen.clear()
        self.red_dot_screen = None
        if self.selected is None:
            return
        c_w = self.center_world_of(self.selected)
        self.red_dot_screen = self.cam.world_to_screen(c_w)

        for nb in Modulo(*self.selected).neighbors_axial():
            if nb not in self.modulos:
                c1_w = self.center_world_of(nb)
                mid_w = ((c_w[0] + c1_w[0]) * 0.5, (c_w[1] + c1_w[1]) * 0.5)
                self.green_dots_screen.append((nb, self.cam.world_to_screen(mid_w)))

    # detectar clic en dot verde sin crear aún
    def green_hit(self, mouse_screen):
        r2 = DOT_R * DOT_R
        for nb, pos_s in self.green_dots_screen:
            dx = mouse_screen[0] - pos_s[0]
            dy = mouse_screen[1] - pos_s[1]
            if dx*dx + dy*dy <= r2:
                return nb, pos_s
        return None

    # colocar con estilo elegido
    def place_with_style(self, axial, style):
        if axial not in self.modulos:
            self.modulos[axial] = Modulo(axial[0], axial[1], style=style)
        self.selected = axial
        self.refresh_dots()

    def try_delete_from_red(self, mouse_screen):
        if self.selected is None or self.red_dot_screen is None:
            return False
        if self.selected == self.base_ax:
            return False
        dx = mouse_screen[0] - self.red_dot_screen[0]
        dy = mouse_screen[1] - self.red_dot_screen[1]
        if dx*dx + dy*dy <= DOT_R * DOT_R:
            del self.modulos[self.selected]
            self.selected = None
            self.refresh_dots()
            return True
        return False

    def try_place_from_green(self, mouse_screen):
        """If click hits a green dot, place a module there with current next style."""
        hit = self.green_hit(mouse_screen)
        if hit is None:
            return False
        axial, _ = hit
        self.place_with_style(axial, self.style_next)
        return True

    def select_or_toggle(self, mouse_screen):
        """Select a module if clicked; deselect if clicking same or empty."""
        picked = self.pick_modulo(mouse_screen)
        if picked is None:
            # clicked empty space -> deselect
            self.selected = None
        else:
            if self.selected == picked:
                self.selected = None
            else:
                self.selected = picked
        self.refresh_dots()

    def set_screen(self, screen):
        self.screen = screen
        # ensure any screen-space dots are recalculated
        self.refresh_dots()

    # ---- Render ----
    def draw(self):
        surf = self.screen
        surf.fill(PALETTE["fondo"])

        for ax, mod in self.modulos.items():
            poly_w = self.poly_world_of(ax)
            poly_s = self.cam.apply_poly(poly_w)
            pygame.draw.polygon(surf, mod.color(), poly_s)
            pygame.draw.polygon(surf, PALETTE["borde"], poly_s, LINE_W)

        if self.selected is not None:
            for _, pos_s in self.green_dots_screen:
                pygame.draw.circle(surf, PALETTE["verde"], (int(pos_s[0]), int(pos_s[1])), DOT_R)
                pygame.draw.circle(surf, PALETTE["blanco"], (int(pos_s[0]), int(pos_s[1])), DOT_R, 2)

            if self.selected != self.base_ax and self.red_dot_screen is not None:
                rx, ry = self.red_dot_screen
                pygame.draw.circle(surf, PALETTE["rojo"], (int(rx), int(ry)), DOT_R)
                pygame.draw.circle(surf, PALETTE["blanco"], (int(rx), int(ry)), DOT_R, 2)

# -------------------- App --------------------
def create_window():
    pygame.init()
    pygame.display.set_caption(APP_NAME)
    info = pygame.display.Info()
    desk_w, desk_h = info.current_w, info.current_h
    pygame.display.set_mode((int(desk_w*0.9), int(desk_h*0.9)), pygame.RESIZABLE)
    return pygame.display.get_surface()

def toggle_fullscreen():
    surf = pygame.display.get_surface()
    flags = surf.get_flags()
    info = pygame.display.Info()
    if flags & pygame.FULLSCREEN:
        pygame.display.set_mode((int(info.current_w*0.9), int(info.current_h*0.9)), pygame.RESIZABLE)
    else:
        pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)

def main():
    screen = create_window()
    modulos_screen(screen)

def modulos_screen(screen):
    clock = pygame.time.Clock()
    cam = Camera(screen)
    world = Mundo(cam)

    # Botón volver (tamaño relativo)
    sw, sh = screen.get_size()
    btn_h = max(36, int(sh * 0.06))
    pad = 20
    gap = 12
    btn_w = max(120, int(sw * 0.14))
    back_rect = pygame.Rect(sw - btn_w - pad, sh - btn_h - pad, btn_w, btn_h)
    save_rect = pygame.Rect(back_rect.left - gap - btn_w, sh - btn_h - pad, btn_w, btn_h)

    font_title = pygame.font.SysFont(None, 32)
    font_button = pygame.font.SysFont(None, 26)

    # Estado selector de material
    selecting_style = False
    pending_ax = None
    selector_rect = None
    mat1_rect = None
    mat2_rect = None

    def open_selector(anchor_screen_pos):
        nonlocal selecting_style, selector_rect, mat1_rect, mat2_rect
        selecting_style = True
        w, h = 180, 90
        ax, ay = int(anchor_screen_pos[0]), int(anchor_screen_pos[1])
        # Evitar que se salga por el borde
        x = min(max(10, ax - w//2), screen.get_width() - w - 10)
        y = min(max(10, ay - h - 14), screen.get_height() - h - 10)
        selector_rect = pygame.Rect(x, y, w, h)
        # Dos botones
        bw, bh = (w - 3*10)//2, h - 20 - 10  # padding: 10
        mat1_rect = pygame.Rect(x + 10, y + 10, bw, bh)
        mat2_rect = pygame.Rect(x + 20 + bw, y + 10, bw, bh)

    def close_selector():
        nonlocal selecting_style, pending_ax
        selecting_style = False
        pending_ax = None

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif e.type == pygame.VIDEORESIZE:
                screen = pygame.display.get_surface()
                cam.set_screen(screen)
                world.set_screen(screen)
                sw, sh = screen.get_size()
                btn_h = max(36, int(sh * 0.06))
                btn_w = max(120, int(sw * 0.14))
                back_rect = pygame.Rect(sw - btn_w - pad, sh - btn_h - pad, btn_w, btn_h)
                save_rect = pygame.Rect(back_rect.left - gap - btn_w, sh - btn_h - pad, btn_w, btn_h)
                world.refresh_dots()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    if selecting_style:
                        close_selector()
                    else:
                        running = False
                elif e.key == pygame.K_F11:
                    toggle_fullscreen()
                    cam.set_screen(pygame.display.get_surface())
                    world.set_screen(pygame.display.get_surface())
                    sw, sh = cam.sw, cam.sh
                    btn_h = max(36, int(sh * 0.06))
                    btn_w = max(120, int(sw * 0.14))
                    back_rect = pygame.Rect(sw - btn_w - pad, sh - btn_h - pad, btn_w, btn_h)
                    save_rect = pygame.Rect(back_rect.left - gap - btn_w, sh - btn_h - pad, btn_w, btn_h)
                    world.refresh_dots()
                elif e.key == pygame.K_r and world.selected is not None:
                    world.modulos[world.selected].style ^= 1

            elif e.type == pygame.MOUSEWHEEL:
                if not selecting_style:
                    if e.y > 0:
                        cam.zoom_at(pygame.mouse.get_pos(), 1.1)
                    elif e.y < 0:
                        cam.zoom_at(pygame.mouse.get_pos(), 1/1.1)
                    world.refresh_dots()

            elif e.type == pygame.MOUSEBUTTONDOWN:
                mouse = pygame.mouse.get_pos()
                # 1) borrar si clic en rojo
                if world.try_delete_from_red(mouse):
                    pass
                # 2) crear si clic en verde
                elif world.try_place_from_green(mouse):
                    pass
                # 3) seleccionar si clic en módulo o vacío
                else:
                    world.select_or_toggle(mouse)

                # Comprobar si clic en botón Volver
                if back_rect.collidepoint(mouse):
                    running = False

        world.draw()

        # HUD
        sw, sh = screen.get_size()
        count = len(world.modulos)
        txt = f'Módulos instalados: {count}'
        txt_surf = font_title.render(txt, True, PALETTE['blanco'])
        txt_rect = txt_surf.get_rect(center=(sw//2, 20 + txt_surf.get_height()//2))
        screen.blit(txt_surf, txt_rect)

        # Botón Guardar
        pygame.draw.rect(screen, PALETTE['btn_save'], save_rect, border_radius=8)
        txt_save = font_button.render('Guardar', True, PALETTE['blanco'])
        screen.blit(txt_save, txt_save.get_rect(center=save_rect.center))

        # Botón Volver
        pygame.draw.rect(screen, PALETTE['btn_back'], back_rect, border_radius=8)
        txt_back = font_button.render('Volver', True, PALETTE['blanco'])
        screen.blit(txt_back, txt_back.get_rect(center=back_rect.center))

        # Selector de material
        if selecting_style and selector_rect:
            pygame.draw.rect(screen, PALETTE["ui_panel"], selector_rect, border_radius=10)
            pygame.draw.rect(screen, PALETTE["ui_border"], selector_rect, 2, border_radius=10)

            # Botón Material 1
            pygame.draw.rect(screen, PALETTE["estilo_a"], mat1_rect, border_radius=8)
            m1 = font_button.render("Material 1", True, PALETTE["blanco"])
            screen.blit(m1, m1.get_rect(center=mat1_rect.center))

            # Botón Material 2
            pygame.draw.rect(screen, PALETTE["estilo_b"], mat2_rect, border_radius=8)
            m2 = font_button.render("Material 2", True, PALETTE["blanco"])
            screen.blit(m2, m2.get_rect(center=mat2_rect.center))

        pygame.display.flip()
        clock.tick(FPS)

    return

if __name__ == "__main__":
    main()
