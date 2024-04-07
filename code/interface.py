# ============================================================================
# File    : interface.py
# Authors : Poulouc and Eraldor
# Date    : April 7th, 2024
# Role    : The game menu shared by the creative mode and the pacman
# ============================================================================

import pyxel
import json


def start_up():
    """Indicates the existing levels and their associated information"""
    with open('./boards/info.json') as file:
        data = json.load(file)
    return data


def research(sequence, element, start: int = 0):
    """Determines the first occurrence of an element in a sequence"""
    index = start
    while index < len(sequence):
        if sequence[index] == element:
            return index
        index += 1
    return 0


class Hitbox:  # by Eraldor
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def is_contained(self, x: int, y: int) -> bool:
        """Returns whether the given coordinates are inside the hitbox"""
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def relative_mouse_co(self) -> tuple[int, int]:
        """Returns the mouse coordinates relative to the hitbox"""
        return pyxel.mouse_x - self.x, pyxel.mouse_y - self.y


class Button:  # by Eraldor and Magistro
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

    def does_left_click(self):
        """Indicates if the button has been clicked on with the left button of the mouse"""
        if self.enabled and pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            self._pressed = self._hitbox.is_contained(pyxel.mouse_x, pyxel.mouse_y)
            return self._pressed
        if pyxel.btnr(pyxel.MOUSE_BUTTON_LEFT) and self._pressed:
            self._pressed = False
        return False

    def does_right_click(self):
        """Indicates if the button has been clicked on with the right button of the mouse"""
        if self.enabled and pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            self._pressed = self._hitbox.is_contained(pyxel.mouse_x, pyxel.mouse_y)
            return self._pressed
        if pyxel.btnr(pyxel.MOUSE_BUTTON_RIGHT) and self._pressed:
            self._pressed = False
        return False

    def toggle(self):
        self.enabled = not self.enabled


class Menu:
    def __init__(self, height, width, nb):
        self.menu_enabled = True
        self.name = "| Select Level |"
        self.height = height
        self.width = width
        self.selector = 2  # level selector in the menu
        self.menu_buttons = [Button(self.width * 20 // 100 - 22, self.height // 2 - 22, 45, 45, ""),
                             Button(self.width * 50 // 100 - 22, self.height // 2 - 22, 45, 45, ""),
                             Button(self.width * 80 // 100 - 22, self.height // 2 - 22, 45, 45, "")]
        self.nb_levels = nb  # amount of available levels
        pyxel.mouse(self.menu_enabled)

    def level_selector(self, n):
        """Allows for scrolling through the levels in the menu"""
        if 2 <= self.selector + n < self.nb_levels:
            self.selector += n

    def is_pressed(self):
        """Returns the value of the pressed button in the menu"""
        for button in self.menu_buttons:
            if button.does_left_click():
                return int(button.text)

    def toggle_menu(self):
        """Toggles the menu on and off"""
        self.menu_enabled = not self.menu_enabled
        pyxel.mouse(self.menu_enabled)
        for bouton in self.menu_buttons:
            bouton.toggle()

    def draw(self):
        pyxel.text(self.width // 2 - len(self.name) - 22, self.height * 30 // 100, self.name, 6)
        pyxel.text(self.menu_buttons[1].y + 372, self.height // 2, ">", 6)
        pyxel.text(self.menu_buttons[1].y - 350, self.height // 2, "<", 6)
        for i in range(0, 3, 1):
            if i < self.nb_levels:
                self.menu_buttons[i].text = str(self.selector - 2 + i)
            else:
                pyxel.text(self.width // 2 - 25, self.height * 60 // 100, "no more level", 6)
                self.menu_buttons[i].text = str("0")
            self.menu_buttons[i].draw()
