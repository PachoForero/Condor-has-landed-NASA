# main.py — base mínima para montar páginas desde ui/
# Uso:
# - Crea ui/inicio.py, ui/seleccion.py, ui/app.py, ui/creditos.py
#   Cada archivo puede definir: draw(screen, state) y handle_event(event, state)
# - Cambia de página con teclas 1,2,3,4

import os
import sys
import pygame

APP_NAME = "Pachos"
SCALE = 0.9  # 90% de la pantalla

def init_window(title=APP_NAME, scale=SCALE):
    pygame.init()
    os.environ["SDL_VIDEO_CENTERED"] = "1"
    info = pygame.display.Info()
    w, h = int(info.current_w * scale), int(info.current_h * scale)
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption(title)
    return screen, w, h

def _import_optional(mod_path):
    try:
        return __import__(mod_path, fromlist=["*"])
    except Exception:
        return None

def main():
    screen, W, H = init_window()
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 28)

    # Importa páginas (opcionales). Si no existen, se muestra placeholder.
    mods = [
        _import_optional("ui.inicio"),
        _import_optional("ui.seleccion"),
        _import_optional("ui.app"),
        _import_optional("ui.creditos"),
    ]
    page_names = ["Inicio", "Selección", "App", "Créditos"]
    current = 0

    # Estado compartido sencillo (pásalo a las páginas si lo necesitan)
    state = {
        "app_name": APP_NAME,
        "size": (W, H),
        "data": {},  # lugar para variables globales
    }

    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
            elif e.type == pygame.KEYDOWN:
                if e.key in (pygame.K_1, pygame.K_KP1): current = 0
                elif e.key in (pygame.K_2, pygame.K_KP2): current = 1
                elif e.key in (pygame.K_3, pygame.K_KP3): current = 2
                elif e.key in (pygame.K_4, pygame.K_KP4): current = 3

            # Delegar eventos a la página si define handle_event
            m = mods[current]
            if m and hasattr(m, "handle_event"):
                m.handle_event(e, state)

        # Dibujo básico
        screen.fill((245, 245, 245))

        # Encabezado mínimo
        pygame.draw.rect(screen, (255, 255, 255), (0, 0, W, 60))
        title = font.render(f"{APP_NAME} — {page_names[current]}", True, (20, 20, 20))
        screen.blit(title, (16, 18))
        pygame.draw.line(screen, (200, 200, 200), (0, 60), (W, 60), 1)

        # Área de contenido
        content_rect = pygame.Rect(0, 60, W, H - 60)
        pygame.draw.rect(screen, (250, 250, 250), content_rect)

        # Llamar a draw de la página si existe
        m = mods[current]   
        if m and hasattr(m, "draw"):
            m.draw(screen, state)
        else:
            # Placeholder si la página no existe o no define draw
            msg = font.render(
                f"Crea ui/{page_names[current].lower()}.py con draw(screen, state)",
                True, (120, 120, 120),
            )
            screen.blit(msg, (24, 84))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
