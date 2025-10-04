import sys
import math
import pygame

# -------------------- Config --------------------
APP_NAME = "Hábitat Hexagonal"
PALETTE = {
    "fondo": (20, 20, 24),
    "borde": (40, 40, 48),
    "estilo_a": (60, 130, 200),
    "estilo_b": (230, 160, 60),
    "verde": (30, 200, 90),
    "rojo": (220, 60, 60),
    "blanco": (240, 240, 240),
}
HEX_SIZE = 45          # radio del hexágono (vértice al centro)
DOT_R = 9              # radio de los puntos verde/rojo
LINE_W = 2             # grosor de bordes
FPS = 60

# Axial neighbors (pointy-top)
NEI = [(1,0),(1,-1),(0,-1),(-1,0),(-1,1),(0,1)]
SQRT3 = math.sqrt(3.0)

# -------------------- Geometría --------------------
def axial_to_pixel(q, r, origin):
    x = HEX_SIZE * SQRT3 * (q + r/2)
    y = HEX_SIZE * 1.5 * r
    return (origin[0] + x, origin[1] + y)

def hex_points(center):
    cx, cy = center
    pts = []
    for i in range(6):
        ang = math.radians(60 * i - 30)  # pointy-top
        pts.append((cx + HEX_SIZE * math.cos(ang),
                    cy + HEX_SIZE * math.sin(ang)))
    return pts

def point_in_polygon(pt, poly):
    # Ray casting
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

def dist2(a, b):
    dx = a[0]-b[0]; dy = a[1]-b[1]
    return dx*dx + dy*dy

# -------------------- Clase Módulo --------------------
class Modulo:
    __slots__ = ("q", "r", "style")
    def __init__(self, q, r, style=0):
        self.q = q
        self.r = r
        self.style = style  # 0 o 1

    def axial(self):
        return (self.q, self.r)

    def color(self):
        return PALETTE["estilo_a"] if self.style == 0 else PALETTE["estilo_b"]

    def neighbors_axial(self):
        q, r = self.q, self.r
        for dq, dr in NEI:
            yield (q + dq, r + dr)

# -------------------- Estado --------------------
class Mundo:
    def __init__(self, screen):
        self.screen = screen
        self.center = (screen.get_width()//2, screen.get_height()//2)
        self.modulos = {}  # (q,r) -> Modulo
        self.base_ax = (0, 0)
        self.selected = None
        self.candidate_dots = []  # [(axial, pos_pix)]
        self.red_dot = None       # (pos_pix)
        self.style_next = 1       # alterna estilos al crear

        # Crear módulo base
        base = Modulo(0, 0, style=0)
        self.modulos[(0,0)] = base

    # ---- Conversión y formas ----
    def center_of(self, axial):
        return axial_to_pixel(axial[0], axial[1], self.center)

    def polygon_of(self, axial):
        return hex_points(self.center_of(axial))

    # ---- Picking ----
    def pick_modulo(self, mouse):
        for ax, m in self.modulos.items():
            poly = self.polygon_of(ax)
            if point_in_polygon(mouse, poly):
                return ax
        return None

    # ---- Dots ----
    def refresh_dots(self):
        self.candidate_dots.clear()
        self.red_dot = None
        if self.selected is None:
            return
        ax = self.selected
        # Punto rojo sobre el centro del módulo seleccionado
        self.red_dot = self.center_of(ax)

        # Verdes en lados vacíos
        c0 = self.center_of(ax)
        for nb in Modulo(*ax).neighbors_axial():
            if nb not in self.modulos:
                c1 = self.center_of(nb)
                mid = ((c0[0] + c1[0]) * 0.5, (c0[1] + c1[1]) * 0.5)
                self.candidate_dots.append((nb, mid))

    # ---- Acciones ----
    def select_or_toggle(self, mouse):
        ax = self.pick_modulo(mouse)
        if ax is None:
            # clic vacío deselecciona
            self.selected = None
            self.refresh_dots()
            return
        self.selected = ax
        self.refresh_dots()

    def try_place_from_green(self, mouse):
        r2 = DOT_R * DOT_R
        for nb, pos in self.candidate_dots:
            if dist2(mouse, pos) <= r2:
                # crear módulo si libre
                if nb not in self.modulos:
                    self.modulos[nb] = Modulo(nb[0], nb[1], style=self.style_next)
                    self.style_next ^= 1
                self.selected = nb
                self.refresh_dots()
                return True
        return False

    def try_delete_from_red(self, mouse):
        if self.selected is None or self.red_dot is None:
            return False
        # no borrar el base
        if self.selected == self.base_ax:
            return False
        if dist2(mouse, self.red_dot) <= DOT_R * DOT_R:
            # borrar
            del self.modulos[self.selected]
            self.selected = None
            self.refresh_dots()
            return True
        return False

    # ---- Render ----
    def draw(self):
        surf = self.screen
        surf.fill(PALETTE["fondo"])

        # Dibujar módulos
        for ax, m in self.modulos.items():
            poly = self.polygon_of(ax)
            pygame.draw.polygon(surf, m.color(), poly)
            pygame.draw.polygon(surf, PALETTE["borde"], poly, LINE_W)

        # Dots si hay selección
        if self.selected is not None:
            # verdes
            for _, pos in self.candidate_dots:
                pygame.draw.circle(surf, PALETTE["verde"], (int(pos[0]), int(pos[1])), DOT_R)
                pygame.draw.circle(surf, PALETTE["blanco"], (int(pos[0]), int(pos[1])), DOT_R, 2)
            # rojo
            if self.selected != self.base_ax and self.red_dot is not None:
                pygame.draw.circle(surf, PALETTE["rojo"], (int(self.red_dot[0]), int(self.red_dot[1])), DOT_R)
                pygame.draw.circle(surf, PALETTE["blanco"], (int(self.red_dot[0]), int(self.red_dot[1])), DOT_R, 2)

# -------------------- App --------------------
def create_window():
    pygame.init()
    pygame.display.set_caption(APP_NAME)
    info = pygame.display.Info()
    desk_w, desk_h = info.current_w, info.current_h
    # Ventana 90% centrada; F11 para fullscreen
    pygame.display.set_mode((int(desk_w*0.9), int(desk_h*0.9)), pygame.RESIZABLE)
    return pygame.display.get_surface()

def toggle_fullscreen():
    flags = pygame.display.get_surface().get_flags()
    info = pygame.display.Info()
    if flags & pygame.FULLSCREEN:
        pygame.display.set_mode((int(info.current_w*0.9), int(info.current_h*0.9)), pygame.RESIZABLE)
    else:
        pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)

