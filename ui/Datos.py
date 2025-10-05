import os
import pygame
import sys
import subprocess

WHITE = (255, 255, 255)
BLUE = (30, 144, 255)
TITLE_COLOR = (34, 49, 73)  # #223149
GRAY = (200, 200, 200)
# Text color requested: #EEE5CA
TEXT_COLOR = (238, 229, 202)
BLACK = (0, 0, 0)

# Defaults for standalone execution
DEFAULT_WIDTH, DEFAULT_HEIGHT = 1920, 1080


class InputBox:
    def __init__(self, rect, font, text=''):
        self.rect = pygame.Rect(rect)
        self.color_inactive = (180, 180, 180)
        self.color_active = (100, 100, 255)
        self.color = self.color_inactive
        self.text = text
        self.font = font
        self.txt_surface = font.render(text, True, TEXT_COLOR)
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
            self.txt_surface = self.font.render(self.text, True, TEXT_COLOR)

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
    # Load and prepare background image (mirrored)
    try:
        base_path = os.path.dirname(__file__)
        img_path = os.path.join(base_path, 'datosb.jpg')
        bg_image = pygame.image.load(img_path).convert()
    except Exception:
        # Fallback: try parent folder or use a plain fill if not found
        try:
            img_path = os.path.join(base_path, '..', 'datosb.jpg')
            bg_image = pygame.image.load(img_path).convert()
        except Exception:
            bg_image = None
    font_title = pygame.font.SysFont(None, 40)
    font_label = pygame.font.SysFont(None, 26)
    font_input = pygame.font.SysFont(None, 24)

    sw, sh = screen.get_size()
    # Scale and flip background to mirror horizontally if available.
    # Use smoothscale and maintain aspect ratio, then center-crop to cover the screen
    if bg_image:
        img_w, img_h = bg_image.get_size()
        # Determine scale factor to cover the screen (cover strategy)
        scale = max(sw / img_w, sh / img_h)
        new_w = int(img_w * scale)
        new_h = int(img_h * scale)
        # Use smoothscale for better quality when enlarging
        try:
            bg_image = pygame.transform.smoothscale(bg_image, (new_w, new_h))
        except Exception:
            bg_image = pygame.transform.scale(bg_image, (new_w, new_h))
        # Center-crop to screen size
        crop_x = (new_w - sw) // 2
        crop_y = (new_h - sh) // 2
        bg_image = bg_image.subsurface((crop_x, crop_y, sw, sh)).copy()
        bg_image = pygame.transform.flip(bg_image, True, False)  # horizontal flip (mirror)
    title_text = font_title.render("Datos - Responde las preguntas", True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(sw//2, int(sh*0.08)))

    questions = [
        "1) N° de personas:",
        "2) Ubicación de la misión:",
        "3) Duración (meses):",
        "4) N° de módulos:",
    ]

    # Form dimensions (centered)
    form_w = min(600, int(sw * 0.6))
    form_h = int(sh * 0.6)
    form_x = (sw - form_w) // 2
    form_y = int(sh * 0.15)

    # Create input boxes for all questions except the second (index 1)
    input_boxes = {}
    start_y = form_y + 60
    gap = max(60, int(form_h * 0.12))
    input_w = int(form_w * 0.65)
    label_x = form_x + int(form_w * 0.05)
    input_x = form_x + int(form_w * 0.3)
    for i in range(len(questions)):
        if i == 1:
            # Skip creating an input for the second question (location)
            continue
        rect = (input_x, start_y + i*gap, input_w, 32)
        input_boxes[i] = InputBox(rect, font_input)

    # Buttons: Enviar y Volver permanecen centrados debajo del formulario.
    # El botón 'Location Y' se reubica debajo del primer cuadro de texto
    # y se alinea horizontalmente con la etiqueta de la segunda pregunta (label_x).
    btn_w, btn_h = 120, 40
    spacing = 12
    total_w = btn_w * 2 + spacing  # Solo Enviar y Volver en la línea inferior
    start_x = sw//2 - total_w//2
    submit_rect = pygame.Rect(start_x, form_y + form_h - 50, btn_w, btn_h)
    back_rect = pygame.Rect(start_x + (btn_w + spacing), form_y + form_h - 50, btn_w, btn_h)

    # Colocar Location a la derecha de la etiqueta de la segunda pregunta
    # y alineado verticalmente con esa etiqueta (index 1).
    # Calculamos la posición x usando el ancho renderizado de la etiqueta
    # para que quede justo a su derecha con un pequeño margen.
    label_for_location = font_label.render(questions[1], True, TEXT_COLOR)
    label_width = label_for_location.get_width()
    small_margin = 12
    location_x = label_x + label_width + small_margin
    # Alinear verticalmente con la etiqueta de la segunda pregunta
    location_y = start_y + 1*gap
    location_rect = pygame.Rect(location_x, location_y, btn_w, btn_h)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for box in input_boxes.values():
                box.handle_event(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if submit_rect.collidepoint(event.pos):
                    # For now, print the responses to console and continue
                    responses = [input_boxes[i].text if i in input_boxes else '' for i in range(len(questions))]
                    print("Respuestas:", responses)
                elif location_rect.collidepoint(event.pos):
                    # Import and run Superficie.main(screen) so it reuses the same pygame window.
                    module_path = os.path.join(os.path.dirname(__file__), 'Superficie.py')
                    if not os.path.exists(module_path):
                        print('No se encontró Superficie.py en:', module_path)
                    else:
                        try:
                            import importlib.util as _il
                            spec = _il.spec_from_file_location('ui.Superficie', module_path)
                            Superficie = _il.module_from_spec(spec)
                            # Execute module code (this will define functions/classes)
                            spec.loader.exec_module(Superficie)
                            # If Superficie defines a main function that accepts a screen, call it.
                            if hasattr(Superficie, 'main'):
                                try:
                                    # Call main with the current screen so the same window is reused.
                                    Superficie.main(screen)
                                except Exception as inner_e:
                                    print('Error ejecutando Superficie.main:', inner_e)
                            else:
                                print('Superficie.py no define una función main(screen)')
                        except Exception as e:
                            print('Error cargando Superficie.py:', e)
                elif back_rect.collidepoint(event.pos):
                    running = False

        # Draw mirrored background if available, otherwise fill white
        if bg_image:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill(WHITE)
        screen.blit(title_text, title_rect)

        # Draw questions and inputs (no form background as requested)
        for i, q in enumerate(questions):
            label = font_label.render(q, True, TEXT_COLOR)
            screen.blit(label, (label_x, start_y + i*gap + 4))
            if i in input_boxes:
                input_boxes[i].update()
                input_boxes[i].draw(screen)

        # Draw buttons
        pygame.draw.rect(screen, GRAY, submit_rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, location_rect, border_radius=8)
        pygame.draw.rect(screen, GRAY, back_rect, border_radius=8)
        # Use the title color for button labels to match the main screen
        txt_submit = font_label.render("Send", True, TITLE_COLOR)
        txt_location = font_label.render("Location Y", True, TITLE_COLOR)
        txt_back = font_label.render("Back", True, TITLE_COLOR)
        screen.blit(txt_submit, txt_submit.get_rect(center=submit_rect.center))
        screen.blit(txt_location, txt_location.get_rect(center=location_rect.center))
        screen.blit(txt_back, txt_back.get_rect(center=back_rect.center))

        pygame.display.flip()
        clock.tick(30)


if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
    datos_screen(screen)
