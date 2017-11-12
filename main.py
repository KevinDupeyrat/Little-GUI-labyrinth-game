#! /usr/bin/python3
# -*-coding:UTF-8*-

# --- GUI ---
# Client avec interface graphique

from tkinter import *
import socket
import _thread


color = '#2d2d2d'


class Frame_Principal(Frame):

    """ Notre fenêtre principale.
        Tous les Widgets sont stockés comme attribut de cette
        fenêtre. """

    def __init__(self, fenetre, fenetre_principale, **kwargs):
        Frame.__init__(self, fenetre,
                       bg=color, width=30,
                       height=50, **kwargs)

        self.pack(fill=BOTH)

        # Création de nos widgets

        self.fenetre_principale = fenetre_principale
        self.text = Text(fenetre, bg='#ebedef')
        self.text.config(state='disabled')
        self.text.pack(
            padx=5, pady=5)

        self.label_commande = Label(fenetre, text="Commande :", bg=color)
        self.label_commande.pack(padx=5, pady=5)
        self.string_entry_commande = StringVar()
        self.entry_commande = Entry(
            fenetre, bg='white', width=50,
            textvariable=self.string_entry_commande)
        self.entry_commande.config(state='disabled')
        self.entry_commande.pack(padx=5, pady=5)
        self.entry_commande.bind("<Return>", self.envoyer_serveur)

        self.b_enoyer = Button(fenetre, text='Envoyer',
                               bg='#5ec3d6', fg="black",
                               disabledforeground="#5ec3d6",
                               command=self.envoyer_serveur)
        self.b_enoyer.pack(padx=5, pady=5)
        self.b_enoyer.config(state='disabled')

        self.frame_ip = Frame(fenetre, bg=color)
        self.frame_ip.pack(side=RIGHT)
        self.label_ip = Label(
            self.frame_ip, text="Adresse IP du serveur :", bg=color)
        self.label_ip.pack(padx=5, pady=5, side=LEFT)
        string_entry_ip = StringVar()
        string_entry_ip.set("127.0.0.1")
        self.entry_ip = Entry(self.frame_ip, width=10, bg='ivory',
                              textvariable=string_entry_ip)
        self.entry_ip.pack(padx=5, pady=5, side=LEFT)

        self.frame_port = Frame(fenetre, bg=color)
        self.frame_port.pack(side=RIGHT)
        self.label_port = Label(
            self.frame_port, text="Port du serveur :", bg=color)
        self.label_port.pack(padx=5, pady=5, side=LEFT)
        string_entry_port = StringVar()
        string_entry_port.set("12800")
        self.entry_port = Entry(self.frame_port,
                                width=10, bg='ivory',
                                textvariable=string_entry_port)
        self.entry_port.pack(padx=5, pady=5, side=LEFT)

        self.frame_button = Frame(fenetre, bg=color)
        self.frame_button.pack(side=RIGHT)
        self.b_connexion = Button(self.frame_button, text='Connexion',
                                  bg="#ef901f", fg="black",
                                  disabledforeground="#ef901f",
                                  command=self.connexion_serveur)
        self.b_connexion.pack(padx=5, pady=5, side=LEFT)
        self.b_deconnexion = Button(self.frame_button, text='Déconnexion',
                                    bg="#9c2724", fg="black",
                                    disabledforeground="#9c2724",
                                    command=self.deconnexion_serveur)
        self.b_deconnexion.config(state='disabled')
        self.b_deconnexion.pack(padx=5, pady=5, side=LEFT)

    def connexion_serveur(self):
        """ On effectue la connexion au serveur
            avec les données entrées par l'utilisateur """

        hote = self.entry_ip.get()
        port = int(self.entry_port.get())

        self.ecraser_dans_cadre(
            "En attente de connexion avec le serveur ...\n")
        # print("En attente de connexion avec le serveur ...")
        # Initialisation de la socket
        self.connexion_avec_serveur = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM)

        # Initialisation de la connexion
        # avec l'adresse du serveur et son
        # port d'écoute

        try:
            self.connexion_avec_serveur.connect((hote, port))
        except ConnectionRefusedError as e:
            self.ecrir_dans_cadre("connexion refusé : \n")
            self.ecrir_dans_cadre(e)
            raise Exception

        self.ecrir_dans_cadre(
            "Connexion établie avec le serveur sur le port {}\n\n".format(
                port))
        self.ecrir_dans_cadre("Tapez 'c' pour commencer à jouer\n")

        self.b_connexion.config(state='disabled')
        self.b_deconnexion.config(state='normal')
        self.b_enoyer.config(state='normal')
        self.entry_ip.config(state='disabled')
        self.entry_port.config(state='disabled')
        self.entry_commande.config(state='normal')

        self.fenetre_principale.configure(background="#ef901f")

        # Un Thread à part est lancer pour pouvoir
        # effectuer la récéption de données sans pour
        # autant bloquer la page
        # Cela ce fait dans un thread en Background
        _thread.start_new_thread(self.recevoir_serveur, ())

    def deconnexion_serveur(self):
        """ On effectue la déconnexion du serveur """

        self.ecrir_dans_cadre("\nDéconnexion avec le serveur\n\n")

        self.b_connexion.config(state='normal')
        self.b_deconnexion.config(state='disabled')
        self.b_enoyer.config(state='disabled')
        self.entry_ip.config(state='normal')
        self.entry_port.config(state='normal')
        self.entry_commande.config(state='disabled')

        self.fenetre_principale.configure(background="#9c2724")

    def envoyer_serveur(self, event=None):
        """ Méthode qui permet l'envoie des données provenant
            de l'utilisateur avec le widget Entry
            vers le serveur qui les traitera par la suite.
            L'utilisateur peut entrer toutes les données
            qu'il veut, elle seront filtré plus tard """

        msg_envoyer = self.entry_commande.get()
        msg_envoyer = msg_envoyer.lower()
        self.entry_commande.delete(0, 'end')
        self.connexion_avec_serveur.send(msg_envoyer.encode())
        if msg_envoyer == "fin":
            self.connexion_avec_serveur.close()
            self.ecrir_dans_cadre("\nAu revoir !\n")

    def recevoir_serveur(self):
        """ Méthode qui reçois les messages
            qui viennent du serveur et
            les affiche dans la fenêtre.
            Cette méthode est lancé dans tun Thread à part
            pour ne pas a avoir a attendre d'envoyer des message
            pour pouvoir en recevoir.
            La récéption ce fait en temps réél de manière
            asynchrone """

        while 1:
            try:
                msg_recu = self.connexion_avec_serveur.recv(1024)
                msg_recu = msg_recu.decode()
                if msg_recu:
                    self.ecraser_dans_cadre(msg_recu)

                    # C'est à nous de jouer
                    if msg_recu == "\n--JOUER\n":
                        self.entry_commande.config(state='normal')
                        self.b_enoyer.config(state='normal')
                    # Ce n'est pas à nous de jouer on attend
                    elif msg_recu == "\n--PASJOUER\n":
                        self.entry_commande.config(state='disabled')
                        self.b_enoyer.config(state='disabled')
                    # Quelqu'un a mis fin à la partie
                    if msg_recu == "\nFin de partie.":
                        print("LLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLLL")
                        self.connexion_avec_serveur.close()
                        self.deconnexion_serveur()
            except socket.error as e:
                self.connexion_avec_serveur.close()
                print("La connexion a était fermée.\n")
                print(e)

    def ecrir_dans_cadre(self, message):
        """ Méthode qui permet d'écrir dans le cadre à
            la suite des données déja existante """

        self.text.config(state='normal')
        self.text.insert(INSERT, message)
        self.text.config(state='disabled')

    def ecraser_dans_cadre(self, message):
        """ Méthode qui permet d'écraser les données
            présente dans le cadre avant d'en rajouter
            d'autre """

        self.text.config(state='normal')
        self.text.delete(1.0, END)
        self.text.insert(INSERT, message)
        self.text.config(state='disabled')


def main():

    root = Tk()
    root.title("Le Labyrinthe")
    # root.resizable(False, False)
    root.geometry("700x600+200+100")
    root.configure(background="#9c2724")
    # Configuration du gestionnaire de grille
    root_frame = Frame(root, bg=color)
    root_frame.pack()

    frame = Frame_Principal(root_frame, root)
    frame.pack()

    root.mainloop()


if __name__ == '__main__':

    main()
