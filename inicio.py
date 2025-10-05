import pygame
import sys
import os
from ui.Datos import datos_screen
from ui.Modulos import modulos_screen

# Try to import Pillow for animated GIF support
try:
    from PIL import Image
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False

# Configuración de la ventana
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)
TITLE_COLOR = (34, 49, 73)  # #223149 (reverted)
GRAY = (238, 229, 202)  # #EEE5CA
BLACK = (0, 0, 0)

pygame.init()
# Iniciar en pantalla completa usando la resolución actual del display
info = pygame.display.Info()
flags = 0
if hasattr(pygame, 'FULLSCREEN_DESKTOP'):
    flags = pygame.FULLSCREEN_DESKTOP
elif hasattr(pygame, 'SCALED'):
    flags = pygame.FULLSCREEN | pygame.SCALED
else:
    flags = pygame.FULLSCREEN

screen = pygame.display.set_mode((info.current_w, info.current_h), flags)
pygame.display.set_caption("CONDOR HAS LANDED")
WIDTH, HEIGHT = screen.get_size()

font_title = pygame.font.SysFont(None, 100)
font_button = pygame.font.SysFont(None, 36)

title_text = font_title.render("CONDOR HAS LANDED", True, TITLE_COLOR)
 # Position title at top center (small margin) without removing existing content
