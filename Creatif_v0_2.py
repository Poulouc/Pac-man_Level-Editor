import pyxel
import bouton
import json

"""made by Romain Guillon"""

class Creatif:
    def __init__(self):
        self.selection = [21, 21, 0]  # selecteur taille nouveau plateau et item
        self.bouton = []  # plateau bouton
        self.objet = {"pacman": [16, 0], "fantome": [48, 0], "-": [0, 80], "|": [16, 80], ">": [0, 96], "<": [16, 96],
                      "+": [32, 96], ".": [48, 96], "pacgomme": "1", "super pacgomme": "!", "0": "rien", "portail": "*", "=": "="}
        # pacman,fantome,mur l, mur h, coin sup d, coin sup g, coin inf g, coin inf d
        self.list_objet = list(self.objet.keys())
        self.show = False
        self.enreg = bouton.start_up()
        self.level_selected = -2  # permet de savoir quel plateau est à charger
        self.decal = 0  # permet de centrer le plateau de jeu
        pyxel.init(900, 900, title="Creativ mod", fps=60, display_scale=1)
        self.autre_bouton = [bouton.Button(pyxel.height // 2 - 22, pyxel.width * 65 // 100, 45, 45, 'New'), bouton.Button(pyxel.height - 25, pyxel.width - 25, 20, 20, "Menu"), bouton.Button(pyxel.height - 25, pyxel.width - 55, 20, 20, "+|+")]
        self.menu = bouton.Menu(pyxel.height, pyxel.width, len(self.enreg))
        self.autre_bouton[1].toggle()
        self.menu.name = "| Select Level to Edit |"
        pyxel.camera(0, 0)
        pyxel.load("PYXEL_RESOURCE_FILE.zip")
        pyxel.run(self.update, self.draw)

    def initialisateur(self, n):
        self.level_selected = n
        self.bouton = []  # vide-les bouton au cas où on change de plateau en cours de fonctionnement du jeu
        if n == -1:
            self.decal = pyxel.width // 2 - self.selection[1] * 19 // 2 - 25
            for i in range(self.selection[0]):
                self.bouton.append([])
                for j in range(self.selection[1]):
                    self.bouton[i].append(
                        bouton.Button(16 * j + 30 + j * 3 + self.decal, 16 * i + 30 + i * 3 + self.decal, 16, 16, ""))
        else:
            with open(self.enreg[self.level_selected]['file-name']) as f:
                plateau = f.read().splitlines()
            niveau = []
            for val in plateau:
                niveau.append(list(val))
            self.decal = pyxel.width // 2 - (len(niveau[0]) * 19) // 2 - 30
            for i in range(len(niveau)): # remplie le plateau bouton
                self.bouton.append([])
                for j in range(len(niveau[i])):
                    if [i, j] == self.enreg[self.level_selected]["pacman-spawn"]:
                        self.bouton[i].append(bouton.Button(16 * j + 30 + j * 3 + self.decal, 16 * i + 30 + i * 3 + self.decal, 16, 16, "pacman"))
                    elif [i, j] == self.enreg[self.level_selected]["ghost-spawn"]:
                        self.bouton[i].append(bouton.Button(16 * j + 30 + j * 3 + self.decal, 16 * i + 30 + i * 3 + self.decal, 16, 16, "fantome"))
                    elif self.enreg[n]["tp"] != [] and ([i, j] == self.enreg[n]["tp"][0] or [i, j] == self.enreg[n]["tp"][1]):
                        self.bouton[i].append(bouton.Button(16 * j + 30 + j * 3 + self.decal, 16 * i + 30 + i * 3 + self.decal, 16, 16, "portail"))
                    elif niveau[i][j] == "1":
                        self.bouton[i].append(bouton.Button(16 * j + 30 + j * 3 + self.decal, 16 * i + 30 + i * 3 + self.decal, 16, 16, "pacgomme"))
                    elif niveau[i][j] == "!":
                        self.bouton[i].append(bouton.Button(16 * j + 30 + j * 3 + self.decal, 16 * i + 30 + i * 3 + self.decal, 16, 16, "super pacgomme"))
                    else:
                        self.bouton[i].append(bouton.Button(16 * j + 30 + j * 3 + self.decal, 16 * i + 30 + i * 3 + self.decal, 16, 16, str(niveau[i][j])))
        bouton.Soundtrack()  # permet de savoir si le plateau a été correctement chargé
        pyxel.play(0, [0, 1], loop=False)

    def selecteur(self, i):
        if 0 <= self.selection[2] + i < len(self.list_objet):
            self.selection[2] += i

    def set_size(self, i, o):
        if 4 <= self.selection[o] + i <= 42:
            self.selection[o] += i

    def creation_niveau(self):
        if self.plateau_bien_construit() and self.level_selected != -2:
            tp = []
            plateau_txt = ""
            for i in range(len(self.bouton)):
                for j in range(len(self.bouton[i])):
                    if self.bouton[i][j].text in ["-", "|", "<", ">", "+", ".", "1", "0", "!", "="]:
                        plateau_txt += self.bouton[i][j].text
                    elif self.bouton[i][j].text == "pacman":
                        plateau_txt += "0"
                        pacman = [i, j]
                    elif self.bouton[i][j].text == "fantome":
                        plateau_txt += "0"
                        fantome = [i, j]
                    elif self.bouton[i][j].text == "portail":
                        plateau_txt += "0"
                        tp.append([i, j])
                    else:
                        plateau_txt += self.objet[self.bouton[i][j].text]
                plateau_txt += "\n"
                print(plateau_txt)
            if self.level_selected == -1:
                with open("info_niveau.json", "w") as info_niveau:
                    json.dump(self.enreg + [{"file-name": "plateau_" + str(len(self.enreg)) + ".txt", "pacman-spawn": pacman,
                                           "ghost-spawn": fantome, "tp": tp, "score": 0}], info_niveau, indent=2)
                with open("plateau_" + str(len(self.enreg)) + ".txt", "w") as f:
                    f.write(plateau_txt)
            else:
                self.enreg[self.level_selected] = {"file-name": "plateau_" + str(self.level_selected) + ".txt",
                                                   "pacman-spawn": pacman,
                                                   "ghost-spawn": fantome, "tp": tp, "score": 0}
                with open("info_niveau.json", "w") as info_niveau:
                    json.dump(self.enreg, info_niveau, indent=2)
                with open("plateau_" + str(self.level_selected) + ".txt", "w") as f:
                    f.write(plateau_txt)

    def plateau_bien_construit(self):
        """Verifie que le plateau est bien construit"""
        pacman = 0
        fantome = 0
        tp = 0
        for i in range(len(self.bouton)):
            for j in range(len(self.bouton[i])):
                if self.bouton[i][j].text == "pacman":
                    pacman += 1
                elif self.bouton[i][j].text == "fantome":
                    fantome += 1
                elif self.bouton[i][j].text == "portail":
                    tp += 1
                elif self.bouton[i][j].text == "":
                    return False
        if pacman == 1 and fantome == 1 and tp in [0, 2]:
            return True
        return False

    def crea_toggle(self, n):
        self.initialisateur(n)
        self.menu.toggle_menu()
        self.autre_bouton[0].toggle()
        self.autre_bouton[1].toggle()

    def miroir(self):
        """Reconstruit le miroir du plateau"""
        inverse = [".", "<", "+", ">"]
        for g in range(len(self.bouton)):
            i, j = 0, len(self.bouton[0]) - 1
            while i < j:  # compliqué de faire le mirroir du centre
                if self.bouton[g][i].text != "" and self.bouton[g][j].text == "":
                    if self.bouton[g][i].text in inverse:
                        self.bouton[g][j].text = inverse[bouton.recherche(inverse, self.bouton[g][i].text) - 2]
                    else:
                        self.bouton[g][j].text = self.bouton[g][i].text
                elif self.bouton[g][j].text != "" and self.bouton[g][i].text == "":
                    if self.bouton[g][j].text in inverse:
                        self.bouton[g][i].text = inverse[bouton.recherche(inverse, self.bouton[g][j].text) - 2]
                    else:
                        self.bouton[g][i].text = self.bouton[g][j].text
                i += 1
                j -= 1

    def update(self):
        pyxel.cls(0)
        if pyxel.btnp(pyxel.KEY_H):  # affiche la notice de jeu
            self.show = not self.show
        elif self.menu.Menu_enabled:
            if pyxel.btn(pyxel.KEY_Q):
                self.menu.selecteur_niveau(-1)
            elif pyxel.btn(pyxel.KEY_D):
                self.menu.selecteur_niveau(1)
            elif pyxel.btnp(pyxel.KEY_UP):
                self.set_size(1, 0)
            elif pyxel.btnp(pyxel.KEY_DOWN):
                self.set_size(-1, 0)
            elif pyxel.btnp(pyxel.KEY_RIGHT):
                self.set_size(1, 1)
            elif pyxel.btnp(pyxel.KEY_LEFT):
                self.set_size(-1, 1)
            self.menu.selecteur_niveau(pyxel.mouse_wheel)
        else:
            for i in range(len(self.bouton)):
                for j in range(len(self.bouton[i])):
                    if self.bouton[i][j].is_pressed_LEFT() and self.bouton[i][j].text == "":
                        self.bouton[i][j].text = self.list_objet[self.selection[2]]
                    elif self.bouton[i][j].is_pressed_LEFT() and self.bouton[i][j].text != "":
                        self.bouton[i][j].text = ""
                    elif self.bouton[i][j].is_pressed_RIGHT() and self.bouton[i][j].text != "":
                        self.selection[2] = bouton.recherche(self.list_objet, self.bouton[i][j].text, 0)
            if self.autre_bouton[1].is_pressed_LEFT():
                self.crea_toggle(-2)
            elif self.autre_bouton[2].is_pressed_LEFT():
                self.miroir()
            elif pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btnp(pyxel.KEY_Q):
                self.selecteur(-1)
            elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btnp(pyxel.KEY_D):
                self.selecteur(1)
            elif self.plateau_bien_construit() and pyxel.btnp(pyxel.KEY_R):
                self.creation_niveau()
            self.selecteur(pyxel.mouse_wheel)

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
            self.autre_bouton[0].draw()
            pyxel.text(self.autre_bouton[0].x + 20, self.autre_bouton[0].y + 60, str(self.selection[1]), 6)
            pyxel.text(self.autre_bouton[0].x - 20, self.autre_bouton[0].y + 23, str(self.selection[0]), 6)
            self.menu.draw()
            val = self.menu.est_presser()
            if val is not None and val < len(self.enreg):
                self.crea_toggle(val)
            elif self.autre_bouton[0].is_pressed_LEFT():
                self.crea_toggle(-1)
        else:
            pyxel.mouse(True)
            self.autre_bouton[1].draw()
            self.autre_bouton[2].draw()
            for i in range(len(self.bouton)):  # affiche ce qui est enregistré dans le bouton
                for j in range(len(self.bouton[i])):
                    if self.bouton[i][j].text == "":
                        self.bouton[i][j].draw()
                    elif self.bouton[i][j].text == "portail":
                        pyxel.rect(self.bouton[i][j].x, self.bouton[i][j].y, 16, 16, 0)
                        pyxel.circ(self.bouton[i][j].x + 8, self.bouton[i][j].y + 8, 2, 10)
                        pyxel.circb(self.bouton[i][j].x + 8, self.bouton[i][j].y + 8, 5, pyxel.frame_count % 15)
                    elif self.bouton[i][j].text == "pacgomme":
                        pyxel.rect(self.bouton[i][j].x, self.bouton[i][j].y, 16, 16, 0)
                        pyxel.circ(self.bouton[i][j].x + 8, self.bouton[i][j].y + 8, 2, 10)
                    elif self.bouton[i][j].text == "super pacgomme":
                        pyxel.rect(self.bouton[i][j].x, self.bouton[i][j].y, 16, 16, 0)
                        pyxel.circb(self.bouton[i][j].x + 8, self.bouton[i][j].y + 8, 5, 6)
                    elif self.bouton[i][j].text == "0":
                        pyxel.rect(self.bouton[i][j].x, self.bouton[i][j].y, 16, 16, 0)
                    elif self.bouton[i][j].text == "=":
                        pyxel.text(self.bouton[i][j].x + 6, self.bouton[i][j].y + 6, "+", 6)
                    else:
                        pyxel.blt(self.bouton[i][j].x, self.bouton[i][j].y, 0, self.objet[self.bouton[i][j].text][0], self.objet[self.bouton[i][j].text][1],
                                  16, 16)
            if self.list_objet[self.selection[2]] == "pacgomme":
                pyxel.circ(20 + 8, 10 + 8, 2, 10)
            elif self.list_objet[self.selection[2]] == "super pacgomme":
                pyxel.circb(20 + 8, 10 + 8, 5, 6)
            elif self.list_objet[self.selection[2]] == "0":
                pyxel.text(20 - 4, 10 + 4, "nothing", 7)
            elif self.list_objet[self.selection[2]] == "portail":
                pyxel.rect(20, 10, 16, 16, 0)
                pyxel.circ(20 + 8, 10 + 8, 2, 10)
                pyxel.circb(20 + 8, 10 + 8, 5, pyxel.frame_count % 15)
            elif self.list_objet[self.selection[2]] == "=":
                pyxel.text(20 + 8, 10 + 8, "+", 6)
            else:
                pyxel.blt(20, 10, 0, self.objet[self.list_objet[self.selection[2]]][0],
                          self.objet[self.list_objet[self.selection[2]]][1], 16, 16)
            pyxel.text(8, 15, '<', 6)
            pyxel.text(45, 15, ">", 6)
            if self.plateau_bien_construit(): # affiche un sourire si le plateau est bien construit
                pyxel.text(pyxel.width - 50, 10, ':)', 6)
            else:
                pyxel.text(pyxel.width - 50, 10, ':(', 6)


Creatif()