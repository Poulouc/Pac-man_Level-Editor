# ============================================================================
# File    : Pacman_v1_7.py
# Author  : Poulouc
# Date    : 04/2024
# Role    : Creating board for the Pacman
# ============================================================================
import pyxel
import ButtonMenu
import json


class Creative:
    def __init__(self):
        self.selection = [21, 21, 0]  # selector for new board size and item
        self.buttons = []  # button array for the board
        self.object = {"pacman": [16, 0], "ghost": [48, 0], "-": [0, 80], "|": [16, 80], ">": [0, 96], "<": [16, 96],
                      "+": [32, 96], ".": [48, 96], "pacgomme": "1", "super pacgomme": "!", "0": "nothing", "portal": "*", "=": "="}
        self.object_list = list(self.object.keys())
        self.show = False
        self.records = ButtonMenu.start_up()
        self.level_selected = -2  # keeps track of the loaded level
        self.offset = 0  # used to center the board
        pyxel.init(900, 900, title="Creativ mod", fps=60, display_scale=1)
        self.other_buttons = [ButtonMenu.Button(pyxel.height // 2 - 22, pyxel.width * 65 // 100, 45, 45, 'New'), ButtonMenu.Button(pyxel.height - 25, pyxel.width - 25, 20, 20, "Menu"), ButtonMenu.Button(pyxel.height - 25, pyxel.width - 55, 20, 20, "+|+")]
        self.menu = ButtonMenu.Menu(pyxel.height, pyxel.width, len(self.records))
        self.other_buttons[1].toggle()
        self.menu.name = "| Select Level to Edit |"
        pyxel.camera(0, 0)
        pyxel.load("PYXEL_RESOURCE_FILE.zip")
        pyxel.run(self.update, self.draw)

    def initialize(self, n):
        self.level_selected = n
        self.buttons = []  # clear buttons in case of changing levels during runtime
        if n == -1:
            self.offset = pyxel.width // 2 - self.selection[1] * 19 // 2 - 25
            for i in range(self.selection[0]):
                self.buttons.append([])
                for j in range(self.selection[1]):
                    self.buttons[i].append(
                        ButtonMenu.Button(16 * j + 30 + j * 3 + self.offset, 16 * i + 30 + i * 3 + self.offset, 16, 16, ""))
        else:
            with open(self.records[self.level_selected]['file-name']) as f:
                board = f.read().splitlines()
            level = []
            for val in board:
                level.append(list(val))
            self.offset = pyxel.width // 2 - (len(level[0]) * 19) // 2 - 30
            for i in range(len(level)):  # fill the button board
                self.buttons.append([])
                for j in range(len(level[i])):
                    if [i, j] == self.records[self.level_selected]["pacman-spawn"]:
                        self.buttons[i].append(ButtonMenu.Button(16 * j + 30 + j * 3 + self.offset, 16 * i + 30 + i * 3 + self.offset, 16, 16, "pacman"))
                    elif [i, j] == self.records[self.level_selected]["ghost-spawn"]:
                        self.buttons[i].append(ButtonMenu.Button(16 * j + 30 + j * 3 + self.offset, 16 * i + 30 + i * 3 + self.offset, 16, 16, "ghost"))
                    elif self.records[n]["tp"] != [] and ([i, j] == self.records[n]["tp"][0] or [i, j] == self.records[n]["tp"][1]):
                        self.buttons[i].append(ButtonMenu.Button(16 * j + 30 + j * 3 + self.offset, 16 * i + 30 + i * 3 + self.offset, 16, 16, "portal"))
                    elif level[i][j] == "1":
                        self.buttons[i].append(ButtonMenu.Button(16 * j + 30 + j * 3 + self.offset, 16 * i + 30 + i * 3 + self.offset, 16, 16, "pacgomme"))
                    elif level[i][j] == "!":
                        self.buttons[i].append(ButtonMenu.Button(16 * j + 30 + j * 3 + self.offset, 16 * i + 30 + i * 3 + self.offset, 16, 16, "super pacgomme"))
                    else:
                        self.buttons[i].append(ButtonMenu.Button(16 * j + 30 + j * 3 + self.offset, 16 * i + 30 + i * 3 + self.offset, 16, 16, str(level[i][j])))
        ButtonMenu.Soundtrack()  # check if the board was correctly loaded
        pyxel.play(0, [0, 1], loop=False)

    def selector(self, i):
        if 0 <= self.selection[2] + i < len(self.object_list):
            self.selection[2] += i

    def set_size(self, i, o):
        if 4 <= self.selection[o] + i <= 42:
            self.selection[o] += i

    def create_level(self):
        if self.plateau_bien_construit() and self.level_selected != -2:
            tp = []
            board_txt = ""
            for i in range(len(self.buttons)):
                for j in range(len(self.buttons[i])):
                    if self.buttons[i][j].text in ["-", "|", "<", ">", "+", ".", "1", "0", "!", "="]:
                        board_txt += self.buttons[i][j].text
                    elif self.buttons[i][j].text == "pacman":
                        board_txt += "0"
                        pacman = [i, j]
                    elif self.buttons[i][j].text == "ghost":
                        board_txt += "0"
                        ghost = [i, j]
                    elif self.buttons[i][j].text == "portal":
                        board_txt += "0"
                        tp.append([i, j])
                    else:
                        board_txt += self.object[self.buttons[i][j].text]
                board_txt += "\n"
                print(board_txt)
            if self.level_selected == -1:
                with open("info_boards.json", "w") as info_niveau:
                    json.dump(self.records + [{"file-name": "plateau_" + str(len(self.records)) + ".txt", "pacman-spawn": pacman,
                                           "ghost-spawn": ghost, "tp": tp, "score": 0}], info_niveau, indent=2)
                with open("plateau_" + str(len(self.records)) + ".txt", "w") as f:
                    f.write(board_txt)
            else:
                self.records[self.level_selected] = {"file-name": "plateau_" + str(self.level_selected) + ".txt",
                                                   "pacman-spawn": pacman,
                                                   "ghost-spawn": ghost, "tp": tp, "score": 0}
                with open("info_boards.json", "w") as info_niveau:
                    json.dump(self.records, info_niveau, indent=2)
                with open("plateau_" + str(self.level_selected) + ".txt", "w") as f:
                    f.write(board_txt)

    def plateau_bien_construit(self):
        """Verifie que le plateau est bien construit"""
        pacman = 0
        ghost = 0
        tp = 0
        for i in range(len(self.buttons)):
            for j in range(len(self.buttons[i])):
                if self.buttons[i][j].text == "pacman":
                    pacman += 1
                elif self.buttons[i][j].text == "ghost":
                    ghost += 1
                elif self.buttons[i][j].text == "portal":
                    tp += 1
                elif self.buttons[i][j].text == "":
                    return False
        if pacman == 1 and ghost == 1 and tp in [0, 2]:
            return True
        return False

    def crea_toggle(self, n):
        self.initialize(n)
        self.menu.toggle_menu()
        self.other_buttons[0].toggle()
        self.other_buttons[1].toggle()

    def miroir(self):
        """Reconstruit le miroir du plateau"""
        inverse = [".", "<", "+", ">"]
        for g in range(len(self.buttons)):
            i, j = 0, len(self.buttons[0]) - 1
            while i < j:  # compliqué de faire le mirroir du centre
                if self.buttons[g][i].text != "" and self.buttons[g][j].text == "":
                    if self.buttons[g][i].text in inverse:
                        self.buttons[g][j].text = inverse[ButtonMenu.research(inverse, self.buttons[g][i].text) - 2]
                    else:
                        self.buttons[g][j].text = self.buttons[g][i].text
                elif self.buttons[g][j].text != "" and self.buttons[g][i].text == "":
                    if self.buttons[g][j].text in inverse:
                        self.buttons[g][i].text = inverse[ButtonMenu.research(inverse, self.buttons[g][j].text) - 2]
                    else:
                        self.buttons[g][i].text = self.buttons[g][j].text
                i += 1
                j -= 1

    def update(self):
        pyxel.cls(0)
        if pyxel.btnp(pyxel.KEY_H):  # show help page
            self.show = not self.show
        elif self.menu.Menu_enabled:
            if pyxel.btn(pyxel.KEY_Q):
                self.menu.level_selector(-1)
            elif pyxel.btn(pyxel.KEY_D):
                self.menu.level_selector(1)
            elif pyxel.btnp(pyxel.KEY_UP):
                self.set_size(1, 0)
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.set_size(-1, 0)
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.set_size(1, 1)
            elif pyxel.btnp(pyxel.KEY_LEFT):
                self.set_size(-1, 1)
            self.menu.level_selector(pyxel.mouse_wheel)
        else:
            for i in range(len(self.buttons)):
                for j in range(len(self.buttons[i])):
                    if self.buttons[i][j].is_pressed_LEFT() and self.buttons[i][j].text == "":
                        self.buttons[i][j].text = self.object_list[self.selection[2]]
                    elif self.buttons[i][j].is_pressed_LEFT() and self.buttons[i][j].text != "":
                        self.buttons[i][j].text = ""
                    elif self.buttons[i][j].is_pressed_RIGHT() and self.buttons[i][j].text != "":
                        self.selection[2] = ButtonMenu.research(self.object_list, self.buttons[i][j].text, 0)
            if self.other_buttons[1].is_pressed_LEFT():
                self.crea_toggle(-2)
            elif self.other_buttons[2].is_pressed_LEFT():
                self.miroir()
            elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_Q):
                self.selector(-1)
            elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
                self.selector(1)
            elif self.plateau_bien_construit() and pyxel.btnp(pyxel.KEY_R):
                self.create_level()
            self.selector(pyxel.mouse_wheel)

    def draw(self):
        pyxel.blt(pyxel.width // 2 - 60, 5, 0, 0, 152, 111, 16)
        pyxel.text(10, pyxel.height - 15, "Press H to see the help page", 10)
        if self.show:
            pyxel.text(pyxel.width // 2 - 100, pyxel.height // 2 - 150,
                       "| Menu |" + 4 * "\n"
                       "mouse wheel, key Q or key D to scroll" + 2 * "\n"
                       "UP or Down to select the height of the new level" + 2 * "\n"
                       "Right or Left to select the width of the new level" + 4 * "\n"
                       "| Create |" + 4 * "\n"
                       "Press Q, mousse wheel or left to scroll to the left in the items selector" + 2 * "\n"
                       "Press D, mousse wheel or right to scroll to the right in the items selector" + 2 * "\n"
                       "Click left to push the item selected" + 2 * "\n"
                       "Choose a little square to place the item selected" + 2 * "\n"
                       "Click right to copy the item on the board" + 4 * "\n"
                       "| Rules |" + 4 * "\n"
                       "You can't place more than 1 pacman" + 2 * "\n"
                       "You can't place more than 1 ghost" + 2 * "\n"
                       "You can't place more than 2 portals on the board" + 2 * "\n"
                       "You can't place 2 portal on the same line or column" + 2 * "\n"
                       "All the squares must be filled" + 2 * "\n"
                       "You must place at least 1 portal" + 2 * "\n"
                       "The corridors can't be wider than 1 square" + 4 * "\n"
                       "Esc to exit the game" + 2 * "\n"
                       "R to save the level", 6)
        elif self.menu.Menu_enabled:
            self.other_buttons[0].draw()
            pyxel.text(self.other_buttons[0].x + 20, self.other_buttons[0].y + 60, str(self.selection[1]), 6)
            pyxel.text(self.other_buttons[0].x - 20, self.other_buttons[0].y + 23, str(self.selection[0]), 6)
            self.menu.draw()
            val = self.menu.is_pressed()
            if val is not None and val < len(self.records):
                self.crea_toggle(val)
            elif self.other_buttons[0].is_pressed_LEFT():
                self.crea_toggle(-1)
        else:
            pyxel.mouse(True)
            self.other_buttons[1].draw()
            self.other_buttons[2].draw()
            for i in range(len(self.buttons)):  # affiche ce qui est enregistré dans le bouton
                for j in range(len(self.buttons[i])):
                    if self.buttons[i][j].text == "":
                        self.buttons[i][j].draw()
                    elif self.buttons[i][j].text == "portal":
                        pyxel.rect(self.buttons[i][j].x, self.buttons[i][j].y, 16, 16, 0)
                        pyxel.circ(self.buttons[i][j].x + 8, self.buttons[i][j].y + 8, 2, 10)
                        pyxel.circb(self.buttons[i][j].x + 8, self.buttons[i][j].y + 8, 5, pyxel.frame_count % 15)
                    elif self.buttons[i][j].text == "pacgomme":
                        pyxel.rect(self.buttons[i][j].x, self.buttons[i][j].y, 16, 16, 0)
                        pyxel.circ(self.buttons[i][j].x + 8, self.buttons[i][j].y + 8, 2, 10)
                    elif self.buttons[i][j].text == "super pacgomme":
                        pyxel.rect(self.buttons[i][j].x, self.buttons[i][j].y, 16, 16, 0)
                        pyxel.circb(self.buttons[i][j].x + 8, self.buttons[i][j].y + 8, 5, 6)
                    elif self.buttons[i][j].text == "0":
                        pyxel.rect(self.buttons[i][j].x, self.buttons[i][j].y, 16, 16, 0)
                    elif self.buttons[i][j].text == "=":
                        pyxel.text(self.buttons[i][j].x + 6, self.buttons[i][j].y + 6, "+", 6)
                    else:
                        pyxel.blt(self.buttons[i][j].x, self.buttons[i][j].y, 0, self.object[self.buttons[i][j].text][0], self.object[self.buttons[i][j].text][1],
                                  16, 16)
            if self.object_list[self.selection[2]] == "pacgomme":
                pyxel.circ(20 + 8, 10 + 8, 2, 10)
            elif self.object_list[self.selection[2]] == "super pacgomme":
                pyxel.circb(20 + 8, 10 + 8, 5, 6)
            elif self.object_list[self.selection[2]] == "0":
                pyxel.text(20 - 4, 10 + 4, "nothing", 7)
            elif self.object_list[self.selection[2]] == "portal":
                pyxel.rect(20, 10, 16, 16, 0)
                pyxel.circ(20 + 8, 10 + 8, 2, 10)
                pyxel.circb(20 + 8, 10 + 8, 5, pyxel.frame_count % 15)
            elif self.object_list[self.selection[2]] == "=":
                pyxel.text(20 + 8, 10 + 8, "+", 6)
            else:
                pyxel.blt(20, 10, 0, self.object[self.object_list[self.selection[2]]][0],
                          self.object[self.object_list[self.selection[2]]][1], 16, 16)
            pyxel.text(8, 15, '<', 6)
            pyxel.text(45, 15, ">", 6)
            if self.plateau_bien_construit(): # show a smile if the board is constructed correctly
                pyxel.text(pyxel.width - 50, 10, ':)', 6)
                pyxel.text(pyxel.width - 50, 10, ':)', 6)
            else:
                pyxel.text(pyxel.width - 50, 10, ':(', 6)


Creative()
