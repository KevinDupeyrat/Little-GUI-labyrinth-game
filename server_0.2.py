#! /usr/bin/python3
# -*-coding:UTF-8*-

# --- SERVEUR ---

import socket
import select
import os
import re
import sys
from labyrinthe import Labyrinthe


class Server:

    def __init__(self):
        """ Initialisation de la class
            Serveur """

        self.hote = ''
        self.port = 12800
        self.compteur_joueur = 0
        self.accepte_nouvelle_connexion = True
        self.nombre_fois = 1
        self.commencer_partie = False
        self.au_tour_de = 1
        self.serveur_lance = True
        self.clients_connectes = []
        self.ids = []
        # On commence par ce connecter au serveur
        self.connexion_principale = self.__init_serveur()
        # On fait le choix de la carte
        self.labyrinthe = self.__init_carte()

    def __init_serveur(self):
        """ Fonction qui permet la connexion au serveur """

        self.connexion_principale = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)
        self.connexion_principale.bind((self.hote, self.port))
        self.connexion_principale.listen(5)
        print("Le serveur écoute à présent sur le port {}".format(self.port))
        return self.connexion_principale

    def __init_carte(self):
        """ Fonction d'affichage de carte.
        Elle affiche toutes les cartes présente dans
        le dossier 'cartes' """

        cartes = []
        input_ok = False

        # On charge les cartes existantes
        # qui sont présentent dans le dossier 'cartes'
        for nom_fichier in os.listdir("cartes"):
            if nom_fichier.endswith(".txt"):
                chemin = os.path.join("cartes", nom_fichier)
                nom_carte = nom_fichier[:-4].lower()
                with open(chemin, "r") as fichier:
                    contenu = fichier.read()

                # Création d'une carte, à compléter
                lab = Labyrinthe(nom_carte, contenu)
                # Ajout de la carte dans la liste de carte
                cartes.append(lab)

        print('Liste des cartes disponibles : \n')
        for i, carte in enumerate(cartes):
            print("\t\t\t{} -> {}".format(i + 1, carte.nom))

        choix = input("Faites votre choix \n")

        while not input_ok:
            try:
                choix = int(choix)
                min = 1
                max = len(cartes)
                assert choix in range(min, max + 1)
                input_ok = True
            except ValueError:
                print('Vous n\'avez pas choisi un nombre')
                choix = input('Faites votre choix ')
            except AssertionError:
                print('Vous n\'avez pas choisi une carte disponible')
                choix = input('Faites votre choix ')

        print("En attente de joueurs ...")
        return cartes[choix - 1]

    def __faire_action(self, identifient, action, direction):
        """ Fonction qui permet d'effectuer une action
            de mouvement/murrage/percage dans une
            direction donnée """

        if direction == 'n':
            return self.labyrinthe.robot_haut(identifient, action)
        elif direction == 's':
            return self.labyrinthe.robot_bas(identifient, action)
        elif direction == 'e':
            return self.labyrinthe.robot_droite(identifient, action)
        elif direction == 'o':
            return self.labyrinthe.robot_gauche(identifient, action)

    def __a_qui_le_tour(self, id_joueur, au_tour_de, c, string):
        """ Méthode qui permet de savoir à qui est le
            tour de jouer """

        print("Id joueur : {}\n".format(id_joueur))
        print("Au tour de : {}\n".format(au_tour_de))

        if id_joueur == au_tour_de:
            c.send(b"\n--JOUER\n")
            string += "\nC'est à vous de jouer\n"
        else:
            c.send(b"\n--PASJOUER\n")
            string += "\nVeuillez patienter . . ."
            string += "\nC'est au tour du joueur"
            string += " {} de jouer\n".format(
                id_joueur)

        return string

    def __accepte_nouveau_client(self, connexions_demandees):
        """ Méthode qui permet de savoir si on accèpte
            de nouveaux client """

        for connexion in connexions_demandees:
            # On accépte la nouvelle connexion
            connexion_avec_client, infos_connexion = connexion.accept()
            # On ajoute le socket connecté à la liste des clients
            self.clients_connectes.append(connexion_avec_client)

            self.ids.append(self.labyrinthe.nouveau_joueur())

            self.compteur_joueur += 1

            if self.compteur_joueur > 5:
                return False
            else:
                return True

    def __bouger_robot(self, msg_recu, id_joueur):
        """ Méthode qui permet de bouger un
            robot """

        # On incrémante le compteur du tour
        # donc on changera de joueur
        if self.au_tour_de < len(self.ids):
            self.au_tour_de += 1
        else:
            self.au_tour_de = 1

        # On récupère le message reçu
        # pour l'analyser
        direction = msg_recu[0]
        if len(msg_recu) == 1:
            nombre_fois = 1
        else:
            nombre_fois = int(msg_recu[1])

        i = 0
        while i < nombre_fois:

            i += 1

            message_retour = self.__faire_action(
                id_joueur.identifient, None, direction)

            if message_retour[1] != "":
                string = message_retour[1]
            else:
                string = ""

            for c in self.clients_connectes:
                # On détermine à qui est le tour
                # de jouer
                # Pour cela nous utilisons la
                # variable 'au_tour_de' qui
                # incrémente de 1 à chaque fois qu'un
                # joueur joue.
                # Une fois que cela est déterminé,
                # on en informe tous les joueurs
                string = ""
                string += self.__a_qui_le_tour(id_joueur,
                                               self.au_tour_de,
                                               c, string)

                c.send((string + str(self.labyrinthe)).encode())

            if message_retour[0] is True:
                for c in self.clients_connectes:
                    string = message_retour[1]
                    string += "\nLa partie a était gagnée "
                    string += " par le joueur {}".format(
                        id_joueur.identifient + 1)
                    c.send(
                        ("\nFin de partie." + string).encode())
                    i = nombre_fois - 1
                    self.serveur_lance = False

    def __murer_percer(self, msg_recu, id_joueur):
        """ Méthode qui permet de soit
            murer une porte soit percer un mur """

        action = msg_recu[0]
        direction = msg_recu[1]

        message_retour = self.__faire_action(
            id_joueur.identifient,
            action, direction, self.labyrinthe)

        # On incrémante le compteur du tour
        # donc on change de joueur
        if self.au_tour_de < len(self.ids):
            self.au_tour_de += 1
        else:
            self.au_tour_de = 1

        string = ""
        for c in self.clients_connectes:

            # On détermine à qui est le tour
            # de jouer
            # Pour cela nous utilisons la
            # variable 'au_tour_de' qui
            # incrémente de 1 à chaque fois qu'un
            # joueur joue.
            # Une fois que cela est déterminé,
            # on en informe tous les joueurs
            string = ""
            string += self.__a_qui_le_tour(id_joueur,
                                           self.au_tour_de,
                                           c, string)
            if message_retour[1] != "":
                string = message_retour[1]
            c.send((string + str(self.labyrinthe)).encode())

    def main(self):
        """ Fonction principale du serveur """

        while self.serveur_lance:
            # On va vérifier que de nouveaux clients ne demandent pas à se
            # connecter
            # Pour cela, on écoute la connexion_principale en lecture
            # On attend maximum 50ms

            connexions_demandees, wlist, xlist = select.select(
                [self.connexion_principale],
                [], [], 0.05)

            # Si il y a encore la place pour un
            # nouveau client
            # Maximum 5
            if self.accepte_nouvelle_connexion:

                self.accepte_nouvelle_connexion = self.__accepte_nouveau_client(
                    connexions_demandees)

            # Maintenant, on écoute la liste des clients connectés
            # Les clients renvoyés par select sont ceux devant être lus (recv)
            # On attend là encore 50ms maximum
            # On enferme l'appel à select.select dans un bloc try
            # En effet, si la liste de clients connectés est vide, une
            # exception peut être levée
            clients_a_lire = []
            try:
                clients_a_lire, wlist, xlist = select.select(
                    self.clients_connectes, [], [], 0.05)
            except select.error:
                pass
            else:

                # On parcourt la liste des clients à lire
                for client in clients_a_lire:

                    id_index = self.clients_connectes.index(client)
                    id_joueur = self.ids[id_index]
                    # Client est de type socket
                    msg_recu = client.recv(1024)
                    msg_recu = msg_recu.decode()
                    msg_recu = msg_recu.lower()

                    print(msg_recu)

                    if self.accepte_nouvelle_connexion:

                        if msg_recu.lower() == "c":

                            if self.compteur_joueur < 2:

                                client.send(
                                    b"Nous attendons d'autres joueur" +
                                    b" pour commencer la partie ...")
                            else:
                                self.accepte_nouvelle_connexion = False
                                commencer_partie = True

                                i = 0
                                for c in self.clients_connectes:

                                    string = ""
                                    # On envoie le message que c'est à son tour
                                    string += self.__a_qui_le_tour(id_index,
                                                                   self.au_tour_de,
                                                                   c, string)

                                    string += "La partie peut commencer !  :)"
                                    string += " \nVous éte le joueur "
                                    string += "{} avec la lettre: '{}'\n\n".format(
                                        i + 1, self.ids[i].symbole)
                                    c.send((string + str(
                                        self.labyrinthe)).encode())
                                    i = i + 1
                        else:
                            if not commencer_partie:
                                client.send(b"Appuyez sur 'c' pour" +
                                            b" commencer une partie")
                            else:
                                msg_recu = "c"

                    else:

                        if re.match(r"^[nsoe][0-9]*$", msg_recu):

                            self.__bouger_robot(msg_recu, id_joueur)

                        elif re.match(r"^[mp][nsoe]$", msg_recu):

                            self.__murer_percer(msg_recu, id_joueur)

                        elif msg_recu == "fin":

                            self.serveur_lance = False
                            for c in self.clients_connectes:
                                c.send(b"\nFin de partie.")

                        else:
                            string = "-----------------\nCommande"
                            string += " Invalide\n-----------------\n"
                            client.send(
                                (string + str(self.labyrinthe)).encode())

        print("Fermeture des connexions")
        for client in self.clients_connectes:
            client.close()

        self.connexion_principale.close()
        sys.exit(0)


if __name__ == '__main__':
    s = Server()
    s.main()
