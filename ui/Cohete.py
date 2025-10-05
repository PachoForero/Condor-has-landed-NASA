import os
import pygame
import sys

# Use the same title color as in inicio.py
# TITLE_COLOR = (34, 49, 73)  # hex #223149
TITLE_COLOR = (34, 49, 73)


def cohete_screen(screen):
    """Fill the screen with the title color and draw ui/rocket.png positioned
    "3/4 a la izquierda". Interpretation: place the rocket so its left edge is
    at 1/4 of the screen width (i.e. visually 3/4 towards the left side).

    Args:
        screen: a pygame.Surface (the main display surface)
    """
    if screen is None:
        return

    base_dir = os.path.dirname(__file__)
    rocket_path = os.path.join(base_dir, 'rocket.png')
    # fallback to cwd if not found
    if not os.path.exists(rocket_path):
        alt = os.path.join(os.getcwd(), 'ui', 'rocket.png')
        if os.path.exists(alt):
            rocket_path = alt

    # Fill background with the title color
    screen.fill(TITLE_COLOR)

    if os.path.exists(rocket_path):
        try:
            img = pygame.image.load(rocket_path).convert_alpha()
            sw, sh = screen.get_size()

            # Scale rocket to a larger fraction of screen height (allow some upscaling)
            max_h = int(sh * 1.55)
            w, h = img.get_size()
            scale = (max_h / h) if h > 0 else 1.0
            # cap upscaling to 2x to avoid excessive blur
            scale = min(scale, 2.0)
            if abs(scale - 1.0) > 0.01:
                new_size = (max(1, int(w * scale)), max(1, int(h * scale)))
                img = pygame.transform.smoothscale(img, new_size)

            rw, rh = img.get_size()

            # Position: "3/4 a la izquierda" interpreted as left edge at 1/4 width
            x = int(sw * 0.15)
            # Shift image down by 1/4 of the screen height
            y = int((sh - rh) // 2 + (sh * 0.55))
            # Clamp to stay within the screen vertically
            if y + rh > sh - 10:
                y = max(10, sh - rh - 10)

            # If the rocket would overflow to the right, shift it left a bit
            if x + rw > sw - 10:
                x = max(10, sw - rw - 10)

            screen.blit(img, (x, y))
        except Exception as e:
            # If loading fails, draw a simple placeholder rectangle
            sw, sh = screen.get_size()
            rect_w, rect_h = int(sw * 0.2), int(sh * 0.3)
            px = int(sw * 0.25)
            py = (sh - rect_h) // 2
            pygame.draw.rect(screen, (200, 200, 200), (px, py, rect_w, rect_h), border_radius=8)
            # small label
            try:
                font = pygame.font.SysFont(None, 28)
                txt = font.render('rocket.png missing or failed to load', True, (20, 20, 20))
                screen.blit(txt, (px + 8, py + rect_h // 2 - txt.get_height() // 2))
            except Exception:
                pass
    else:
        # Image not found: draw placeholder
        sw, sh = screen.get_size()
        rect_w, rect_h = int(sw * 0.2), int(sh * 0.3)
        px = int(sw * 0.25)
        py = (sh - rect_h) // 2
        pygame.draw.rect(screen, (200, 200, 200), (px, py, rect_w, rect_h), border_radius=8)
        try:
            font = pygame.font.SysFont(None, 28)
            txt = font.render('rocket.png not found', True, (20, 20, 20))
            screen.blit(txt, (px + 8, py + rect_h // 2 - txt.get_height() // 2))
        except Exception:
            pass


def main():
    """Simple test runner for Cohete module."""
    pygame.init()
    info = pygame.display.Info()
    w, h = min(1280, info.current_w), min(800, info.current_h)
    screen = pygame.display.set_mode((w, h), pygame.RESIZABLE)
    pygame.display.set_caption('Cohete preview')
    clock = pygame.time.Clock()

    running = True
    while running:
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                running = False
            elif ev.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((ev.w, ev.h), pygame.RESIZABLE)

        cohete_screen(screen)
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
