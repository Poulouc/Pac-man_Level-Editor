import json
from random import randint
from time import monotonic
import pyxel
import bouton


# fichier personnage decor --> pyxel edit PYXEL_RESOURCE_FILE

# definition du plateau
# "1" pac-gum
# "!" super pac-gum
# "0" case vide
# ">" coin supérieur droit
# "<" coin supérieur gauche
# "+" coin inférieur gauche
# "." coin inférieur droit
# "-" mur horizontal
# "|" mur vertical
# "*" fruit béni
# 🛑pacman et fantôme non posé sur le plateau uniquement définie par son x et y🛑
# pacman et fantôme respect les règles du plateau et ne peuvent franchir les murs définis dans infranchissable
"""made by Romain Guillon"""

class Pacman:
    """Permet de jouer au pac-man avec la possibilité d'ajouter des niveaux via Creatif"""
    def __init__(self, speed=6):
        """Initialisation de base du pacman"""
        self.fantome = [[None, None, [0, 0], False], [None, None, [0, 0], False], [None, None, [0, 0], False],
                        [None, None, [0, 0], False]]
        # chaque valeur est un fantôme est composé de ses coordonnées x, y, de direction prise et s'il est mangeable
        self.coordonne = [[-1, 0], [0, -1], [1, 0], [0, 1]]  # haut, gauche, bas, droite ,et ordre très important car l'opposé de la ou on va -2 est la ou on vient important pour fantome
        self.infranchissable = {"-": [0, 80], "|": [16, 80], ".": [48, 96], "+": [32, 96], "<": [16, 96], ">": [0, 96],
                                "=": [80082, 80082]}
        self.show = False  # permet d'afficher la notice du jeu et de le mettre en pause
        self.temps = 0  # temps depuis le début du jeu permettent de faire apparaitre les fantômes
        self.point = 0  # nb de point total sur le plateau
        self.plateau = []  # plateau de jeu
        self.originel = []  # [pxy, fxy, tp, niv selectionner]
        self.pacman = []  # [pxy, [0, 0]]  # emplacement de pacman et ancienne direction prise
        self.vie = 3  # nombre de vie de pacman
        self.tmpsmangeable = 0  # temps où les fantômes sont mangeables
        self.pause = 0  # temps de pause du jeu
        self.nb_fantome = 0  # nb de fantôme déjà sur le terrain
        self.high_score = 0
        self.decal = 0
        self.donne = bouton.start_up()
        pyxel.init(700, 700, title="Pac-man", fps=speed)
        self.menu = bouton.Menu(pyxel.height, pyxel.width, len(self.donne))
        pyxel.camera(0, 0)
        pyxel.load("PYXEL_RESOURCE_FILE.zip")  # charge les items du plateau depuis le dossier pyxel_ressource_file.zip
        pyxel.run(self.update, self.draw)

    def initialisateur(self, n):
        """Permet d'initialiser les données du pacman avec les données du niveau choisi"""
        with open(self.donne[n]['file-name']) as f:
            plateau = f.read().splitlines()
        niveau = []
        for val in plateau:
            niveau.append(list(val))
        self.plateau = niveau
        self.originel = [self.donne[n]['pacman-spawn'], self.donne[n]['ghost-spawn'], self.donne[n]["tp"], n]
        self.high_score = self.donne[n]["score"]
        self.pacman = [self.originel[0][:], [0, 0]]  # [:] permet copie à une autre adresse mémoire du tableau
        self.point = self.nbpoint()
        self.temps = monotonic()
        self.pause = 3
        self.vie = 3
        self.nb_fantome = 0
        self.tmpsmangeable = 0
        self.decal = pyxel.width // 2 - len(self.plateau[0]) * 16 // 2 + 15 # permet de centrer à peu près le plateau
        bouton.Soundtrack()
        pyxel.play(0, [0, 1], loop=False)  # Permet d'etre sûr que l'instruction a bien été chargé

    def bestscore(self):
        if self.point > self.high_score:
            with open('info_niveau.json') as file:
                donnee = json.load(file)
            donnee[self.originel[-1]]["score"] = self.point
            with open("info_niveau.json", "w") as info_niveau:
                json.dump(donnee, info_niveau, indent=2)
            self.high_score = self.point

    def nbpoint(self):
        """Compte le nb de chose mangeable sur le terrain"""
        p = 0
        for i in range(len(self.plateau)):
            for j in range(len(self.plateau[i])):
                if self.plateau[i][j] in "1!":
                    p += 1
        return p

    def teleporteur(self):
        """Permet de faire téléporter Pacman d'un endroit à un autre du plateau"""
        if not self.originel[2] == [] and self.pacman[0] == self.originel[2][0]:
            self.pacman[0] = [self.originel[2][1][0], self.originel[2][1][1]]
        elif not self.originel[2] == [] and self.pacman[0] == self.originel[2][1]:
            self.pacman[0] = [self.originel[2][0][0], self.originel[2][0][1]]

    def direction(self, ind):
        """Permet de diriger le pacman
        ind correspond à l'indice de la direction enregistré dans self.coordonné
        et permet de diriger le pacman en ajoutant les valeurs défini par ind direction et l'ajoute aux x et y du pacman"""
        self.teleporteur()
        if self.plateau[self.pacman[0][0] + self.coordonne[ind][0]][
            self.pacman[0][1] + self.coordonne[ind][1]] not in self.infranchissable:
            self.pacman[1] = self.coordonne[ind]
            self.pacman[0][0], self.pacman[0][1] = self.pacman[0][0] + self.coordonne[ind][0], self.pacman[0][1] + \
                                                   self.coordonne[ind][1]
            self.event()
            self.plateau[self.pacman[0][0]][self.pacman[0][1]] = "0"

    def mangeable(self, t):
        for i in range(self.nb_fantome):
            self.fantome[i][3] = True
        self.tmpsmangeable = monotonic() - self.temps + t

    def event(self):
        """Permet de faire les actions suivantes
        pacman peut manger les fantômes
        -un fantôme malade a été mangé
        -un fantôme a mangé Pacman"""
        i = 0
        if self.plateau[self.pacman[0][0]][self.pacman[0][1]] == "!":
            self.mangeable(7)
        elif self.plateau[self.pacman[0][0]][self.pacman[0][1]] == "*":
            self.point += 100
            self.mangeable(10)
        while self.nb_fantome > i:
            if self.fantome[i][3] and self.fantome[i][:2] == self.pacman[0]:  # si le fantôme est mangeable et manger
                self.fantome[i] = [self.originel[1][0], self.originel[1][1], [0, 0], False]
                self.point += 200
            elif not self.fantome[i][3] and self.fantome[i][:2] == self.pacman[0]:
                # si le fantôme n'est pas mangeable et qu'on le rencontre
                for j in range(self.nb_fantome):
                    self.fantome[j] = [self.originel[1][0], self.originel[1][1], [0, 0], False]
                self.pacman = [self.originel[0][:], [0, 0]]
                self.vie -= 1
                self.pause = monotonic() - self.temps + 3
            i += 1

    def auto_mod(self, fantome):
        """Auto-pilot des fantômes"""
        if not fantome[:2] == [None, None] and not self.show and monotonic() - self.temps > self.pause:
            self.event()
            # tp pour les fantômes
            if not self.originel[2] == [] and fantome[:2] == self.originel[2][0]:
                fantome[0], fantome[1] = self.originel[2][1][0], self.originel[2][1][1]
            elif not self.originel[2] == [] and fantome[:2] == self.originel[2][1]:
                fantome[0], fantome[1] = self.originel[2][0][0], self.originel[2][0][1]
                # choisi une nouvelle direction
            possibilite = []
            for i in range(len(self.coordonne)):
                # vérifie haut bas gauche droite s'il y a un mur n'est pas répertorié dans la possibilité
                if self.coordonne[i - 2] != fantome[2] and self.plateau[self.coordonne[i][0] + fantome[0]][
                    self.coordonne[i][1] + fantome[
                        1]] not in "-+.|<>":  # opposé de la direction ou l'on va est la direction d'ou l'on vient donc si gauche -2 dans la liste est droite
                    # si se n'est pas la direction de laquelle on vient et si se n'est pas un mur dans cette direction
                    possibilite.append(self.coordonne[i])
            fantome[2] = possibilite[randint(0, len(possibilite) - 1)]
            # choisi une nouvelle direction parmis possibilité et l'enregistre pour ne pas retourner en arrière
            fantome[0], fantome[1] = fantome[0] + fantome[2][0], fantome[1] + fantome[2][1]
            # replace le fantôme directement donc pas besoin de haut bas etc, car coordonnés déjà défini
            if randint(0, 1000) == 42 and self.plateau[fantome[0]][fantome[1]] != "*":
                self.plateau[fantome[0]][fantome[1]] = "*"

    def convertime(self):  # en soi ça ne sert à rien, mais c sympa
        """Permet d'afficher le temps de jeu"""
        sec = int(monotonic() - self.temps)
        return '{:02}:{:02}'.format(sec // 60, sec % 60)

    def redemarage(self):
        """Fait redémarrer le jeu après un certain temps"""
        if self.pause < monotonic() - self.temps - 1:
            self.pause = monotonic() - self.temps + 3
        elif self.pause < monotonic() - self.temps:
            self.menu.toggle_menu()

    def update(self):
        pyxel.cls(0)  # mettre à 1 pour comprendre comment l'affichage fonctionne
        if self.menu.Menu_enabled:
            if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_Q):
                self.menu.selecteur_niveau(-1)
            elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
                self.menu.selecteur_niveau(1)
            self.menu.selecteur_niveau(pyxel.mouse_wheel)
        else:
            if (pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_UP) or self.pacman[1] == self.coordonne[0]) \
                    and not self.show and monotonic() - self.temps > self.pause:
                self.direction(0)  # haut
            if (pyxel.btn(pyxel.KEY_Q) or pyxel.btn(pyxel.KEY_LEFT) or self.pacman[1] == self.coordonne[1]) \
                    and not self.show and monotonic() - self.temps > self.pause:
                self.direction(1)  # gauche
            if (pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN) or self.pacman[1] == self.coordonne[2]) \
                    and not self.show and monotonic() - self.temps > self.pause:
                self.direction(2)  # bas
            if (pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT) or self.pacman[1] == self.coordonne[3]) \
                    and not self.show and monotonic() - self.temps > self.pause:
                self.direction(3)  # droite
            if pyxel.btnp(pyxel.KEY_H):  # affiche la notice de jeu et met pause
                self.show = not self.show

    def ghost_action(self):
        """Fait jouer les fantômes chacun leurs tours comme sur un jeu de plateau"""
        if self.nb_fantome < 4 and monotonic() - self.temps > [10, 20, 30, 35][
            self.nb_fantome]:  # fait appraitre les fantome
            self.fantome[self.nb_fantome][:2] = [self.originel[1][0], self.originel[1][1]]
            self.nb_fantome += 1
        if monotonic() - self.temps > self.tmpsmangeable:  # les rend immangeables
            for jsp in range(self.nb_fantome):
                self.fantome[jsp][3] = False
            self.tmpsmangeable = 0
        for ghost in range(self.nb_fantome):  # les fait jouer
            self.auto_mod(self.fantome[ghost])

    def ghost_draw(self, coordonnee):
        for g in range(self.nb_fantome):
            if self.fantome[g][3] and self.tmpsmangeable < monotonic() - self.temps + 2 and \
                    self.fantome[g][:2] == coordonnee:
                pyxel.blt(16 * coordonnee[1] - 8 + self.decal, 16 * coordonnee[0] - 8 + self.decal, 0,
                          16 * (pyxel.frame_count % 2), 64, 16, 16)
            elif self.fantome[g][3] and self.fantome[g][:2] == coordonnee:
                pyxel.blt(16 * coordonnee[1] - 8 + self.decal, 16 * coordonnee[0] - 8 + self.decal, 0, 0, 64, 16, 16)
            elif self.fantome[g][:2] == coordonnee:
                pyxel.blt(16 * coordonnee[1] - 8 + self.decal, 16 * coordonnee[0] - 8 + self.decal, 0,
                          bouton.recherche(self.coordonne, self.fantome[g][2], 0) * 16 + 32, g * 16, 16, 16)

    def decompte(self):
        if monotonic() - self.temps + 3 > self.pause > monotonic() - self.temps:  # compte à rebour de 3 sec
            pyxel.blt(self.decal // 2, self.decal // 2, 0, [48, 24, 0][-int(monotonic() - self.pause - self.temps)],
                      112, 24, 35)

    def indicateur_joueur(self):
        pyxel.text(pyxel.width * 80 // 100, 20, self.convertime() + " min", 7)
        pyxel.text(10, pyxel.height - 30, "Press H to put pause and see how to play", 10)
        pyxel.text(pyxel.width * 90 // 100, 20,
                   "High Score : " + str(self.high_score) + 2 * "\n" + str(self.point - self.nbpoint()) + " : point", 7)
        for i in range(self.vie):  # affiche le nb de vie en affichant des pacman
            pyxel.blt(16 * i + 5, 5, 0, 16, 0, 16, 16)
        self.decompte()

    def draw(self):
        pyxel.blt(pyxel.width // 2 - 50, 10, 0, 0, 152, 111, 16)
        # affiche le menu
        if self.menu.Menu_enabled:
            self.menu.draw()
            val = self.menu.est_presser()
            if val is not None and val < len(self.donne):
                self.initialisateur(val)
                self.menu.toggle_menu()
        else:
            # consigne de jeu
            if self.show:
                pyxel.text(pyxel.width // 2 - 30, pyxel.height // 2 - 50,
                           "Up or Z to go up" + 2 * "\n" + "Left or Q to go left " + 2 * "\n" +
                           "Down or S to go down" + 2 * "\n" + "Right or D to go right" + 2 * "\n" +
                           "Echap to exit the game", 6)
                self.pause = monotonic() - self.temps + 3
                pyxel.text(10, pyxel.height - 30, "Press H to play ", 10)
            elif self.point - self.nbpoint() == self.point:  # s'il n'y a plus de gum sur le terrain
                pyxel.blt(pyxel.width // 2 - 50, pyxel.height // 2 - 30, 0, 0, 168 + 16 * (pyxel.frame_count % 2), 111, 16)
                pyxel.text(pyxel.width * 90 // 100, 20, "High Score : " + str(self.high_score) + 2 * "\n" + str(
                               self.point - self.nbpoint()) + " : point", 7)
                self.bestscore()  # enregistre le nouveau meilleur score uniquement si on gagne
                self.decompte()
                self.redemarage()
            elif self.vie == 0:  # s'il n'a plus de vie
                pyxel.text(pyxel.width // 2, pyxel.height // 2 - 8, 'You Lose', pyxel.frame_count % 3 + 10)
                self.decompte()
                self.redemarage()
            else:
                self.indicateur_joueur()
                for i in range(len(self.plateau)):
                    for j in range(len(self.plateau[i])):
                        if self.pacman[0] == [i, j]:  # affiche notre star
                            pyxel.blt(16 * j - 16 // 2 + self.decal, 16 * i - 16 // 2 + self.decal, 0,
                                      16 * (pyxel.frame_count % 2),
                                      16 * bouton.recherche([[1, 0], [0, 1], [0, -1], [-1, 0]], self.pacman[1], 0), 16,
                                      16)
                        elif self.plateau[i][j] == "1":  # affiche les pac-gum
                            pyxel.circ(16 * j + self.decal - 1, 16 * i + self.decal - 1, 2, 10)
                        elif self.plateau[i][j] == "!":  # affiche les super pac-gum
                            pyxel.circb(16 * j + self.decal - 1, 16 * i + self.decal - 1, 5, 6)
                        elif self.plateau[i][j] == "=":
                            pyxel.text(16 * j + self.decal - 1, 16 * i + self.decal - 1, "+", 6)
                        elif self.plateau[i][j] in self.infranchissable:
                            pyxel.blt(16 * j + self.decal - 8, 16 * i + self.decal - 8, 0,
                                      self.infranchissable[self.plateau[i][j]][0],
                                      self.infranchissable[self.plateau[i][j]][1], 16, 16)
                        elif self.plateau[i][j] == "*":  # le fruit béni
                            pyxel.blt(16 * j - 8 + self.decal, 16 * i - 8 + self.decal, 0, 96, 0, 16, 16)
                        self.ghost_draw([i, j])
                self.ghost_action()


Pacman() #  possibilité de régler la vitesse manuellement
# * étale tous les arguments pour les prendre en paramètre