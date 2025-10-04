import pygame
import sys

pygame.init()

# Configuración
WIDTH, HEIGHT = 500, 400
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("App con botones y campos de texto")

FONT = pygame.font.Font(None, 32)
COLOR_BG = (240, 240, 240)
COLOR_TEXT = (0, 0, 0)
COLOR_BOX_INACTIVE = (180, 180, 180)
COLOR_BOX_ACTIVE = (0, 120, 255)
COLOR_BUTTON = (0, 180, 90)
COLOR_BUTTON_TEXT = (255, 255, 255)

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

