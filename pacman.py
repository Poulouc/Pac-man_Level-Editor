# ============================================================================
# File    : pacman.py
# Author  : Poulouc
# Date    : April 7th, 2024
# Role    : Playing Pacman
# ============================================================================

import json
import pyxel
from random import randint
from time import monotonic
from code import interface


# character decor file --> pyxel edit pyxel_res

# board definition
# "1" pac-gum
# "!" super pac-gum
# "0" empty space
# ">" top right corner
# "<" top left corner
# "+" bottom left corner
# "." bottom right corner
# "-" horizontal wall
# "|" vertical wall
# "*" blessed fruit
# 🛑pacman and ghost not placed on the board only defined by their x and y🛑
# pacman and ghost follow the rules of the board and cannot cross the walls defined in impassable

class Pacman:
    """Allows playing Pac-Man with the ability to add levels via the creative mode"""
    def __init__(self, speed=6):
        """Basic initialization of Pac-Man"""
        self.ghosts = [[None, None, [0, 0], False] for _ in range(4)]
        # each value for a ghost is composed of its x, y coordinates, the direction taken, and whether it's edible
        self.coordinate = [[-1, 0], [0, -1], [1, 0], [0, 1]]  # up, left, down, right, and very important order as the opposite of where we go -2 is where we come from important for ghost
        self.impassable = {"-": [0, 80], "|": [16, 80], ".": [48, 96], "+": [32, 96], "<": [16, 96], ">": [0, 96],
                           "=": [80082, 80082]}
        self.show = False  # allows displaying the game instructions and putting it on pause
        self.time = 0  # time since the start of the game allowing to make ghosts appear
        self.points = 0  # total number of points on the board
        self.board = []  # game board
        self.original = []  # [pxy, fxy, tp, selected level]
        self.pacman = []  # [pxy, [0, 0]]  # pacman's location and previous direction taken
        self.lives = 3  # pacman's number of lives
        self.temporary_edible = 0  # time when ghosts are edible
        self.pause = 0  # game pause time
        self.nb_ghosts = 0  # number of ghosts already on the field
        self.high_score = 0
        self.offset = 0
        self.start_button = interface.start_up()
        pyxel.init(700, 700, title="Pac-man", fps=speed)
        self.menu = interface.Menu(pyxel.height, pyxel.width, len(self.start_button))
        pyxel.camera(0, 0)
        pyxel.load("./pyxel_res.pyxres")  # loads the resources from the dedicated file
        pyxel.run(self.update, self.draw)
        pyxel.run(self.update, self.draw)

    def initialize(self, n):
        """Initializes Pac-Man's data with the chosen level's data"""
        with open("./boards/" + self.start_button[n]['file-name']) as f:
            plateau = f.read().splitlines()
        level = []
        for val in plateau:
            level.append(list(val))
        self.board = level
        self.original = [self.start_button[n]['pacman-spawn'], self.start_button[n]['ghost-spawn'], self.start_button[n]["tp"], n]
        self.high_score = self.start_button[n]["score"]
        self.pacman = [self.original[0][:], [0, 0]]  # [:] allows copy with a different memory address
        self.points = self.nb_points()
        self.time = monotonic()
        self.pause = 3
        self.lives = 3
        self.nb_ghosts = 0
        self.temporary_edible = 0
        self.offset = pyxel.width // 2 - len(self.board[0]) * 16 // 2 + 15  # to center(ish) the board
        pyxel.playm(0)

    def best_score(self):
        if self.points > self.high_score:
            with open('boards/info.json') as file:
                data = json.load(file)
            data[self.original[-1]]["score"] = self.points
            with open("boards/info.json", "w") as info_niveau:
                json.dump(data, info_niveau, indent=2)
            self.high_score = self.points

    def nb_points(self):
        """Counts the number of edible things on the field"""
        p = 0
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                if self.board[i][j] in "1!":
                    p += 1
        return p

    def teleport(self):
        """Allows Pacman to teleport from one place to another on the board"""
        if not self.original[2] == [] and self.pacman[0] == self.original[2][0]:
            self.pacman[0] = [self.original[2][1][0], self.original[2][1][1]]
        elif not self.original[2] == [] and self.pacman[0] == self.original[2][1]:
            self.pacman[0] = [self.original[2][0][0], self.original[2][0][1]]

    def direction(self, ind):
        """Allows Pacman to move
        ind corresponds to the index of the direction stored in self.coordinate
        and allows Pacman to move by adding the values defined by ind direction to Pacman's x and y"""
        self.teleport()
        if self.board[self.pacman[0][0] + self.coordinate[ind][0]][
                self.pacman[0][1] + self.coordinate[ind][1]] not in self.impassable:
            self.pacman[1] = self.coordinate[ind]
            self.pacman[0][0], self.pacman[0][1] = (self.pacman[0][0] + self.coordinate[ind][0],
                                                    self.pacman[0][1] + self.coordinate[ind][1])
            self.event()
            self.board[self.pacman[0][0]][self.pacman[0][1]] = "0"

    def edible(self, t):
        for i in range(self.nb_ghosts):
            self.ghosts[i][3] = True
        self.temporary_edible = monotonic() - self.time + t

    def event(self):
        """Allows performing the following actions
        pacman can eat ghosts
        -a sick ghost was eaten
        -a ghost ate Pacman"""
        i = 0
        if self.board[self.pacman[0][0]][self.pacman[0][1]] == "!":
            self.edible(7)
        elif self.board[self.pacman[0][0]][self.pacman[0][1]] == "*":
            self.points += 100
            self.edible(10)
        while self.nb_ghosts > i:
            if self.ghosts[i][3] and self.ghosts[i][:2] == self.pacman[0]:  # if the ghost is edible and eaten
                self.ghosts[i] = [self.original[1][0], self.original[1][1], [0, 0], False]
                self.points += 200
            elif not self.ghosts[i][3] and self.ghosts[i][:2] == self.pacman[0]:
                # if the ghost is not edible and encountered
                for j in range(self.nb_ghosts):
                    self.ghosts[j] = [self.original[1][0], self.original[1][1], [0, 0], False]
                self.pacman = [self.original[0][:], [0, 0]]
                self.lives -= 1
                self.pause = monotonic() - self.time + 3
            i += 1

    def auto_mod(self, spectre):
        """Automatically moves the ghosts"""
        if not spectre[:2] == [None, None] and not self.show and monotonic() - self.time > self.pause:
            self.event()
            # teleportation for ghosts
            if not self.original[2] == [] and spectre[:2] == self.original[2][0]:
                spectre[0], spectre[1] = self.original[2][1][0], self.original[2][1][1]
            elif not self.original[2] == [] and spectre[:2] == self.original[2][1]:
                spectre[0], spectre[1] = self.original[2][0][0], self.original[2][0][1]
                # chooses a new direction
            possibilities = []
            for i in range(len(self.coordinate)):
                # checks up down left right if there is a wall not listed in possibility
                if self.coordinate[i - 2] != spectre[2] and self.board[self.coordinate[i][0] + spectre[0]][
                    self.coordinate[i][1] + spectre[
                        1]] not in "-+.|<>":  # opposite of the direction we're going is the direction we're coming from so if left -2 in the list is right
                    # if it's not the direction we're coming from and if it's not a wall in that direction
                    possibilities.append(self.coordinate[i])
            spectre[2] = possibilities[randint(0, len(possibilities) - 1)]
            # choose a new direction among the possibilities and record it to avoid going back
            spectre[0], spectre[1] = spectre[0] + spectre[2][0], spectre[1] + spectre[2][1]
            # replaces the ghost directly so no need for up, down, etc. because coordinates already defined
            if randint(0, 1000) == 42 and self.board[spectre[0]][spectre[1]] != "*":
                self.board[spectre[0]][spectre[1]] = "*"

    def convertime(self):  # in itself it serves no purpose, but it's cool
        """Displays the game time"""
        sec = int(monotonic() - self.time)
        return '{:02}:{:02}'.format(sec // 60, sec % 60)

    def restart(self):
        """Restarts the game after 3sec"""
        if self.pause < monotonic() - self.time - 1:
            self.pause = monotonic() - self.time + 3
        elif self.pause < monotonic() - self.time:
            self.menu.toggle_menu()

    def update(self):
        pyxel.cls(0)  # set to 1 to understand how the display works
        if self.menu.menu_enabled:
            if pyxel.btnp(pyxel.KEY_LEFT) or pyxel.btn(pyxel.KEY_Q):
                self.menu.level_selector(-1)
            elif pyxel.btnp(pyxel.KEY_RIGHT) or pyxel.btn(pyxel.KEY_D):
                self.menu.level_selector(1)
            self.menu.level_selector(pyxel.mouse_wheel)
        else:
            if (pyxel.btn(pyxel.KEY_Z) or pyxel.btn(pyxel.KEY_UP) or self.pacman[1] == self.coordinate[0]) \
                    and not self.show and monotonic() - self.time > self.pause:
                self.direction(0)  # up
            if (pyxel.btn(pyxel.KEY_Q) or pyxel.btn(pyxel.KEY_LEFT) or self.pacman[1] == self.coordinate[1]) \
                    and not self.show and monotonic() - self.time > self.pause:
                self.direction(1)  # left
            if (pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN) or self.pacman[1] == self.coordinate[2]) \
                    and not self.show and monotonic() - self.time > self.pause:
                self.direction(2)  # down
            if (pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT) or self.pacman[1] == self.coordinate[3]) \
                    and not self.show and monotonic() - self.time > self.pause:
                self.direction(3)  # right
            if pyxel.btnp(pyxel.KEY_H):  # displays the game instructions and pauses
                self.show = not self.show

    def ghost_action(self):
        """Makes the ghosts play each their turn like on a board game"""
        if self.nb_ghosts < 4 and monotonic() - self.time > [10, 20, 30, 35][
                self.nb_ghosts]:  # makes the ghosts appear
            self.ghosts[self.nb_ghosts][:2] = [self.original[1][0], self.original[1][1]]
            self.nb_ghosts += 1
        if monotonic() - self.time > self.temporary_edible:  # makes them inedible
            for jsp in range(self.nb_ghosts):
                self.ghosts[jsp][3] = False
            self.temporary_edible = 0
        for ghost in range(self.nb_ghosts):  # makes them play
            self.auto_mod(self.ghosts[ghost])

    def ghost_draw(self, coordonnee):
        for ectoplasme in range(self.nb_ghosts):
            if self.ghosts[ectoplasme][3] and self.temporary_edible < monotonic() - self.time + 2 and \
                    self.ghosts[ectoplasme][:2] == coordonnee:
                pyxel.blt(16 * coordonnee[1] - 8 + self.offset, 16 * coordonnee[0] - 8 + self.offset, 0,
                          16 * (pyxel.frame_count % 2), 64, 16, 16)
            elif self.ghosts[ectoplasme][3] and self.ghosts[ectoplasme][:2] == coordonnee:
                pyxel.blt(16 * coordonnee[1] - 8 + self.offset, 16 * coordonnee[0] - 8 + self.offset, 0, 0, 64, 16, 16)
            elif self.ghosts[ectoplasme][:2] == coordonnee:
                pyxel.blt(16 * coordonnee[1] - 8 + self.offset, 16 * coordonnee[0] - 8 + self.offset, 0,
                          interface.research(self.coordinate, self.ghosts[ectoplasme][2], 0) * 16 + 32, ectoplasme * 16, 16, 16)

    def countdown(self):
        if monotonic() - self.time + 3 > self.pause > monotonic() - self.time:  # 3 sec countdown
            pyxel.blt(self.offset // 2, self.offset // 2, 0, [48, 24, 0][-int(monotonic() - self.pause - self.time)],
                      112, 24, 35)

    def player_indicator(self):
        pyxel.text(pyxel.width * 80 // 100, 20, self.convertime() + " min", 7)
        pyxel.text(10, pyxel.height - 30, "Press H to put pause and see how to play", 10)
        pyxel.text(pyxel.width * 90 // 100, 20,
                   "High Score : " + str(self.high_score) + 2 * "\n" + str(self.points - self.nb_points()) + " : points", 7)
        for i in range(self.lives):  # displays the number of lives by displaying pacmans
            pyxel.blt(16 * i + 5, 5, 0, 16, 0, 16, 16)
        self.countdown()

    def draw(self):
        pyxel.blt(pyxel.width // 2 - 50, 10, 0, 0, 152, 111, 16)
        # displays the menu
        if self.menu.menu_enabled:
            self.menu.draw()
            val = self.menu.is_pressed()
            if val is not None and val < len(self.start_button):
                self.initialize(val)
                self.menu.toggle_menu()
        else:
            # game instructions
            if self.show:
                pyxel.text(pyxel.width // 2 - 30, pyxel.height // 2 - 50,
                           "Up or Z to go up\n\nLeft arrow or Q to go left\n\n"
                           "Down or S to go down\n\nRight arrow or D to go right\n\n"
                           "Esc to exit the game", 6)
                self.pause = monotonic() - self.time + 3
                pyxel.text(10, pyxel.height - 30, "Press H to play ", 10)
            elif self.points - self.nb_points() == self.points:  # if there are no more gums on the ground
                pyxel.blt(pyxel.width // 2 - 50, pyxel.height // 2 - 30, 0, 0, 168 + 16 * (pyxel.frame_count % 2), 111, 16)
                pyxel.text(pyxel.width * 90 // 100, 20, "High Score: " + str(self.high_score) + "\n\n" + str(
                    self.points - self.nb_points()) + " points", 7)
                self.best_score()  # saves the new best score only if you win
                self.countdown()
                self.restart()
            elif self.lives == 0:  # if there are no more lives
                pyxel.text(pyxel.width // 2, pyxel.height // 2 - 8, 'You Lose', pyxel.frame_count % 3 + 10)
                self.countdown()
                self.restart()
            else:
                self.player_indicator()
                for i in range(len(self.board)):
                    for j in range(len(self.board[i])):
                        if self.pacman[0] == [i, j]:  # displays our star
                            pyxel.blt(16 * j - 16 // 2 + self.offset, 16 * i - 16 // 2 + self.offset, 0,
                                      16 * (pyxel.frame_count % 2),
                                      16 * interface.research([[1, 0], [0, 1], [0, -1], [-1, 0]], self.pacman[1], 0), 16,
                                      16)
                        elif self.board[i][j] == "1":  # displays the pac-gums
                            pyxel.circ(16 * j + self.offset - 1, 16 * i + self.offset - 1, 2, 10)
                        elif self.board[i][j] == "!":  # displays the super pac-gums
                            pyxel.circb(16 * j + self.offset - 1, 16 * i + self.offset - 1, 5, 6)
                        elif self.board[i][j] == "=":
                            pyxel.text(16 * j + self.offset - 1, 16 * i + self.offset - 1, "+", 6)
                        elif self.board[i][j] in self.impassable:
                            pyxel.blt(16 * j + self.offset - 8, 16 * i + self.offset - 8, 0,
                                      self.impassable[self.board[i][j]][0],
                                      self.impassable[self.board[i][j]][1], 16, 16)
                        elif self.board[i][j] == "*":  # the blessed fruit
                            pyxel.blt(16 * j - 8 + self.offset, 16 * i - 8 + self.offset, 0, 96, 0, 16, 16)
                        self.ghost_draw([i, j])
                self.ghost_action()


Pacman()  # it's possible to manually set the speed