def main():
    screen = create_window()
    modulos_screen(screen)


def modulos_screen(screen):
    """Run the Modulos app using an existing pygame `screen`.

    This version does not call pygame.quit() or sys.exit() when the user
    returns; instead it returns control to the caller (like `datos_screen`).
    Press ESC to go back to the caller. Closing the window will quit the app.
    """
    clock = pygame.time.Clock()
    world = Mundo(screen)

    # Botón volver (tamaño relativo)
    sw, sh = screen.get_size()
    btn_w, btn_h = max(100, int(sw * 0.12)), max(36, int(sh * 0.06))
    back_rect = pygame.Rect(sw - btn_w - 20, sh - btn_h - 20, btn_w, btn_h)

    # Fuentes para título/contador y botones
    font_title = pygame.font.SysFont(None, 32)
    font_button = pygame.font.SysFont(None, 26)

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                # Propagate full quit to exit the whole program (consistent with datos_screen)
                pygame.quit()
                sys.exit()
            elif e.type == pygame.VIDEORESIZE:
                # Recalcular centro al redimensionar
                world.screen = pygame.display.get_surface()
                world.center = (world.screen.get_width()//2, world.screen.get_height()//2)
                world.refresh_dots()
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    # Regresar al llamador en vez de cerrar toda la aplicación
                    running = False
                elif e.key == pygame.K_F11:
                    toggle_fullscreen()
                    world.screen = pygame.display.get_surface()
                    world.center = (world.screen.get_width()//2, world.screen.get_height()//2)
                    world.refresh_dots()
            elif e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
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

        # Dibujar contador superior
        sw, sh = screen.get_size()
        count = len(world.modulos)
        txt = f'Módulos instalados: {count}'
        txt_surf = font_title.render(txt, True, PALETTE['blanco'])
        txt_rect = txt_surf.get_rect(center=(sw//2, 20 + txt_surf.get_height()//2))
        screen.blit(txt_surf, txt_rect)

        # Dibujar botón Volver en la esquina inferior derecha
        pygame.draw.rect(screen, PALETTE['borde'], back_rect, border_radius=8)
        txt_back = font_button.render('Volver', True, PALETTE['blanco'])
        screen.blit(txt_back, txt_back.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(FPS)

    # simplemente retornar control al llamador (no pygame.quit())
    return

if __name__ == "__main__":
    main()