import pygame
import sys
import subprocess
import os
from ui.Datos import datos_screen
from ui.Modulos import modulos_screen

# Configuración de la ventana
DEFAULT_WIDTH, DEFAULT_HEIGHT = 1920, 1080
WHITE = (255, 255, 255)
BLUE = (30, 144, 255)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)

pygame.init()
# Iniciar en pantalla completa usando la resolución actual del display
info = pygame.display.Info()
# Try to open fullscreen without changing the display resolution.
# Prefer FULLSCREEN_DESKTOP (if available) or FULLSCREEN|SCALED, else fallback to FULLSCREEN.
flags = 0
if hasattr(pygame, 'FULLSCREEN_DESKTOP'):
    flags = pygame.FULLSCREEN_DESKTOP
elif hasattr(pygame, 'SCALED'):
    flags = pygame.FULLSCREEN | pygame.SCALED
else:
    flags = pygame.FULLSCREEN

screen = pygame.display.set_mode((info.current_w, info.current_h), flags)
pygame.display.set_caption("Condor has landed - NASA")
# Actualizar dimensiones reales
WIDTH, HEIGHT = screen.get_size()

font_title = pygame.font.SysFont(None, 48)
font_button = pygame.font.SysFont(None, 36)

# Título (calcular después de conocer WIDTH/HEIGHT)
title_text = font_title.render("Condor has landed - NASA", True, BLUE)
title_rect = title_text.get_rect(center=(WIDTH // 2, HEIGHT // 3))

# Botones (tamaño relativo para pantallas grandes)
button_width, button_height = max(180, int(WIDTH * 0.15)), max(50, int(HEIGHT * 0.08))
button1_rect = pygame.Rect(WIDTH//2 - button_width - 20, HEIGHT//2, button_width, button_height)
button2_rect = pygame.Rect(WIDTH//2 + 20, HEIGHT//2, button_width, button_height)
# Botón de salir debajo de los botones horizontales
exit_button_width, exit_button_height = button_width, button_height
exit_button_rect = pygame.Rect((WIDTH - exit_button_width) // 2, HEIGHT//2 + button_height + 20, exit_button_width, exit_button_height)

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

def main():
    while True:
        screen.fill(WHITE)
        screen.blit(title_text, title_rect)
        draw_button(button1_rect, "Abrir archivo 1")
        draw_button(button2_rect, "Abrir archivo 2")
        draw_exit_button(exit_button_rect, "Salir")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if button1_rect.collidepoint(event.pos):
                    # Open the Datos form in the same window
                    datos_screen(screen)
                elif button2_rect.collidepoint(event.pos):
                    # Abrir la pantalla de Módulos en la misma ventana
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