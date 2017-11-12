#! /usr/bin/python3
# -*-coding:Utf-8 -*

"""
   Ce module contient la classe Robot.
   Elle permet d'initialier le robot avec ses coordonnées
"""


class Robot:

    """Classe représentant un robot."""

    def __init__(self, identifient, x, y, symbole):
        self.identifient = identifient
        self.x = int(x)
        self.y = int(y)
        self.symbole = symbole

    def __repr__(self):
        return "<Robot x={} y={}>".format(self.x, self.y)

    def __str__(self):
        return "Robot {}.{}".format(self.x, self.y)
