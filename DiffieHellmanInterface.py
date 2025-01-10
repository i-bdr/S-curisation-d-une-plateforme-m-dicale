import time
import tkinter as tk
from tkinter import messagebox, filedialog

class DiffieHellmanInterface:
    def __init__(self, root, on_success_callback, role):
        self.root = root
        self.total_execution_time = 0  # Initialisation du temps total d'exécution
        self.start_time = time.time()   # Temps d'exécution cumulatif
        self.on_success_callback = on_success_callback
        self.role = role
        
        # Initialisation de n et g pour éviter des erreurs avant leur chargement
        self.n = 23
        self.g = 5

        # Configure la fenêtre principale
        self.root.title("Authentification Diffie-Hellman")
        self.root.geometry("600x600")
        self.root.configure(bg="#2c3e50")  # Fond sombre pour un look moderne

        # Configuration des styles
        self.label_font = ("Arial", 12, "bold")
        self.entry_font = ("Arial", 11)
        self.button_font = ("Arial", 11)
        self.bg_color = "#34495e"
        self.fg_color = "#ecf0f1"

        # Création des Labels et des Entrées
        self.create_label_entry("Nombre premier n (identifiant de sécurité):", 0, str(self.n), "n")
        self.create_label_entry("Générateur g (clé d'authentification):", 1, str(self.g), "g")
        self.create_label_entry("Clé privée (numéro de dossier):", 3, "", "x")
        self.create_label_entry("Dossier calculé (référence générée):", 5, "", "X_prime")
        self.create_label_entry("Référence externe reçue:", 8, "", "Y_prime")
        self.create_label_entry("Clé calculée pour le dossier:", 10, "", "K_A")
        self.create_label_entry("Clé externe chargée:", 12, "", "K_B", state="readonly")

        # Création des Boutons
        self.create_button("Charger n et g", self.load_constants_from_file, 2)
        self.create_button("Générer la référence", self.calculate_X_prime, 4)
        self.create_button("Enregistrer la référence...", self.save_X_prime, 6)
        self.create_button("Charger une référence externe...", self.load_Y_prime, 7)
        self.create_button("Calculer la clé pour le dossier", self.calculate_K, 9)
        self.create_button("Enregistrer la clé...", self.save_K_A, 11)
        self.create_button("Charger une clé externe...", self.load_K_B, 13)

    def create_label_entry(self, text, row, default_value, attr_name, state="normal"):
        """Fonction d'aide pour créer un label et une entrée avec un design moderne."""
        label = tk.Label(self.root, text=text, bg=self.bg_color, fg=self.fg_color, font=self.label_font)
        label.grid(row=row, column=0, sticky=tk.W, padx=10, pady=5)

        entry = tk.Entry(self.root, font=self.entry_font, state=state)
        entry.insert(0, default_value)
        entry.grid(row=row, column=1, padx=10, pady=5, sticky=tk.W)
        
        # Sauvegarder l'entrée dans self par le nom de l'attribut
        setattr(self, f"entry_{attr_name}", entry)

    def create_button(self, text, command, row):
        """Fonction d'aide pour créer un bouton stylisé."""
        button = tk.Button(self.root, text=text, command=command, font=self.button_font, 
                           bg="#3498db", fg="#ecf0f1", activebackground="#2980b9", activeforeground="white")
        button.grid(row=row, column=0, columnspan=2, padx=10, pady=10, sticky=tk.EW)

    def load_constants_from_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    self.n = int(f.readline().strip())
                    self.g = int(f.readline().strip())
                self.entry_n.delete(0, tk.END)
                self.entry_n.insert(0, str(self.n))
                self.entry_g.delete(0, tk.END)
                self.entry_g.insert(0, str(self.g))
                messagebox.showinfo("Succès", "Constantes n et g chargées avec succès.")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors du chargement des constantes: {e}")

    def calculate_X_prime(self):
        if not hasattr(self, 'n') or not hasattr(self, 'g'):
            messagebox.showerror("Erreur", "Les constantes n et g doivent être chargées avant de générer la référence.")
            return

        try:
            start_time = time.time()
            x = int(self.entry_x.get())
            
            # Calcul de X' en utilisant n, g et x
            X_prime = pow(self.g, x, self.n)
            elapsed = time.time() - start_time
            self.total_execution_time += elapsed

            # Mise à jour du champ d'entrée X_prime avec la valeur calculée
            self.entry_X_prime.delete(0, tk.END)  # Effacer la valeur précédente
            self.entry_X_prime.insert(0, str(X_prime))  # Afficher la nouvelle valeur

            # Afficher un message d'information avec le temps d'exécution
            messagebox.showinfo("Succès", f"X' calculé en {elapsed:.6f} secondes. Enregistrez-le pour l'envoyer à B.")

        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une valeur valide pour x.")


    def save_X_prime(self):
        X_prime = self.entry_X_prime.get()
        if X_prime:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, "w") as file:
                    file.write(X_prime)
                messagebox.showinfo("Succès", f"X' enregistré dans le fichier {file_path}.")
        else:
            messagebox.showerror("Erreur", "Veuillez calculer X' avant de l'enregistrer.")

    def load_Y_prime(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    Y_prime = int(file.read().strip())
                    self.entry_Y_prime.delete(0, tk.END)
                    self.entry_Y_prime.insert(0, str(Y_prime))
                messagebox.showinfo("Succès", "Y' chargé avec succès.")
            except ValueError:
                messagebox.showerror("Erreur", "Le fichier ne contient pas un entier valide pour Y'.")

    def calculate_K(self):
        try:
            x = int(self.entry_x.get())
            Y_prime = int(self.entry_Y_prime.get())
            K_A = pow(Y_prime, x, self.n)  # Calcul de K côté A
            self.entry_K_A.delete(0, tk.END)
            self.entry_K_A.insert(0, str(K_A))
            messagebox.showinfo("Succès", "K calculé avec succès. Enregistrez-le pour l'envoyer à B.")
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer une valeur valide pour Y'.")

    def save_K_A(self):
        K_A = self.entry_K_A.get()
        if K_A:
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, "w") as file:
                    file.write(K_A)
                messagebox.showinfo("Succès", f"K calculé enregistré dans le fichier {file_path}.")
        else:
            messagebox.showerror("Erreur", "Veuillez calculer K avant de l'enregistrer.")

    def load_K_B(self):
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
        if file_path:
            try:
                with open(file_path, "r") as file:
                    K_B = int(file.read().strip())
                    self.entry_K_B.delete(0, tk.END)
                    self.entry_K_B.insert(0, str(K_B))
                
                # Vérifier si K est identique à celui calculé côté B
                K_A = int(self.entry_K_A.get())
                if K_A == K_B:
                    # Calculer et afficher le temps total d'exécution
                    self.total_execution_time = time.time() - self.start_time
                    messagebox.showinfo("Connexion", f"Connexion acceptée!\nTemps total d'exécution : {self.total_execution_time:.6f} secondes.")
                    self.on_success_callback()
                    self.root.destroy()
                else:
                    messagebox.showerror("Connexion", "Connexion refusée : Les clés ne correspondent pas.")
            except ValueError:
                messagebox.showerror("Erreur", "Le fichier ne contient pas un entier valide pour K de B.")
