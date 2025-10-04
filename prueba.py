import pygame
import sys

pygame.init()

# Configuración adaptativa
info = pygame.display.Info()
WIDTH = int(info.current_w * 0.9)
HEIGHT = int(info.current_h * 0.9)

SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("App con botones y campos de texto")


FONT = pygame.font.Font(None, 32)
COLOR_BG = (240, 240, 240)
COLOR_TEXT = (0, 0, 0)
COLOR_BOX_INACTIVE = (180, 180, 180)
COLOR_BOX_ACTIVE = (0, 120, 255)
COLOR_BUTTON = (0, 180, 90)
COLOR_BUTTON_TEXT = (255, 255, 255)
COLOR_FRAME = (120, 120, 120)
COLOR_BTN = (200, 200, 200)
COLOR_BTN_HOVER = (180, 180, 180)
COLOR_VALUE_BG = (255, 255, 255)

# Campos de texto
class InputBox:
    def __init__(self, x, y, w, h, text=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.color = COLOR_BOX_INACTIVE
        self.text = text
        self.txt_surface = FONT.render(text, True, COLOR_TEXT)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Activar el campo si se hace clic
            self.active = self.rect.collidepoint(event.pos)
            self.color = COLOR_BOX_ACTIVE if self.active else COLOR_BOX_INACTIVE
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = COLOR_BOX_INACTIVE
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                self.text += event.unicode
            self.txt_surface = FONT.render(self.text, True, COLOR_TEXT)

    def draw(self, screen):
        # Dibujar texto
        screen.blit(self.txt_surface, (self.rect.x + 5, self.rect.y + 5))
        # Dibujar caja
        pygame.draw.rect(screen, self.color, self.rect, 2)

# Botón
class Button:
    def __init__(self, x, y, w, h, text, callback):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.callback = callback

    def draw(self, screen):
        pygame.draw.rect(screen, COLOR_BUTTON, self.rect)
        txt_surface = FONT.render(self.text, True, COLOR_BUTTON_TEXT)
        screen.blit(txt_surface, (self.rect.x + 10, self.rect.y + 10))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
            self.callback()


class Stepper:
    """
    Control numérico: [Label] [ caja valor ][ ^ ]
                                   [  v  ]
    """
    def __init__(self, x, y, label, value=0, step=1, vmin=None, vmax=None, w=180, h=40):
        self.x, self.y = x, y
        self.label = label
        self.value = value
        self.step = step
        self.vmin = vmin
        self.vmax = vmax

        # Layout
        self.w = w
        self.h = h
        self.label_surface = FONT.render(self.label, True, COLOR_TEXT)

        # Rect principal del valor
        self.value_rect = pygame.Rect(self.x + self.label_surface.get_width() + 16, self.y, self.w, self.h)

        # Zona botones: dos botones verticales a la derecha del value_rect
        btn_w = int(self.h * 0.6)
        btn_h = self.h // 2
        self.btn_up = pygame.Rect(self.value_rect.right + 6, self.y, btn_w, btn_h)
        self.btn_dn = pygame.Rect(self.value_rect.right + 6, self.y + btn_h, btn_w, btn_h)

        # Estados hover
        self.hover_up = False
        self.hover_dn = False
        self.hover_value = False

    def clamp(self):
        if self.vmin is not None:
            self.value = max(self.vmin, self.value)
        if self.vmax is not None:
            self.value = min(self.vmax, self.value)

    def increment(self, n=1):
        self.value += self.step * n
        self.clamp()

    def decrement(self, n=1):
        self.value -= self.step * n
        self.clamp()

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            mx, my = event.pos
            self.hover_up = self.btn_up.collidepoint(mx, my)
            self.hover_dn = self.btn_dn.collidepoint(mx, my)
            self.hover_value = self.value_rect.collidepoint(mx, my)

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # clic izquierdo
                if self.btn_up.collidepoint(event.pos):
                    self.increment(1)
                elif self.btn_dn.collidepoint(event.pos):
                    self.decrement(1)

        if event.type == pygame.KEYDOWN and self.hover_value:
            if event.key in (pygame.K_UP, pygame.K_RIGHT):
                self.increment(1)
            elif event.key in (pygame.K_DOWN, pygame.K_LEFT):
                self.decrement(1)
            elif event.key == pygame.K_PAGEUP:
                self.increment(5)
            elif event.key == pygame.K_PAGEDOWN:
                self.decrement(5)

    def draw_triangle(self, surface, rect, up=True, hover=False):
        color = COLOR_BTN_HOVER if hover else COLOR_BTN
        pygame.draw.rect(surface, color, rect, border_radius=4)
        # Triángulo centrado
        cx = rect.centerx
        if up:
            pts = [(cx, rect.top + 6), (rect.left + 6, rect.bottom - 6), (rect.right - 6, rect.bottom - 6)]
        else:
            pts = [(rect.left + 6, rect.top + 6), (rect.right - 6, rect.top + 6), (cx, rect.bottom - 6)]
        pygame.draw.polygon(surface, COLOR_TEXT, pts)

    def draw(self, screen):
        # Label
        screen.blit(self.label_surface, (self.x, self.y + (self.h - self.label_surface.get_height()) // 2))

        # Caja de valor
        pygame.draw.rect(screen, COLOR_VALUE_BG, self.value_rect, border_radius=6)
        pygame.draw.rect(screen, COLOR_FRAME, self.value_rect, 2, border_radius=6)

        # Texto de valor
        val_txt = FONT.render(str(self.value), True, COLOR_TEXT)
        screen.blit(val_txt, (self.value_rect.x + 10, self.value_rect.y + (self.h - val_txt.get_height()) // 2))

        # Botones ↑ y ↓
        self.draw_triangle(screen, self.btn_up, up=True, hover=self.hover_up)
        self.draw_triangle(screen, self.btn_dn, up=False, hover=self.hover_dn)

    def get_value(self):
        return self.value
    

# Variables
values = {}

# Función para guardar
def save_values():
    global values
    values = {f"campo_{i+1}": box.text for i, box in enumerate(input_boxes)}
    print("Valores guardados:", values)

# Crear campos de texto
input_boxes = [InputBox(150, 50 + i*60, 200, 32) for i in range(3)]
save_button = Button(200, 250, 100, 40, "Guardar", save_values)

# Bucle principal
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        for box in input_boxes:
            box.handle_event(event)
        save_button.handle_event(event)

    SCREEN.fill(COLOR_BG)

    for i, box in enumerate(input_boxes):
        label = FONT.render(f"Valor {i+1}:", True, COLOR_TEXT)
        SCREEN.blit(label, (60, 55 + i*60))
        box.draw(SCREEN)

    save_button.draw(SCREEN)

    pygame.display.flip()
