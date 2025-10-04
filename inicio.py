import pygame
import sys
import subprocess
from ui.Datos import datos_screen

# Configuración de la ventana
WIDTH, HEIGHT = 600, 400
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Condor has landed - NASA")
font_title = pygame.font.SysFont(None, 48)
font_button = pygame.font.SysFont(None, 36)

# Título
title_text = font_title.render("Condor has landed - NASA", True, BLUE)
title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))

# Botones
button_width, button_height = 180, 50
button1_rect = pygame.Rect(WIDTH//2 - button_width - 20, HEIGHT//2, button_width, button_height)
button2_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2, button_width, button_height)

def draw_button(rect, text):
    pygame.draw.rect(screen, GRAY, rect, border_radius=10)
    txt = font_button.render(text, True, BLACK)
    txt_rect = txt.get_rect(center=rect.center)
    screen.blit(txt, txt_rect)

def main():
    while True:
        screen.fill(WHITE)
        screen.blit(title_text, title_rect)
        draw_button(button1_rect, "Abrir archivo 1")
        draw_button(button2_rect, "Abrir archivo 2")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button1_rect.collidepoint(event.pos):
                    # Open the Datos form in the same window
                    datos_screen(screen)
                elif button2_rect.collidepoint(event.pos):
                    subprocess.Popen(['python', 'archivo2.py'])

        pygame.display.flip()

if __name__ == "__main__":
    main()