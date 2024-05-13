# ============================================================================
# File    : interfaces.py
# Autor   : Poulouc and Eraldor
# Date    : 04/2024
# Role    : all the button menu and music shared by the creative and the pacman
# ============================================================================
import pyxel
import json


def start_up():
    """Indique combien de niveau existe"""
    with open('./levels_files/info_boards.json') as file:
        donnee = json.load(file)
    return donnee


def research(liste, motifs, depart=0):
    """Determine la première occurence de quelque chose dans une liste ou un str"""
    ind_txt = depart
    while ind_txt < len(liste):
        if liste[ind_txt] == motifs:
            return ind_txt
        ind_txt += 1
    return 0


class Hitbox: # by Eraldor
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def __contains__(self, item: tuple[int, int]) -> bool:
        return self.is_contained(*item)

    def is_contained(self, x: int, y: int) -> bool:
        """Returns whether the given coordinates are inside the hitbox."""
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def mouse_co_inside(self) -> tuple[int, int]:
        """Returns the mouse coordinates relative to the hitbox."""
        return pyxel.mouse_x - self.x, pyxel.mouse_y - self.y


class Button: # by Eraldor and Magistro
    def __init__(self, x: int, y: int, width: int, height: int, text: str):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.enabled = True
        self._pressed = False
        self._hitbox = Hitbox(self.x, self.y, self.width, self.height)

    def draw(self):
        if self.enabled:
            pyxel.rect(self.x, self.y, self.width, self.height,
                       7 if self._pressed else 10)
            pyxel.text(self.x + self.width // 2 - 2 * len(self.text) + 1,
                       self.y + self.height // 2 - 3,
                       self.text, 0)

    def is_pressed_LEFT(self):
        if self.enabled and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._pressed = self._hitbox.is_contained(pyxel.mouse_x, pyxel.mouse_y)
            return self._pressed
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self._pressed:
            self._pressed = False
        return False

    def is_pressed_RIGHT(self):
        if self.enabled and pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self._pressed = self._hitbox.is_contained(pyxel.mouse_x, pyxel.mouse_y)
            return self._pressed
        if pyxel.btnr(pyxel.MOUSE_BUTTON_RIGHT) and self._pressed:
            self._pressed = False
        return False

    def toggle(self):
        self.enabled = not self.enabled


class Menu:
    def __init__(self, high, larg, nb):
        self.Menu_enabled = True
        self.name = "| Select Level |"
        self.haut = high
        self.large = larg
        self.selecteur = 2  # sélecteur de niveau dans le menu
        self.bouton_menu = [Button(self.large * 20 // 100 - 22, self.haut // 2 - 22, 45, 45, ""),
                            Button(self.large * 50 // 100 - 22, self.haut // 2 - 22, 45, 45, ""),
                            Button(self.large * 80 // 100 - 22, self.haut // 2 - 22, 45, 45, "")]  # bouton du menu
        self.nb_niveau = nb  # indique le nb de niveau dispo
        pyxel.mouse(self.Menu_enabled)

    def level_selector(self, n):
        """Permet de faire défiler les niveaux du menu"""
        if 2 <= self.selecteur + n < self.nb_niveau:
            self.selecteur += n

    def is_pressed(self):
        """Renvoi la valeur du bouton presser pour définir quel niveau doit être initialisé"""
        for bouton in self.bouton_menu:
            if bouton.is_pressed_LEFT():
                return int(bouton.text)

    def toggle_menu(self):
        """Désactive/Active l'affichage du menu et ses boutons"""
        self.Menu_enabled = not self.Menu_enabled
        pyxel.mouse(self.Menu_enabled)
        for bouton in self.bouton_menu:
            bouton.toggle()

    def draw(self):
        pyxel.text(self.large // 2 - len(self.name) - 22, self.haut * 30 // 100, self.name, 6)
        pyxel.text(self.bouton_menu[1].y + 372, self.haut // 2, ">", 6)
        pyxel.text(self.bouton_menu[1].y - 350, self.haut // 2, "<", 6)
        for i in range(0, 3, 1):
            if i < self.nb_niveau:
                self.bouton_menu[i].text = str(self.selecteur - 2 + i)
            else:
                pyxel.text(self.large // 2 - 25, self.haut * 60 // 100, "no more level", 6)
                self.bouton_menu[i].text = str("0")
            self.bouton_menu[i].draw()


class Soundtrack:
    def __init__(self):
        pyxel.sound(1).set(
            "b2b2 b3b3 f#3f#3 e-3e-3"
            "b2f#3 f#3f#3 e-3e-3 e-3r"
            "c3c3 c4c4 g3g3 e3e3"
            "c4g3 g3g3 e3e3 e3r"
            "b2b2 b3b3 f#3f#3 e-3e-3"
            "b2f#3 f#3f#3 e-3e-3 e-3r"
            "e-3e3 f3r f3f#3 g3r"
            "g3a-3 a3a3 b3b3b3r",
            "s", "6", "n", 7
        )
        pyxel.sound(2).set(
            "b0b0b0b0 b0b0b1b1 b0b0b0b0 b0b0b1b1"
            "c1c1c1c1 c1c1c2c2 c1c1c1c1 c1c1c2c2"
            "b0b0b0b0 b0b0b1b1 b0b0b0b0 b0b0b1b1"
            "f#1f#1f#1f#1 a-1a-1a-1a-1 b-1b-1b-1b-1 b1b1b1b1",
            "t", "4", "n", 7
        )
        pyxel.sound(3).set(
            "e2e2c2g1 g1g1c2e2 d2d2d2g2 g2g2rr" "c2c2a1e1 e1e1a1c2 b1b1b1e2 e2e2rr",
            "p",
            "6",
            "vffn fnff vffs vfnn",
            25,
        )
        pyxel.sound(4).set(
            "c1g1c1g1 c1g1c1g1 b0g1b0g1 b0g1b0g1" "a0e1a0e1 a0e1a0e1 g0d1g0d1 g0d1g0d1",
            "t",
            "7",
            "n",
            25,
        )
        pyxel.sound(5).set(
            "f0c1f0c1 g0d1g0d1 c1g1c1g1 a0e1a0e1" "f0c1f0c1 f0c1f0c1 g0d1g0d1 g0d1g0d1",
            "t",
            "7",
            "n",
            25,
        )
        pyxel.sound(6).set(
            "g0d1",
            "s",
            "7",
            "f",
            20
        )
