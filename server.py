#! /usr/bin/python3
# -*-coding:UTF-8*-

# --- SERVEUR ---

import socket
import select
import os
import re
import sys
from labyrinthe import Labyrinthe


def init_serveur():
    """ Fonction qui permet la connexion au serveur """

    hote = ''
    port = 12800

    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_principale.bind((hote, port))
    connexion_principale.listen(5)
    print("Le serveur écoute à présent sur le port {}".format(port))
    return connexion_principale


def init_carte():
    """ Fonction d'affichage de carte.
        Elle affiche toutes les cartes présente dans
        le dossier 'cartes' """

    cartes = []
    input_ok = False

    """ On charge les cartes existantes
        qui sont présentent dans le dossier 'cartes' """
    for nom_fichier in os.listdir("cartes"):
        if nom_fichier.endswith(".txt"):
            chemin = os.path.join("cartes", nom_fichier)
            nom_carte = nom_fichier[:-4].lower()
            with open(chemin, "r") as fichier:
                contenu = fichier.read()

            """ Création d'une carte, à compléter """
            lab = Labyrinthe(nom_carte, contenu)
            """ Ajout de la carte dans la liste de carte """
            cartes.append(lab)

    print('Liste des cartes disponibles : \n')
    for i, carte in enumerate(cartes):
        print("\t\t\t{} -> {}".format(i + 1, carte.nom))

    choix = input("Faites votre choix \n")

    """ On fait la vérificationd de la saisie """
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

    """ attend les joueurs """
    print("En attente de joueurs ...")
    return cartes[choix - 1]


def faire_action(identifient, action, direction, labyrinthe):
    """ Fonction qui permet d'effectuer une action
        de mouvement/murrage/percage dans une
        direction donnée """

    if direction == 'n':
        return labyrinthe.robot_haut(identifient, action)
    elif direction == 's':
        return labyrinthe.robot_bas(identifient, action)
    elif direction == 'e':
        return labyrinthe.robot_droite(identifient, action)
    elif direction == 'o':
        return labyrinthe.robot_gauche(identifient, action)


# def a_qui_le_tour(id_joueur, tabIdJoueur, tabClientPartie):
#     """ Méthode qui permet de savoir c'est à qui de jouer
#         et donc de faire les action nécessaire avec la GUI.
#         On reçois en paramètre l'id du jour qui a jouer
#         et la liste de joueur. C'est donc a celui d'après de jouer """
#     au_tour_de = None
#     string = None

#     if (id_joueur + 1) > len(tabIdJoueur):
#         au_tour_de = 1
#     else:
#         au_tour_de = id_joueur + 1

#     # print("Id joueur : {}\n".format(id_joueur))
#     # print("Au tour de : {}\n".format(au_tour_de))
#     i = 0
#     for c in tabClientPartie:

#         print("au_tour_de : {}".format(au_tour_de))
#         print("tabIdJoueur i : {}".format(tabIdJoueur[i]))

#         # On envoie au joueur à qui c'est le tour
#         # le signal que c'est à lui
#         if au_tour_de == tabIdJoueur[i]:
#             c.send(b"\n--JOUER\n")
#             string += "\nC'est à vous de jouer\n"
#         # On envoie au autres le signal que ce n'est pas
#         # a eux de jouer et qu'ils doivent attendre
#         # leur tour
#         else:
#             c.send(b"\n--PASJOUER\n")
#             string += "\nVeuillez patienter . . ."
#             string += "\nC'est au tour du joueur"
#             string += " {} de jouer\n".format(
#                 id_joueur)
#         i = i + 1

#     return string


