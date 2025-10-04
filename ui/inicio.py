import pygame
import sys

# Configuración básica
WIDTH, HEIGHT = 800, 600
TITLE = "Condor ha aterrizado"

# Definición de botones
BUTTONS = [
    {"text": "Ir a Pantalla 1", "pos": (WIDTH // 2, HEIGHT // 2 - 40), "target": "pantalla1"},
    {"text": "Ir a Pantalla 2", "pos": (WIDTH // 2, HEIGHT // 2 + 40), "target": "pantalla2"},
]

def draw(screen, state):
    screen.fill((30, 30, 30))
    font = pygame.font.SysFont(None, 60)
    title_surf = font.render(TITLE, True, (255, 255, 255))
    title_rect = title_surf.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title_surf, title_rect)

    btn_font = pygame.font.SysFont(None, 40)
    for btn in BUTTONS:
        btn_surf = btn_font.render(btn["text"], True, (0, 0, 0))
        btn_rect = btn_surf.get_rect(center=btn["pos"])
        pygame.draw.rect(screen, (200, 200, 200), btn_rect.inflate(40, 20))
        screen.blit(btn_surf, btn_rect)

def handle_event(event, state):
    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
        mouse_pos = event.pos
        btn_font = pygame.font.SysFont(None, 40)
        for btn in BUTTONS:
            btn_surf = btn_font.render(btn["text"], True, (0, 0, 0))
            btn_rect = btn_surf.get_rect(center=btn["pos"])
            btn_rect = btn_rect.inflate(40, 20)
            if btn_rect.collidepoint(mouse_pos):
                state["next_screen"] = btn["target"]

# Ejemplo de uso independiente (opcional, puedes eliminar esto si usas un gestor de pantallas)
if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()
    state = {}

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            handle_event(event, state)
        draw(screen, state)
        pygame.display.flip()
        clock.tick(60)
