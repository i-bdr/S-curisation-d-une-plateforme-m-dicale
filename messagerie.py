import subprocess
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

def load_constants():
    try:
        with open('constants.txt', 'r') as f:
            global n, g
            n = int(f.readline().strip())
            g = int(f.readline().strip())
    except Exception as e:
        messagebox.showerror("Erreur", f"Erreur lors du chargement des constantes: {e}")

# Charger les constantes dès le début
load_constants()

def calculate_X_prime():
    try:
        x = int(entry_x.get())
        X_prime = pow(g, x, n)
        entry_X_prime.delete(0, tk.END)
        entry_X_prime.insert(0, str(X_prime))
        messagebox.showinfo("Succès", "X' calculé. Enregistrez-le pour l'envoyer à B.")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer une valeur valide pour x.")

def save_X_prime():
    X_prime = entry_X_prime.get()
    if X_prime:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(X_prime)
            messagebox.showinfo("Succès", f"X' enregistré dans le fichier {file_path}.")
    else:
        messagebox.showerror("Erreur", "Veuillez calculer X' avant de l'enregistrer.")

def load_Y_prime():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "r") as file:
                Y_prime = int(file.read().strip())
                entry_Y_prime.delete(0, tk.END)
                entry_Y_prime.insert(0, str(Y_prime))
            messagebox.showinfo("Succès", "Y' chargé avec succès.")
        except ValueError:
            messagebox.showerror("Erreur", "Le fichier ne contient pas un entier valide pour Y'.")

def calculate_K():
    try:
        x = int(entry_x.get())
        Y_prime = int(entry_Y_prime.get())
        K_A = pow(Y_prime, x, n)  # Calcul de K côté A
        entry_K_A.delete(0, tk.END)
        entry_K_A.insert(0, str(K_A))
        messagebox.showinfo("Succès", "K calculé avec succès. Enregistrez-le pour l'envoyer à B.")
    except ValueError:
        messagebox.showerror("Erreur", "Veuillez entrer une valeur valide pour Y'.")

def save_K_A():
    K_A = entry_K_A.get()
    if K_A:
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(K_A)
            messagebox.showinfo("Succès", f"K calculé enregistré dans le fichier {file_path}.")
    else:
        messagebox.showerror("Erreur", "Veuillez calculer K avant de l'enregistrer.")

def load_K_B():
    file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
    if file_path:
        try:
            with open(file_path, "r") as file:
                K_B = int(file.read().strip())
                entry_K_B.delete(0, tk.END)
                entry_K_B.insert(0, str(K_B))
            # Vérifier si K est identique à celui calculé côté B
            K_A = int(entry_K_A.get())
            if K_A == K_B:
                messagebox.showinfo("Connexion", "Connexion acceptée !")
                entry_message.config(state=tk.NORMAL)  # Activer la saisie du message
                btn_send_message.config(state=tk.NORMAL)  # Activer le bouton d'accès à la discussion
            else:
                messagebox.showerror("Connexion", "Connexion refusée : Les clés ne correspondent pas.")
                entry_message.config(state=tk.DISABLED)  # Désactiver la saisie du message
                btn_send_message.config(state=tk.DISABLED)  # Désactiver le bouton d'accès à la discussion
        except ValueError:
            messagebox.showerror("Erreur", "Le fichier ne contient pas un entier valide pour K de B.")

# Création de la fenêtre principale pour A
root = tk.Tk()
root.title("Messagerie Diffie-Hellman - Authentification mutuelle")

# Valeurs constantes pour n et g affichées
tk.Label(root, text=f"Nombre premier n: {n}").grid(row=0, column=0, sticky=tk.W)
tk.Label(root, text=f"Générateur g: {g}").grid(row=1, column=0, sticky=tk.W)

# Champ pour la clé privée x
tk.Label(root, text="Clé privée x:").grid(row=2, column=0, sticky=tk.W)
entry_x = tk.Entry(root)
entry_x.grid(row=2, column=1)

# Bouton pour calculer X'
btn_calculate_X_prime = tk.Button(root, text="Calculer X'", command=calculate_X_prime)
btn_calculate_X_prime.grid(row=3, column=0, columnspan=2, pady=5)

# Champ pour afficher X'
tk.Label(root, text="X' calculé:").grid(row=4, column=0, sticky=tk.W)
entry_X_prime = tk.Entry(root)
entry_X_prime.grid(row=4, column=1)

# Bouton pour enregistrer X' dans un fichier
btn_save_X_prime = tk.Button(root, text="Enregistrer X'...", command=save_X_prime)
btn_save_X_prime.grid(row=5, column=0, columnspan=2, pady=5)

# Bouton pour charger Y' depuis un fichier
btn_load_Y_prime = tk.Button(root, text="Charger Y'...", command=load_Y_prime)
btn_load_Y_prime.grid(row=6, column=0, columnspan=2, pady=5)

# Champ pour afficher Y' reçu de B
tk.Label(root, text="Y' reçu de B:").grid(row=7, column=0, sticky=tk.W)
entry_Y_prime = tk.Entry(root)
entry_Y_prime.grid(row=7, column=1)

# Bouton pour calculer K et enregistrer K dans un fichier
btn_calculate_K = tk.Button(root, text="Calculer K", command=calculate_K)
btn_calculate_K.grid(row=8, column=0, columnspan=2, pady=5)

# Champ pour afficher K côté A
tk.Label(root, text="K calculé par A:").grid(row=9, column=0, sticky=tk.W)
entry_K_A = tk.Entry(root)
entry_K_A.grid(row=9, column=1)

# Champ pour afficher K reçu de B
tk.Label(root, text="K reçu de B:").grid(row=10, column=0, sticky=tk.W)
entry_K_B = tk.Entry(root)
entry_K_B.grid(row=10, column=1)

# Bouton pour enregistrer K calculé par A
btn_save_K_A = tk.Button(root, text="Enregistrer K...", command=save_K_A)
btn_save_K_A.grid(row=11, column=0, columnspan=2, pady=5)

# Bouton pour charger K de B
btn_load_K_B = tk.Button(root, text="Charger K de B...", command=load_K_B)
btn_load_K_B.grid(row=12, column=0, columnspan=2, pady=5)

# Champ pour le message
tk.Label(root, text="Message à envoyer:").grid(row=13, column=0, sticky=tk.W)
entry_message = tk.Entry(root, state=tk.DISABLED)  # Désactivé par défaut
entry_message.grid(row=13, column=1)

def open_message_page():
    subprocess.run(['python', 'message.py'])  # Assurez-vous que le chemin est correct si nécessaire

def open_message_page():
    subprocess.run(['python', 'message.py'])  # Assurez-vous que le chemin est correct si nécessaire

# Désactiver le bouton d'accès à la discussion par défaut
btn_send_message = tk.Button(root, text="Accéder à la discussion", command=open_message_page, state=tk.DISABLED)
btn_send_message.grid(row=14, column=0, columnspan=2, pady=5)


# Boucle principale de la fenêtre
root.mainloop()
