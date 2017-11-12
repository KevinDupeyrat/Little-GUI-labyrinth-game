#! /usr/bin/python3
# -*-coding:UTF-8*-

# --- CLIENT ---

# Partie joué en console sans interface
# graphique

import socket
import sys
from threading import Thread
# from urllib.request import urlopen


hote = 'localhost'
port = 12800
fin_de_connexion = False
print("En attente de connexion avec le serveur ...")
# Initialisation de la socket
connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Initialisation de la connexion
# avec l'adresse du serveur et son
# port d'écoute
connexion_avec_serveur.connect((hote, port))
print("Connexion établie avec le serveur sur le port {}\n\n".format(port))
print("Tapez 'c' pour commencer à jouer")


class Envoyer(Thread):

    """ Thread chargé simplement d'envoyer
        les messages au serveur """

    def __init__(self, fin_de_connexion):
        Thread.__init__(self)
        self.fin_de_connexion = fin_de_connexion

    def run(self):
        while not self.fin_de_connexion:
            """ Code à exécuter pendant l'exécution du thread. """
            msg_envoyer = input("")
            # On envoie le message
            connexion_avec_serveur.send(msg_envoyer.lower().encode())
            if msg_envoyer == "fin":
                self.fin_de_connexion = True
                connexion_avec_serveur.close()
                print("\nAu revoir !\n")


class Recu(Thread):

    """ Thread chargé simplement d'afficher
        les message qui viennent du serveur """

    def __init__(self, fin_de_connexion):
        Thread.__init__(self)
        self.fin_de_connexion = fin_de_connexion

    def run(self):
        while not self.fin_de_connexion:
            """ Code à exécuter pendant l'exécution du thread. """
            try:
                msg_recu = connexion_avec_serveur.recv(1024)
                msg_recu = msg_recu.decode()
                if msg_recu:
                    print(msg_recu)
                    if msg_recu == "\nFin de partie.":
                        print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
                        self.fin_de_connexion = True
                        connexion_avec_serveur.close()
                        print("\nAu revoir !\n")
                        # sys.exit(0)
            except socket.error as e:
                self.fin_de_connexion = True
                connexion_avec_serveur.close()
                print("La connexion a était fermée.\n")
                print(e)


thread_envoyer = Envoyer(fin_de_connexion)
thread_recu = Recu(fin_de_connexion)

thread_recu.start()
thread_envoyer.start()
