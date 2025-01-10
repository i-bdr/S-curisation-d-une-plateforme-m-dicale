import tkinter as tk
from tkinter import messagebox

class DiffieHelmanConfiguration:
    def __init__(self, root):
        self.root = root
        self.setup_diffie_hellman_window()

    def setup_diffie_hellman_window(self):
        """Configurer la fenêtre pour saisir n et g."""
        self.root.title("Configurer Diffie-Hellman")
        self.root.geometry("300x200")  # Ajuster la taille de la fenêtre

        frame = tk.Frame(self.root)
        frame.pack(pady=10)

        tk.Label(frame, text="Valeur de n:", font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=10)
        self.entry_n = tk.Entry(frame, width=30, bd=2, relief="solid")
        self.entry_n.grid(row=0, column=1, padx=10, pady=5)

        tk.Label(frame, text="Valeur de g:", font=("Arial", 12)).grid(row=1, column=0, sticky="w", padx=10)
        self.entry_g = tk.Entry(frame, width=30, bd=2, relief="solid")
        self.entry_g.grid(row=1, column=1, padx=10, pady=5)

        btn_save_constants = tk.Button(frame, text="Sauvegarder n et g", command=self.save_constants, bg="#4CAF50", fg="white")
        btn_save_constants.grid(row=2, columnspan=2, pady=20)

    def is_prime(self, number):
        """Vérifie si un nombre est premier."""
        if number < 2:
            return False
        for i in range(2, int(number ** 0.5) + 1):
            if number % i == 0:
                return False
        return True

    def save_constants(self):
        """Sauvegarder les valeurs de n et g dans un fichier si les conditions sont respectées."""
        try:
            n_value = int(self.entry_n.get())
            g_value = int(self.entry_g.get())

            # Vérifier si n est premier
            if not self.is_prime(n_value):
                messagebox.showerror("Erreur", "La valeur de n doit être un nombre premier.")
                return

            # Vérifier si 1 <= g <= n - 1
            if not (1 <= g_value <= n_value - 1):
                messagebox.showerror("Erreur", "La valeur de g doit être comprise entre 1 et n - 1.")
                return

            # Sauvegarder n et g dans un fichier si les conditions sont respectées
            with open('constants.txt', 'w') as f:
                f.write(f"{n_value}\n{g_value}")
            messagebox.showinfo("Succès", "Les valeurs de n et g ont été sauvegardées.")
            
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer des valeurs valides pour n et g.")
