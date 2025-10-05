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
TITLE_COLOR = (34, 49, 73)  # #223149
GRAY = (200, 200, 200)
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
button_width, button_height = max(180, int(WIDTH * 0.15)), max(50, int(HEIGHT * 0.08))
button1_rect = pygame.Rect(WIDTH//2 - button_width - 20, HEIGHT//2, button_width, button_height)
button2_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2, button_width, button_height)
exit_button_rect = pygame.Rect((WIDTH - button_width) // 2, HEIGHT//2 + button_height + 20, button_width, button_height)


def draw_button(rect, text):
    pygame.draw.rect(screen, GRAY, rect, border_radius=10)
    txt = font_button.render(text, True, BLACK)
    txt_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, txt_rect)


def draw_exit_button(rect, text):
    pygame.draw.rect(screen, (200, 0, 0), rect, border_radius=10)
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

        screen.blit(title_text, title_rect)
        draw_button(button1_rect, "Simular habitat")
        draw_button(button2_rect, "Ver habitat")
        draw_exit_button(exit_button_rect, "Salir")

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
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        pygame.display.flip()


if __name__ == "__main__":
    main()