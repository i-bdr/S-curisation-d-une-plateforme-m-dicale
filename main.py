import tkinter as tk
from Login import LoginPage  # Assurez-vous d'importer la classe LoginPage

def main():
    root = tk.Tk()  # Créer la fenêtre principale
    app = LoginPage(root)  # Initialiser la page de connexion
    root.mainloop()  # Lancer la boucle principale de Tkinter

if __name__ == '__main__':
    main()
