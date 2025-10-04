# main.py
import os
import sys
import pygame

# ---- Importa controles y pantallas desde otros módulos ----
# Estructura sugerida:
# ui/input_box.py  -> clase InputBox
# ui/button.py     -> clase Button
# ui/stepper.py    -> clase Stepper
from ui.input_box import InputBox
from ui.button import Button
from ui.stepper import Stepper


# ----------------- Configuración clave -----------------
def init_window(title: str = "App modular pygame", scale: float = 0.9):
    pygame.init()
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    info = pygame.display.Info()
    width = int(info.current_w * scale)
    height = int(info.current_h * scale)

    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption(title)
    return screen, width, height


def make_palette():
    return {
        "bg": (245, 245, 245),
        "text": (20, 20, 20),
        "box_inactive": (180, 180, 180),
        "box_active": (0, 120, 255),
        "button": (0, 180, 90),
        "button_text": (255, 255, 255),
        "frame": (120, 120, 120),
        "value_bg": (255, 255, 255),
    }


# ----------------- Aplicación -----------------
class App:
    def __init__(self):
        self.screen, self.W, self.H = init_window()
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 32)
        self.colors = make_palette()

        # ---- Estado global que otros módulos pueden leer/actualizar ----
        self.values = {}

        # ---- UI básica (importada de otros archivos) ----
        self.input_boxes = [
            InputBox(
                x=160,
                y=80 + i * 70,
                w=280,
                h=36,
                font=self.font,
                color_inactive=self.colors["box_inactive"],
                color_active=self.colors["box_active"],
                text_color=self.colors["text"],
            )
            for i in range(2)
        ]

        self.stepper = Stepper(
            x=160,
            y=80 + 2 * 70,
            label="Cantidad:",
            value=5,
            step=1,
            vmin=0,
            vmax=100,
            w=140,
            h=40,
            font=self.font,
            colors={
                "text": self.colors["text"],
                "frame": self.colors["frame"],
                "btn": (200, 200, 200),
                "btn_hover": (180, 180, 180),
                "value_bg": self.colors["value_bg"],
            },
        )

        self.save_button = Button(
            x=160,
            y=80 + 3 * 70,
            w=140,
            h=42,
            text="Guardar",
            font=self.font,
            bg=self.colors["button"],
            fg=self.colors["button_text"],
            on_click=self.save_values,
        )

    # --------- Lógica de acciones ---------
    def save_values(self):
        # Recolecta textos de InputBox y valor del Stepper
        self.values = {
            "campo_1": self.input_boxes[0].text,
            "campo_2": self.input_boxes[1].text,
            "cantidad": self.stepper.get_value(),
        }
        print("Valores guardados:", self.values)

    # --------- Bucle principal ---------
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                for box in self.input_boxes:
                    box.handle_event(event)

                self.stepper.handle_event(event)
                self.save_button.handle_event(event)

            self.draw()
            pygame.display.flip()
            self.clock.tick(60)

    # --------- Dibujo ---------
    def draw(self):
        self.screen.fill(self.colors["bg"])

        # Etiquetas
        labels = ["Valor 1:", "Valor 2:"]
        for i, label in enumerate(labels):
            surf = self.font.render(label, True, self.colors["text"])
            self.screen.blit(surf, (60, 86 + i * 70))

        # Controles
        for box in self.input_boxes:
            box.draw(self.screen)

        self.stepper.draw(self.screen)
        self.save_button.draw(self.screen)

        # Estado visible
        info = self.font.render(
            f"Cantidad: {self.stepper.get_value()}", True, self.colors["text"]
        )
        self.screen.blit(info, (60, 86 + 2 * 70 + 48))


# ----------------- Entrada -----------------
if __name__ == "__main__":
    App().run()
