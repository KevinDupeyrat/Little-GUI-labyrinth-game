#! /usr/bin/python3
# -*-coding:Utf-8 -*

"""
   Ce module contient la classe Labyrinthe.
   Elle permet d'initialier la grille en partant d'un
   str. Chaque joueurs aura son propre robot
   représenté par une lettre.
   Ses coordonées seront mis au hazard dans la grill
"""

import copy
import robot
import random

SYMBOLE = ['A', 'B', 'C', 'D', 'E']


class Labyrinthe:

    """
        Classe représentant un labyrinthe.
        Elle aurat comme attribut les dimensions du labyrinthe,
        le nom, la position des robots et la
        position de la sortie.

        Elle inclut également toutes les méthodes
        permettant la mouvement du robot dans ce labyrinthe
    """

    def __init__(self, nom, grill):
        self.nom = nom
        self.hauteur = 1
        self.largeur = 0
        self.case_vide = []
        self.grille = self.__init_labyrinthe(grill)
        self.grille_vierge = copy.deepcopy(self.grille)
        self.robots = []
        self.sortie = self.__init_element("U")

    def nouveau_joueur(self):

        """ On ajouter un nouveau joueur dans la partie
            en lui attribuant des coordonées et un symbole """

        # ATTENTION ! id_robot commence à 0  !!!
        id_robot = len(self.robots)
        symbole_robot = SYMBOLE[id_robot]
        robot_x, robot_y = self.__init_cooronnees_robot()
        joueur = robot.Robot(id_robot,
                             robot_x, robot_y, symbole_robot)
        self.robots.append(joueur)
        self.grille[joueur.x][joueur.y] = joueur.symbole
        # On retourne l'identifiant à l'utilisateur
        # celui-ci est unique et utilisé par
        # le joueur tout le long de la partie
        return joueur

    def __init_cooronnees_robot(self):

        """ On initialise les coordonées du nouveau robot
            de façon aléatoire sur les cases vide de la cartes
            cette methode renvoie un tuple de coodonnées  """

        return random.choice(self.case_vide)

    def __init_labyrinthe(self, grille):

        """ Méthode privée d'initialisation du labyrinthe.
            Nous allons calculer les dimensions du
            labyrinthe et également transférer le
            labyrinthe de l'etat de str à une list
            à deux dimensions pour faciliter
            les mouvements du robot """

        # On fait le calcule des dimension du labyrinthe
        for i in grille:
            if i == "\n":
                self.hauteur += 1
                self.largeur = 0
            else:
                self.largeur += 1

        # List à deux dimensions
        array = [[0 for _ in range(self.largeur)] for _ in range(self.hauteur)]
        i, k = 0, 0
        while i < self.hauteur:
            j = 0
            while j < self.largeur:

                if grille[k] is not "\n":
                    array[i][j] = grille[k]
                    if array[i][j] is " ":
                        self.case_vide.append((i, j))
                    j += 1
                k += 1

            i += 1

        return array

    def __init_element(self, element):

        """ Méthode privée d'initialisation du robot
            Ou de tout autre élément au besoin (sortie, mur ...)
            On initilise tous les éléments passé en paramètre
            pour pouvoir connaitre leur coordonées dans le
            tableau à deux dimension """

        i = 0
        while i < self.hauteur:
            j = 0
            while j < self.largeur:

                if self.grille[i][j] == element:
                    return (i, j)
                j += 1

            i += 1

    def robot_haut(self, identifient_joueur, action):

        """ Méthode qui demande au robot d'aller
            d'un cran vers le haut """

        if action == 'm':
            return self.__murrer_porte(self.robots[identifient_joueur].x - 1,
                                       self.robots[identifient_joueur].y)
        if action == 'p':
            return self.__percer_mur(self.robots[identifient_joueur].x - 1,
                                     self.robots[identifient_joueur].y)
        else:
            return self.__bouge_le_robot(self.robots[identifient_joueur].x - 1,
                                         self.robots[identifient_joueur].y,
                                         identifient_joueur)

    def robot_bas(self, identifient_joueur, action):

        """ Méthode qui demande au robot d'aller/murrer/percer
            d'un cran vers le bas """

        if action == 'm':
            return self.__murrer_porte(self.robots[identifient_joueur].x + 1,
                                       self.robots[identifient_joueur].y)
        if action == 'p':
            return self.__percer_mur(self.robots[identifient_joueur].x + 1,
                                     self.robots[identifient_joueur].y)
        else:
            return self.__bouge_le_robot(self.robots[identifient_joueur].x + 1,
                                         self.robots[identifient_joueur].y,
                                         identifient_joueur)

    def robot_gauche(self, identifient_joueur, action):

        """ Méthode qui demande au robot d'aller/murrer/percer
            d'un cran vers la gauche """

        if action == 'm':
            return self.__murrer_porte(self.robots[identifient_joueur].x,
                                       self.robots[identifient_joueur].y - 1)
        if action == 'p':
            return self.__percer_mur(self.robots[identifient_joueur].x,
                                     self.robots[identifient_joueur].y - 1)
        else:
            return self.__bouge_le_robot(self.robots[identifient_joueur].x,
                                         self.robots[identifient_joueur].y - 1,
                                         identifient_joueur)

    def robot_droite(self, identifient_joueur, action):

        """ Méthode qui demande au robot d'aller/murrer/percer
            d'un cran vers la droite """

        if action == 'm':
            return self.__murrer_porte(self.robots[identifient_joueur].x,
                                       self.robots[identifient_joueur].y + 1)
        if action == 'p':
            return self.__percer_mur(self.robots[identifient_joueur].x,
                                     self.robots[identifient_joueur].y + 1)
        else:
            return self.__bouge_le_robot(self.robots[identifient_joueur].x,
                                         self.robots[identifient_joueur].y + 1,
                                         identifient_joueur)

    def __percer_mur(self, x, y):

        """ Méthode qui permet de percer un murre """

        if self.grille[x][y] != "O":
            return False, "-----------------------\nVous ne pouvez percer que les mur !!!\n-----------------------\n"
        else:
            self.grille[x][y] = " "
            return False, "-----------------------\nVous avez percer un mur !!!\n-----------------------\n"

    def __murrer_porte(self, x, y):

        """ Méthode qui permet de murrer une porte """

        if self.grille[x][y] != ".":
            return False, "-----------------------\nVous ne pouvez murrer que les portes !!!\n-----------------------\n"
        else:
            self.grille[x][y] = "O"
            return False, "-----------------------\nVous avez murrer la portes !!!\n-----------------------\n"

    def __bouge_le_robot(self, x, y, identifient_joueur):

        """ Méthode privée qui permet les mouvements du robot dans
            le labyrinthe
            On vérifie si le caractère ce situent aux coordonnées
            passé en paramètre n'est pas
            un mur 'O', si c'est n'est pas le cas,
            on positionne le robot sur ces coordonnées """

        for r in self.robots:
            if x == r.x and y == r.y:
                return False, "-----------------------\nUn pote est déjà là !!!\n-----------------------\n"

        if self.grille[x][y] == "O":
            return False, "-----------------\nAIE le mur !!!!!!\n-----------------\n"

        # Si le robot est aux mêmes coordonnées que la sortie
        # alors c'est gagnée et on renvoie True
        if (x, y) == self.sortie:
            return True, "\n---------------\nC'est gagné !!!\n----------------\n"

        self.grille = copy.deepcopy(self.grille_vierge)
        self.grille[x][y] = self.robots[identifient_joueur].symbole

        for r in self.robots:
            if r is not self.robots[identifient_joueur]:
                self.grille[r.x][r.y] = r.symbole

        self.robots[identifient_joueur].x = x
        self.robots[identifient_joueur].y = y

        return False, "\n\n\n"

    def __affiche_labyrinthe(self):

        """ Méthode d'affichage interne du labyrinthe
            Nous avons mis cette méthode en privée car l'utilisateur
            peut déja afficher le labyrinthe avec __repr__ """

        print(repr(self))

    def __repr__(self):

        """ Permet de renvoyer la string du labyrinthe pour l'afficher """

        i, j = 0, 0
        string = ""
        while i < self.hauteur:
            j = 0
            while j < self.largeur:
                string += self.grille[i][j]
                j += 1
            string += "\n"
            i += 1

        return string

    def __str__(self):

        return repr(self)