title_rect = title_text.get_rect(midtop=(WIDTH // 2, 20))

# Botones
# Calculate button sizes so the label text always fits (with padding)
labels = ["Simular habitat", "Ver habitat", "Salir"]
# Render texts once to measure
rendered_texts = [font_button.render(lbl, True, BLACK) for lbl in labels]
text_widths = [t.get_width() for t in rendered_texts]
text_heights = [t.get_height() for t in rendered_texts]
padding_x = max(20, int(WIDTH * 0.02))
padding_y = max(12, int(HEIGHT * 0.02))
button_width = max(180, max(text_widths) + padding_x * 2, int(WIDTH * 0.15))
button_height = max(50, max(text_heights) + padding_y * 2, int(HEIGHT * 0.07))

# Horizontal gap between left and right buttons
gap = max(40, int(WIDTH * 0.02))
button1_rect = pygame.Rect(WIDTH // 2 - button_width - gap // 2, HEIGHT // 2, button_width, button_height)
button2_rect = pygame.Rect(WIDTH // 2 + gap // 2, HEIGHT // 2, button_width, button_height)
# Make exit button slightly smaller and place it at bottom-right with margin
exit_w = int(button_width * 0.8)
exit_h = int(button_height * 0.8)
margin = max(20, int(WIDTH * 0.02))
exit_button_rect = pygame.Rect(WIDTH - exit_w - margin, HEIGHT - exit_h - margin, exit_w, exit_h)

# Credits button placed under the horizontal buttons, centered
credits_button_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT // 2 + button_height + 20, button_width, button_height)


def draw_button(rect, text):
    # Create a surface with per-pixel alpha for semi-transparent button
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    alpha_color = (*GRAY, 180)  # RGBA: last value is alpha (0-255)
    pygame.draw.rect(surf, alpha_color, surf.get_rect(), border_radius=10)
    screen.blit(surf, rect.topleft)
    # Use title color for button text to match the title (except Exit button)
    txt = font_button.render(text, True, TITLE_COLOR)
    txt_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, txt_rect)


def draw_exit_button(rect, text):
    # Semi-transparent exit button
    surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    exit_color = (223, 138, 93)  # #DF8A5D
    alpha_color = (*exit_color, 180)
    pygame.draw.rect(surf, alpha_color, surf.get_rect(), border_radius=10)
    screen.blit(surf, rect.topleft)
    txt = font_button.render(text, True, WHITE)
    txt_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, txt_rect)


def load_gif_frames_with_pillow(path):
    """Return list of (pygame.Surface, duration_ms) extracted from an animated GIF using Pillow."""
    frames = []
    if not PIL_AVAILABLE:
        return frames
    try:
        img = Image.open(path)
    except Exception:
        return frames

    try:
        while True:
            frame = img.convert('RGBA')
            size = frame.size
            raw = frame.tobytes()
            surf = pygame.image.fromstring(raw, size, 'RGBA')
            duration = img.info.get('duration', 100)
            frames.append((surf, int(duration)))
            img.seek(img.tell() + 1)
    except EOFError:
        pass
    except Exception:
        pass
    return frames


def credits_screen(screen):
    """Simple credits screen: shows some text and returns to main when any key or mouse button is pressed."""
    clock = pygame.time.Clock()
    small_font = pygame.font.SysFont(None, 30)
    title_font = pygame.font.SysFont(None, 40)
    lines = ["Credits", "Developed by:","Juan David Chica Garcia","Francisco Andres Forero Daza","Daniel Sneyder Ramirez Torres","Daniela Alejandra Castillo Avellaneda","Maria Jose Barrios Riaño","Assets: NASA / internal", "Press any key or click to return"]
    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN or (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1):
                return

        # Draw background
        screen.fill(WHITE)

        y = HEIGHT // 4
        for i, line in enumerate(lines):
            if i == 0:
                txt = title_font.render(line, True, TITLE_COLOR)
            else:
                txt = small_font.render(line, True, BLACK)
            rect = txt.get_rect(center=(WIDTH // 2, y))
            screen.blit(txt, rect)
            y += 50

        pygame.display.flip()


def main():
    # Only use ini.gif. Search the script directory first, then cwd.
    base_dir = os.path.dirname(__file__)
    gif_path = os.path.join(base_dir, 'ini.gif')
    if not os.path.exists(gif_path):
        alt = os.path.join(os.getcwd(), 'ini.gif')
        if os.path.exists(alt):
            gif_path = alt

    frames = []
    bg_static = None
    use_gif = False

    # Preload logo (logito.png) from script dir or cwd
    logo_surf = None
    logo_path = os.path.join(base_dir, 'logito.png')
    if not os.path.exists(logo_path):
        alt_logo = os.path.join(os.getcwd(), 'logito.png')
        if os.path.exists(alt_logo):
            logo_path = alt_logo

    if os.path.exists(logo_path):
        try:
            tmp_logo = pygame.image.load(logo_path).convert_alpha()
            # Scale logo if it's larger than 10% of screen width or height
            max_logo_w = int(WIDTH * 0.12)
            max_logo_h = int(HEIGHT * 0.12)
            lw, lh = tmp_logo.get_size()
            scale = min(1.0, max_logo_w / lw if lw > max_logo_w else 1.0, max_logo_h / lh if lh > max_logo_h else 1.0)
            if scale < 1.0:
                new_size = (max(1, int(lw * scale)), max(1, int(lh * scale)))
                logo_surf = pygame.transform.smoothscale(tmp_logo, new_size)
            else:
                logo_surf = tmp_logo
            print(f"Loaded logo from: {logo_path}")
        except Exception as e:
            print(f"Failed to load logito.png: {e}")
    else:
        # No logo found; logo_surf remains None
        pass

    if os.path.exists(gif_path):
        print(f"Found ini.gif at: {gif_path}")
        if PIL_AVAILABLE:
            frames = load_gif_frames_with_pillow(gif_path)
            if frames:
                use_gif = True
                print(f"Loaded {len(frames)} frames from GIF")
            else:
                # Failed to extract frames with Pillow; try pygame static load
                try:
                    tmp = pygame.image.load(gif_path)
                    bg_static = pygame.transform.scale(tmp, (WIDTH, HEIGHT))
                    print("Loaded static GIF via pygame")
                except Exception as e:
                    print(f"Failed to load ini.gif: {e}")
        else:
            # Pillow not installed: load the GIF as a static image via pygame
            try:
                tmp = pygame.image.load(gif_path)
                bg_static = pygame.transform.scale(tmp, (WIDTH, HEIGHT))
                print("Pillow not installed — using static GIF via pygame")
            except Exception as e:
                print(f"Failed to load ini.gif with pygame: {e}")
    else:
        print("ini.gif not found in script dir or cwd. Place ini.gif next to inicio.py")

    clock = pygame.time.Clock()
    bg_index = 0
    bg_acc = 0

    while True:
        dt = clock.tick(60)

        # Update background
        if use_gif and frames:
            surf, dur = frames[bg_index]
            bg_acc += dt
            if bg_acc >= dur:
                bg_acc = 0
                bg_index = (bg_index + 1) % len(frames)
            try:
                bg_to_draw = pygame.transform.scale(surf, (WIDTH, HEIGHT))
            except Exception:
                bg_to_draw = None
        else:
            bg_to_draw = bg_static

        if bg_to_draw:
            screen.blit(bg_to_draw, (0, 0))
        else:
            screen.fill(WHITE)

        # Draw logo in bottom-left if available
        if logo_surf:
            logo_margin = max(10, int(WIDTH * 0.01))
            logo_pos = (logo_margin, HEIGHT - logo_surf.get_height() - logo_margin)
            screen.blit(logo_surf, logo_pos)

        screen.blit(title_text, title_rect)
        draw_button(button1_rect, "Habitat simulation")
        draw_button(button2_rect, "See habitat")
        draw_button(credits_button_rect, "Credits")
        draw_exit_button(exit_button_rect, "Exit")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button1_rect.collidepoint(event.pos):
                    datos_screen(screen)
                elif button2_rect.collidepoint(event.pos):
                    modulos_screen(screen)
                elif exit_button_rect.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()
                elif credits_button_rect.collidepoint(event.pos):
                    credits_screen(screen)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()


if __name__ == "__main__":
    main()