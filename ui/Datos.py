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
        # By default allow any characters; can be set externally to restrict to digits only
        self.digits_only = False

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
                # Basic character input (ignore non-printables). If digits_only flag is set,
                # accept only numeric characters (0-9).
                if len(event.unicode) > 0:
                    ch = event.unicode
                    if self.digits_only:
                        if ch.isdigit():
                            self.text += ch
                        else:
                            # ignore non-digit input
                            pass
                    else:
                        self.text += ch
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
    title_text = font_title.render("Data - Answer the questions", True, TITLE_COLOR)
    title_rect = title_text.get_rect(center=(sw//2, int(sh*0.08)))

    questions = [
        "1) Number of people",
        "2) Mission location:",
        "3) Duration (months):",
        "4) Number of modules:",
    ]

    # Form dimensions (centered)
    form_w = min(600, int(sw * 0.6))
    form_h = int(sh * 0.6)
    form_x = (sw - form_w) // 2
    form_y = int(sh * 0.15)

    # Create input boxes for all questions except the second (index 1)
    input_boxes = {}
    # Move inputs slightly further down to reduce overlap with labels
    start_y = form_y + 80
    gap = max(70, int(form_h * 0.12))
    input_w = int(form_w * 0.65)
    label_x = form_x + int(form_w * 0.05)
    input_x = form_x + int(form_w * 0.3)
    for i in range(len(questions)):
        if i == 1:
            # Skip creating an input for the second question (location)
            continue
        # Shift first (i==0), third (i==2), and fourth (i==3) input boxes slightly to the right
        x_offset = 40 if i in (0, 2, 3) else 0
        rect = (input_x + x_offset, start_y + i*gap, input_w, 32)
        input_boxes[i] = InputBox(rect, font_input)
        # Make numeric-only for questions that expect numbers (indices 0,2,3)
        if i in (0, 2, 3):
            input_boxes[i].digits_only = True

    # Buttons: Enviar y Volver permanecen centrados debajo del formulario.
    # El botón 'Location Y' se reubica debajo del primer cuadro de texto
    # y se alinea horizontalmente con la etiqueta de la segunda pregunta (label_x).
    btn_w, btn_h = 120, 40
    spacing = 12
    total_w = btn_w * 2 + spacing  # Solo Enviar y Volver en la línea inferior
    start_x = sw//2 - total_w//2
    submit_rect = pygame.Rect(start_x, form_y + form_h - 50, btn_w, btn_h)
    back_rect = pygame.Rect(start_x + (btn_w + spacing), form_y + form_h - 50, btn_w, btn_h)

    # Place Location button to the right of the second question label
    # and vertically aligned with that label (index 1).
    # Calculamos la posición x usando el ancho renderizado de la etiqueta
    # para que quede justo a su derecha con un pequeño margen.
    label_for_location = font_label.render(questions[1], True, TEXT_COLOR)
    label_width = label_for_location.get_width()
    small_margin = 12
    location_x = label_x + label_width + small_margin
    # Vertically align with the second question label
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
                    print("Responses:", responses)
                elif location_rect.collidepoint(event.pos):
                    # Import and run Superficie.main(screen) so it reuses the same pygame window.
                    module_path = os.path.join(os.path.dirname(__file__), 'Superficie.py')
                    if not os.path.exists(module_path):
                        print('Superficie.py not found at:', module_path)
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
                                    prev_screen = screen
                                    try:
                                        prev_size = prev_screen.get_size()
                                    except Exception:
                                        prev_size = (DEFAULT_WIDTH, DEFAULT_HEIGHT)

                                    # Create fullscreen with SCALED if available.
                                    flags = pygame.FULLSCREEN
                                    if hasattr(pygame, 'SCALED'):
                                        flags |= pygame.SCALED
                                    info = pygame.display.Info()
                                    real_w, real_h = info.current_w, info.current_h
                                    factor = 1.5
                                    factor = min(factor, 2.0)
                                    logical_w = int(real_w * factor)
                                    logical_h = int(real_h * factor)
                                    try:
                                        fs_screen = pygame.display.set_mode((logical_w, logical_h), flags)
                                    except Exception:
                                        fs_screen = pygame.display.set_mode((real_w, real_h), flags)

                                    # Pass the fullscreen screen to Superficie
                                    Superficie.main(fs_screen)

                                    # After returning, ensure pygame/display are initialized
                                    if not pygame.get_init() or pygame.display.get_surface() is None:
                                        try:
                                            pygame.init()
                                        except Exception as e:
                                            print('Could not reinitialize pygame:', e)

                                    # Attempt to restore the previous windowed screen size
                                    try:
                                        pygame.display.set_mode(prev_size)
                                        screen = pygame.display.get_surface()
                                    except Exception:
                                        try:
                                            pygame.display.set_mode((DEFAULT_WIDTH, DEFAULT_HEIGHT))
                                            screen = pygame.display.get_surface()
                                        except Exception as e:
                                            print('Could not restore previous window:', e)

                                    print('Restored previous window after exiting Superficie')
                                except Exception as inner_e:
                                    print('Error running Superficie.main:', inner_e)
                            else:
                                print('Superficie.py does not define a main(screen) function')
                        except Exception as e:
                            print('Error loading Superficie.py:', e)
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
        txt_submit = font_label.render("Submit", True, TITLE_COLOR)
        txt_location = font_label.render("Location", True, TITLE_COLOR)
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
