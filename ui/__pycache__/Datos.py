import pygame
import sys

WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)


class InputBox:
    def __init__(self, rect, font, text=''):
        self.rect = pygame.Rect(rect)
        self.color_inactive = (180, 180, 180)
        self.color_active = (100, 100, 255)
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.txt_surface = font.render(text, True, BLACK)
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            # If the user clicked on the input_box rect.
            if self.rect.collidepoint(event.pos):
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if self.active else self.color_inactive
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                self.color = self.color_inactive
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            else:
                # Basic character input (ignore non-printables)
                if len(event.unicode) > 0:
                    self.text += event.unicode
            self.txt_surface = self.font.render(self.text, True, BLACK)

    def update(self):
        width = max(200, self.txt_surface.get_width()+10)
        self.rect.w = width

    def draw(self, screen):
        # Blit the text.
        screen.blit(self.txt_surface, (self.rect.x+5, self.rect.y+5))
        # Blit the rect.
        pygame.draw.rect(screen, self.color, self.rect, 2, border_radius=6)


def datos_screen(screen):
    clock = pygame.time.Clock()
    font_title = pygame.font.SysFont(None, 40)
    font_label = pygame.font.SysFont(None, 26)
    font_input = pygame.font.SysFont(None, 24)

    title_text = font_title.render("Datos - Responde las preguntas", True, BLUE)
    title_rect = title_text.get_rect(center=(WIDTH//2, 40))

    questions = [
        "1) Nombre:",
        "2) Edad:",
        "3) Ocupación:",
        "4) Comentarios:",
    ]

    input_boxes = []
    start_y = 90
    gap = 60
    for i in range(len(questions)):
        rect = (200, start_y + i*gap, 280, 32)
        input_boxes.append(InputBox(rect, font_input))

    # Buttons
    submit_rect = pygame.Rect(WIDTH//2 - 90, HEIGHT - 70, 80, 36)
    back_rect = pygame.Rect(WIDTH//2 + 10, HEIGHT - 70, 80, 36)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for box in input_boxes:
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if submit_rect.collidepoint(event.pos):
                    # For now, print the responses to console and continue
                    responses = [b.text for b in input_boxes]
                    print("Respuestas:", responses)
                elif back_rect.collidepoint(event.pos):
                    running = False

        screen.fill(WHITE)
        screen.blit(title_text, title_rect)

        # Draw questions and inputs
        for i, q in enumerate(questions):
            label = font_label.render(q, True, BLACK)
            screen.blit(label, (40, 95 + i*gap))
            input_boxes[i].update()
            input_boxes[i].draw(screen)

        # Draw buttons
        pygame.draw.rect(screen, GRAY, submit_rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, back_rect, border_radius=8)
        txt_submit = font_label.render("Enviar", True, BLACK)
        txt_back = font_label.render("Volver", True, BLACK)
        screen.blit(txt_submit, txt_submit.get_rect(center=submit_rect.center))
        screen.blit(txt_back, txt_back.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    datos_screen(screen)
