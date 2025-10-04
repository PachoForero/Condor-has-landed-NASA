import sys
import math
import pygame

# -------------------- Config --------------------
APP_NAME = "Hábitat Hexagonal con Pan y Zoom"
PALETTE = {
    "fondo": (20, 20, 24),
    "borde": (40, 40, 48),
    "estilo_a": (60, 130, 200),
    "estilo_b": (230, 160, 60),
    "verde": (30, 200, 90),
    "rojo": (220, 60, 60),
    "blanco": (240, 240, 240),
}
HEX_SIZE = 45          # radio del hexágono (vértice al centro) en coordenadas mundo
DOT_R_SCR = 9          # radio de puntos en pixeles de pantalla
LINE_W = 2
FPS = 60

# Axial neighbors (pointy-top)
NEI = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
SQRT3 = math.sqrt(3.0)

# -------------------- Geometría hex --------------------
def axial_to_world(q, r):
    # origen (0,0) en mundo, luego cámara lo mapea a pantalla
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

    def apply_to_poly(self, poly_world):
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
        # mover cámara en sentido opuesto, escalado por zoom
        self.pos = (self.pos[0] - dx / self.zoom, self.pos[1] - dy / self.zoom)
        self._last_mouse = mouse_pos

    def zoom_at(self, mouse_screen, zoom_factor):
        # zoom hacia el cursor: mantener punto mundo bajo el cursor fijo
        before = self.screen_to_world(mouse_screen)
        self.zoom = max(self.min_zoom, min(self.max_zoom, self.zoom * zoom_factor))
        after = self.screen_to_world(mouse_screen)
        self.pos = (self.pos[0] + (before[0] - after[0]),
                    self.pos[1] + (before[1] - after[1]))

# -------------------- Módulo --------------------
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
        self.modulos = {}           # (q,r) -> Modulo
        self.base_ax = (0, 0)
        self.selected = None
        self.green_dots_screen = [] # [(axial, (sx,sy))]
        self.red_dot_screen = None
        self.style_next = 1

        self.modulos[self.base_ax] = Modulo(0, 0, style=0)

    # ---- Geometría y picking ----
    def center_world_of(self, axial):
        return axial_to_world(axial[0], axial[1])

    def poly_world_of(self, axial):
        return hex_points_world(self.center_world_of(axial))

    def pick_modulo(self, mouse_screen):
        # convertir mouse a coords mundo para probar polígono en mundo
        mouse_world = self.cam.screen_to_world(mouse_screen)
        for ax, m in self.modulos.items():
            poly_w = self.poly_world_of(ax)
            if point_in_polygon(mouse_world, poly_w):
                return ax
        return None

    # ---- Dots ----
    def refresh_dots(self):
        self.green_dots_screen.clear()
        self.red_dot_screen = None
        if self.selected is None:
            return

        # punto rojo en el centro del módulo seleccionado
        c_w = self.center_world_of(self.selected)
        self.red_dot_screen = self.cam.world_to_screen(c_w)

        # puntos verdes en lados con vecino libre
        for nb in Modulo(*self.selected).neighbors_axial():
            if nb not in self.modulos:
                c1_w = self.center_world_of(nb)
                mid_w = ((c_w[0] + c1_w[0]) * 0.5, (c_w[1] + c1_w[1]) * 0.5)
                mid_s = self.cam.world_to_screen(mid_w)
                self.green_dots_screen.append((nb, mid_s))

    # ---- Acciones ----
    def select_or_clear(self, mouse_screen):
        ax = self.pick_modulo(mouse_screen)
        if ax is None:
            self.selected = None
        else:
            self.selected = ax
        self.refresh_dots()

    def try_place_from_green(self, mouse_screen):
        r2 = DOT_R_SCR * DOT_R_SCR
        for nb, pos_s in self.green_dots_screen:
            dx = mouse_screen[0] - pos_s[0]
            dy = mouse_screen[1] - pos_s[1]
            if dx*dx + dy*dy <= r2:
                if nb not in self.modulos:
                    self.modulos[nb] = Modulo(nb[0], nb[1], style=self.style_next)
                    self.style_next ^= 1
                self.selected = nb
                self.refresh_dots()
                return True
        return False

    def try_delete_from_red(self, mouse_screen):
        if self.selected is None or self.red_dot_screen is None:
            return False
        if self.selected == self.base_ax:
            return False
        dx = mouse_screen[0] - self.red_dot_screen[0]
        dy = mouse_screen[1] - self.red_dot_screen[1]
        if dx*dx + dy*dy <= DOT_R_SCR * DOT_R_SCR:
            del self.modulos[self.selected]
            self.selected = None
            self.refresh_dots()
            return True
        return False

    # ---- Render ----
    def draw(self, screen):
        screen.fill(PALETTE["fondo"])

        # módulos
        for ax, m in self.modulos.items():
            poly_w = self.poly_world_of(ax)
            poly_s = self.cam.apply_to_poly(poly_w)
            pygame.draw.polygon(screen, m.color(), poly_s)
            pygame.draw.polygon(screen, PALETTE["borde"], poly_s, LINE_W)

        # puntos verdes
        if self.selected is not None:
            for _, pos_s in self.green_dots_screen:
                pygame.draw.circle(screen, PALETTE["verde"], (int(pos_s[0]), int(pos_s[1])), DOT_R_SCR)
                pygame.draw.circle(screen, PALETTE["blanco"], (int(pos_s[0]), int(pos_s[1])), DOT_R_SCR, 2)

            # punto rojo si no es el base
            if self.selected != self.base_ax and self.red_dot_screen is not None:
                rx, ry = self.red_dot_screen
                pygame.draw.circle(screen, PALETTE["rojo"], (int(rx), int(ry)), DOT_R_SCR)
                pygame.draw.circle(screen, PALETTE["blanco"], (int(rx), int(ry)), DOT_R_SCR, 2)

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
    clock = pygame.time.Clock()
    cam = Camera(screen)
    world = Mundo(cam)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False

            elif e.type == pygame.VIDEORESIZE:
                screen = pygame.display.get_surface()
                cam.set_screen(screen)
                world.refresh_dots()

            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    running = False
                elif e.key == pygame.K_F11:
                    toggle_fullscreen()
                    cam.set_screen(pygame.display.get_surface())
                    world.refresh_dots()
                elif e.key == pygame.K_r and world.selected is not None:
                    # alterna estilo del módulo seleccionado
                    m = world.modulos[world.selected]
                    m.style ^= 1

            # Zoom con rueda
            elif e.type == pygame.MOUSEWHEEL:
                if e.y > 0:
                    cam.zoom_at(pygame.mouse.get_pos(), 1.1)
                elif e.y < 0:
                    cam.zoom_at(pygame.mouse.get_pos(), 1/1.1)
                world.refresh_dots()

            # Pan con botón derecho
            elif e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 3:
                    cam.start_drag(pygame.mouse.get_pos())
                elif e.button == 1:
                    mouse = pygame.mouse.get_pos()
                    if world.try_delete_from_red(mouse):
                        pass
                    elif world.try_place_from_green(mouse):
                        pass
                    else:
                        world.select_or_clear(mouse)

            elif e.type == pygame.MOUSEBUTTONUP:
                if e.button == 3:
                    cam.stop_drag()

            elif e.type == pygame.MOUSEMOTION:
                if pygame.mouse.get_pressed(num_buttons=3)[2]:
                    cam.drag_update(pygame.mouse.get_pos())

        world.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