def main():
    """ Fonction principale du serveur """

    # On commence par ce connecter au serveur
    connexion_principale = init_serveur()
    # On fait le choix de la carte
    labyrinthe = init_carte()

    compteur_joueur = 0
    accepte_nouvelle_connexion = True
    ids = []
    nombre_fois = 1
    commencer_partie = False

    serveur_lance = True
    clients_connectes = []
    while serveur_lance:
        # On va vérifier que de nouveaux clients ne demandent pas à se
        # connecter
        # Pour cela, on écoute la connexion_principale en lecture
        # On attend maximum 50ms

        connexions_demandees, wlist, xlist = select.select(
            [connexion_principale],
            [], [], 0.05)

        # Si il y a encore la place pour un
        # nouveau client
        # Maximum 5
        if accepte_nouvelle_connexion:
            for connexion in connexions_demandees:
                # On accépte la nouvelle connexion
                connexion_avec_client, infos_connexion = connexion.accept()
                # On ajoute le socket connecté à la liste des clients
                clients_connectes.append(connexion_avec_client)

                ids.append(labyrinthe.nouveau_joueur())

                compteur_joueur += 1

                if compteur_joueur > 5:
                    accepte_nouvelle_connexion = False
                else:
                    accepte_nouvelle_connexion = True

        # Maintenant, on écoute la liste des clients connectés
        # Les clients renvoyés par select sont ceux devant être lus (recv)
        # On attend là encore 50ms maximum
        # On enferme l'appel à select.select dans un bloc try
        # En effet, si la liste de clients connectés est vide, une exception
        # Peut être levée
        clients_a_lire = []
        try:
            clients_a_lire, wlist, xlist = select.select(clients_connectes,
                                                         [], [], 0.05)
        except select.error:
            pass
        else:

            # On parcourt la liste des clients à lire
            for client in clients_a_lire:

                id_index = clients_connectes.index(client)
                id_joueur = ids[id_index]
                # Client est de type socket
                msg_recu = client.recv(1024)
                msg_recu = msg_recu.decode()
                msg_recu = msg_recu.lower()

                if accepte_nouvelle_connexion:
                    if msg_recu.lower() == "c":
                        if compteur_joueur < 2:
                            client.send(
                                b"Nous attendons d'autres joueur" +
                                b" pour commencer la partie ...")
                        else:
                            accepte_nouvelle_connexion = False
                            commencer_partie = True

                            i = 0
                            for c in clients_connectes:

                                string = ""
                                # # On envoie le message que c'est à son tour
                                # string += a_qui_le_tour(
                                #     id_joueur.identifient - 1,
                                #     id_index,
                                #     clients_connectes)

                                string += "La partie peut commencer !  :)"
                                string += " \nVous éte le joueur "
                                string += "{} avec la lettre: '{}'\n\n".format(
                                    i + 1, ids[i].symbole)
                                c.send((string + str(labyrinthe)).encode())
                                i = i + 1
                    else:
                        if not commencer_partie:
                            client.send(b"Appuyez sur 'c' pour" +
                                        b" commencer une partie")
                        else:
                            msg_recu = "c"

                else:

                    if re.match(r"^[nsoe][0-9]*$", msg_recu):

                        direction = msg_recu[0]
                        if len(msg_recu) == 1:
                            nombre_fois = 1
                        else:
                            nombre_fois = int(msg_recu[1])

                        i = 0
                        while i < nombre_fois:

                            i += 1

                            message_retour = faire_action(
                                id_joueur.identifient, None,
                                direction, labyrinthe)

                            string = ""
                            for c in clients_connectes:
                                if message_retour[1] != "":
                                    string = message_retour[1]

                                # On détermine à qui est le tour
                                # de jouer
                                # Pour cela nous utilisons la
                                # variable 'au_tour_de' qui
                                # incrémente de 1 à chaque fois qu'un
                                # joueur joue.
                                # Une fois que cela est déterminé,
                                # on en informe tous les joueurs
                                # string += a_qui_le_tour(
                                #     id_joueur.identifient,
                                #     id_index, clients_connectes)

                            if message_retour[0] is True:
                                for c in clients_connectes:
                                    string = message_retour[1]
                                    string += "\nLa partie a était gagnée "
                                    string += " par le joueur {}".format(
                                        id_joueur.identifient + 1)
                                    c.send(
                                        ("\nFin de partie." + string).encode())
                                    i = nombre_fois
                                    serveur_lance = False
                            else:
                                for c in clients_connectes:
                                    c.send((string + str(labyrinthe)).encode())

                    elif msg_recu == "fin":
                        serveur_lance = False
                        for c in clients_connectes:
                            c.send(b"\nFin de partie.")

                    elif re.match(r"^[mp][nsoe]$", msg_recu):
                        action = msg_recu[0]
                        direction = msg_recu[1]

                        message_retour = faire_action(
                            id_joueur.identifient,
                            action, direction, labyrinthe)

                        string = ""
                        for c in clients_connectes:
                            if message_retour[1] != "":
                                string = message_retour[1]
                            c.send((string + str(labyrinthe)).encode())

                    else:
                        string = "-----------------\nCommande"
                        string += " Invalide\n-----------------\n"
                        client.send((string + str(labyrinthe)).encode())

    print("Fermeture des connexions")
    for client in clients_connectes:
        client.close()

    connexion_principale.close()
    sys.exit(0)


if __name__ == '__main__':
    main()
