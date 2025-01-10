import tkinter as tk
from tkinter import messagebox, ttk
import re
import sqlite3
import cryptography
from cryptography.fernet import Fernet
import subprocess
from PIL import Image, ImageTk
import os

class ModernUI:
    @staticmethod
    def setup_styles():
        style = ttk.Style()
        style.theme_use("clam")

        # Configuration générale
        style.configure("TFrame", background="#ffffff")
        style.configure("TLabel", 
                       background="#ffffff",
                       font=("Helvetica Neue", 10))  # Taille de police réduite
        
        # Configuration du Treeview
        style.configure("Treeview",
                       background="white",
                       fieldbackground="white",
                       foreground="#1e293b",
                       font=("Helvetica Neue", 10),  # Taille de police réduite
                       rowheight=30)  # Hauteur de ligne réduite
        
        style.configure("Treeview.Heading",
                       background="#f1f5f9",
                       foreground="#1e293b",
                       font=("Helvetica Neue", 10, "bold"),  # Taille de police réduite
                       relief="flat",
                       padding=5)  # Padding réduit
        
        # Configuration des boutons
        style.configure("Primary.TButton",
                       font=("Helvetica Neue", 10, "bold"),  # Taille de police réduite
                       padding=(10, 5),  # Padding réduit
                       background="#2563eb",
                       foreground="white")

        style.configure("Danger.TButton",
                       font=("Helvetica Neue", 10, "bold"),  # Taille de police réduite
                       padding=(10, 5),  # Padding réduit
                       background="#dc2626",
                       foreground="white")

        style.configure("Success.TButton",
                       font=("Helvetica Neue", 10, "bold"),  # Taille de police réduite
                       padding=(10, 5),  # Padding réduit
                       background="#059669",
                       foreground="white")

        # Configuration des entrées
        style.configure("TEntry",
                       padding=5,  # Padding réduit
                       font=("Helvetica Neue", 10))  # Taille de police réduite

class ModernEntry(ttk.Entry):
    def __init__(self, parent, placeholder="", show=None, **kwargs):
        super().__init__(parent, font=("Helvetica Neue", 10), **kwargs)  # Taille de police réduite
        
        self.placeholder = placeholder
        self.placeholder_color = "#94a3b8"
        self.default_color = "#1e293b"
        self.show = show
        
        self["foreground"] = self.placeholder_color
        
        if placeholder:
            self.insert(0, placeholder)
        
        self.bind("<FocusIn>", self.on_focus_in)
        self.bind("<FocusOut>", self.on_focus_out)

    def on_focus_in(self, event):
        if self.get() == self.placeholder:
            self.delete(0, "end")  # Efface le texte si le placeholder est présent
            self["foreground"] = self.default_color
            if self.show:
                self["show"] = self.show

    def on_focus_out(self, event):
        if not self.get():
            self.insert(0, self.placeholder)
            self["foreground"] = self.placeholder_color
            if self.show:
                self["show"] = ""

    def get(self):
        current_value = super().get()
        if current_value == self.placeholder:
            return ""
        return current_value

# Configuration de la base de données et du chiffrement
key_file = 'key.key'
if os.path.exists(key_file):
    with open(key_file, 'rb') as kf:
        key = kf.read()
else:
    key = Fernet.generate_key()
    with open(key_file, 'wb') as kf:
        kf.write(key)

cipher = Fernet(key)

try:
    conn = sqlite3.connect('DBESante.db')
    cur = conn.cursor()
    
    # Création de la table si elle n'existe pas
    cur.execute('''CREATE TABLE IF NOT EXISTS "user" (
                    "iduser" INTEGER PRIMARY KEY,
                    "mail" TEXT DEFAULT NULL,
                    "motdepasse" TEXT DEFAULT NULL,
                    "nom" TEXT DEFAULT NULL,
                    "prenom" TEXT DEFAULT NULL,
                    "role_id" INTEGER NOT NULL,
                    "date_naissance" TEXT,
                    FOREIGN KEY("role_id") REFERENCES "role"("idrole")
                )''')
    conn.commit()
except sqlite3.Error as e:
    messagebox.showerror("Erreur de connexion", f"Erreur lors de la connexion à la base de données: {e}")
    exit()

class User:
    def __init__(self, nom, prenom, email, password, role_id, date_naissance):
        self.nom = nom
        self.prenom = prenom
        self.email = email
        self.password = self.encrypt_password(password)
        self.role_id = role_id
        self.date_naissance = date_naissance

    @staticmethod
    def encrypt_password(password):
        return cipher.encrypt(password.encode())

    @staticmethod
    def decrypt_password(encrypted_password):
        return cipher.decrypt(encrypted_password).decode()

class Application:
    def __init__(self, root):
        self.root = root
        self.setup_window()
        self.create_widgets()
        self.setup_bindings()

    def setup_window(self):
        self.root.title("Gestion des Utilisateurs - E-Santé")
        self.root.geometry("800x600")  # Taille de la fenêtre réduite
        self.root.configure(bg="#ffffff")
        ModernUI.setup_styles()

    def create_widgets(self):
        # Main container
        self.main_container = ttk.Frame(self.root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)  # Padding réduit

        # Header
        self.create_header()

        # Content area
        self.content_frame = ttk.Frame(self.main_container)
        self.content_frame.pack(fill=tk.BOTH, expand=True, pady=10)

        # Form and list
        self.create_form()
        self.create_user_list()

        # Action buttons
        self.create_action_buttons()

    def create_header(self):
        header_frame = ttk.Frame(self.main_container)
        header_frame.pack(fill=tk.X, pady=(0, 10))

        try:
            image = Image.open("logo_esante.png")
            image = image.resize((100, 100), Image.LANCZOS)  # Taille de l'image réduite
            self.logo = ImageTk.PhotoImage(image)
            logo_label = ttk.Label(header_frame, image=self.logo)
            logo_label.pack(side=tk.LEFT)
        except Exception as e:
            print(f"Erreur lors du chargement de l'image: {e}")

        title = ttk.Label(header_frame,
                         text="Gestion des Utilisateurs",
                         font=("Helvetica Neue", 20, "bold"),  # Taille de police réduite
                         foreground="#1e293b")
        title.pack(side=tk.LEFT, padx=10)

    def create_form(self):
        form_frame = ttk.Frame(self.content_frame)
        form_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Form fields configuration
        self.entries = {
            "nom": ("Nom", ""),
            "prenom": ("Prénom", ""),
            "email": ("Email", ""),
            "date_naissance": ("Date de naissance", "YYYY-MM-DD"),
            "password1": ("Mot de passe", "", "*"),
            "password2": ("Confirmer le mot de passe", "", "*")
        }

        for key, (label_text, placeholder, *show) in self.entries.items():
            frame = ttk.Frame(form_frame)
            frame.pack(fill=tk.X, pady=5)

            label = ttk.Label(frame,
                            text=label_text,
                            font=("Helvetica Neue", 8, "bold"))  # Taille de police réduite
            label.pack(anchor=tk.W, pady=(0, 3))

            entry = ModernEntry(frame,
                              placeholder=placeholder,
                              show=show[0] if show else None)
            entry.pack(fill=tk.X, ipady=3)
            setattr(self, f"entry_{key}", entry)

        # Role combobox
        role_frame = ttk.Frame(form_frame)
        role_frame.pack(fill=tk.X, pady=3)

        role_label = ttk.Label(role_frame,
                             text="Rôle",
                             font=("Helvetica Neue", 5, "bold"))  # Taille de police réduite
        role_label.pack(anchor=tk.W, pady=(0, 3))

        self.role_combobox = ttk.Combobox(role_frame,
                                         font=("Helvetica Neue", 5),
                                         state="readonly")
        self.role_combobox.pack(fill=tk.X, ipady=3)
        
        self.update_roles()

        # Validation button
        validate_button = ttk.Button(form_frame, text="Valider", command=self.add_user, style="Success.TButton")
        validate_button.pack(pady=3)

    def create_user_list(self):
        list_frame = ttk.Frame(self.content_frame)
        list_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        columns = ("nom", "prenom", "email", "motdepasse", "date_naissance")
        self.user_list = ttk.Treeview(list_frame,
                                     columns=columns,
                                     show="headings",
                                     style="Treeview")

        headings = {
            "nom": "Nom",
            "prenom": "Prénom",
            "email": "Email",
            "motdepasse": "Mot de passe",
            "date_naissance": "Date de naissance"
        }

        for col, heading in headings.items():
            self.user_list.heading(col, text=heading)
            self.user_list.column(col, width=120, anchor="center")  # Largeur de colonne réduite

        scrollbar = ttk.Scrollbar(list_frame,
                                orient=tk.VERTICAL,
                                command=self.user_list.yview)
        self.user_list.configure(yscrollcommand=scrollbar.set)

        self.user_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.user_list.tag_configure("oddrow", background="#f8fafc")
        self.user_list.tag_configure("evenrow", background="#ffffff")

        self.update_user_list()

    def create_action_buttons(self):
        button_frame = ttk.Frame(self.main_container)
        button_frame.pack(pady=20)

        ttk.Button(button_frame,
                  text="Ajouter Utilisateur",
                  command=self.add_user,
                  style="Success.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                  text="Modifier",
                  command=self.modify_user,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                  text="Supprimer",
                  command=self.delete_user,
                  style="Danger.TButton").pack(side=tk.LEFT, padx=5)

        ttk.Button(button_frame,
                  text="Revenir",
                  command=self.back_home,
                  style="Primary.TButton").pack(side=tk.LEFT, padx=5)

        # Save button (hidden by default)
        self.save_button = ttk.Button(self.main_container,
                                    text="Sauvegarder les modifications",
                                    style="Success.TButton")
        self.save_button.pack_forget()

    def update_roles(self):
        try:
            cur.execute("SELECT idrole, rolename FROM role")
            roles = cur.fetchall()
            self.role_combobox['values'] = [role[1] for role in roles]
            return roles
        except sqlite3.Error as e:
            messagebox.showerror("Erreur SQL", f"Erreur lors de la récupération des rôles: {e}")
            return []

    def update_user_list(self):
        for item in self.user_list.get_children():
            self.user_list.delete(item)
        
        try:
            cur.execute("SELECT nom, prenom, mail, motdepasse, date_naissance FROM user")
            rows = cur.fetchall()
            for index, row in enumerate(rows):
                try:
                    decrypted_password = User.decrypt_password(row[3])
                except cryptography.fernet.InvalidToken:
                    decrypted_password = "Mot de passe invalide"
                
                tag = "evenrow" if index % 2 == 0 else "oddrow"
                self.user_list.insert("", "end",
                                    values=(row[0], row[1], row[2], decrypted_password, row[4]),
                                    tags=(tag,))
        except sqlite3.Error as e:
            messagebox.showerror("Erreur SQL", f"Erreur lors de la récupération des utilisateurs: {e}")

    def add_user(self):
        nom = self.entry_nom.get()
        prenom = self.entry_prenom.get()
        email = self.entry_email.get()
        password1 = self.entry_password1.get()
        password2 = self.entry_password2.get()
        selected_role = self.role_combobox.get()
        date_naissance = self.entry_date_naissance.get()

        # Validation
        if not all([nom, prenom, email, password1, password2, selected_role, date_naissance]):
            messagebox.showwarning("Entrée manquante", "Veuillez remplir tous les champs.")
            return

        if not self.is_valid_email(email):
            messagebox.showwarning("E-mail invalide", "Veuillez entrer une adresse e-mail valide.")
            return

        is_valid, msg = self.is_valid_password(password1)
        if not is_valid:
            messagebox.showwarning("Mot de passe invalide", msg)
            return

        if password1 != password2:
            messagebox.showwarning("Mot de passe", "Les mots de passe ne correspondent pas.")
            return

        if not re.match(r"\d{4}-\d{2}-\d{2}", date_naissance):
            messagebox.showwarning("Date de naissance", "Format de date invalide (YYYY-MM-DD).")
            return

        # Récupération de l'ID du rôle
        roles = self.update_roles()
        role_id = next((role[0] for role in roles if role[1] == selected_role), None)

        if role_id is None:
            messagebox.showwarning("Erreur", "Rôle sélectionné invalide.")
            return

        try:
            encrypted_password = User.encrypt_password(password1)
            cur.execute(""" 
                INSERT INTO user (mail, motdepasse, nom, prenom, role_id, date_naissance) 
                VALUES (?, ?, ?, ?, ?, ?)
            """, (email, encrypted_password, nom, prenom, role_id, date_naissance))
            conn.commit()
            messagebox.showinfo("Succès", "Utilisateur ajouté avec succès.")
            self.clear_entries()
            self.update_user_list()
        except sqlite3.Error as e:
            messagebox.showerror("Erreur SQL", f"Erreur lors de l'ajout de l'utilisateur: {e}")

    def modify_user(self):
        selected_item = self.user_list.selection()
        if not selected_item:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un utilisateur à modifier.")
            return

        # Récupérer les données de l'utilisateur sélectionné
        item_values = self.user_list.item(selected_item)['values']
        nom, prenom, email, motdepasse, date_naissance = item_values

        # Remplir les champs
        self.entry_nom.delete(0, tk.END)
        self.entry_nom.insert(0, nom)
        
        self.entry_prenom.delete(0, tk.END)
        self.entry_prenom.insert(0, prenom)
        
        self.entry_email.delete(0, tk.END)
        self.entry_email.insert(0, email)
        
        self.entry_date_naissance.delete(0, tk.END)
        self.entry_date_naissance.insert(0, date_naissance)
        
        self.entry_password1.delete(0, tk.END)
        self.entry_password2.delete(0, tk.END)

        # Afficher le bouton de sauvegarde
        self.save_button.configure(command=lambda: self.save_modifications(email))
        self.save_button.pack(pady=10)

    def save_modifications(self, original_email):
        # Récupérer les nouvelles valeurs
        new_nom = self.entry_nom.get()
        new_prenom = self.entry_prenom.get()
        new_email = self.entry_email.get()
        new_password1 = self.entry_password1.get()
        new_password2 = self.entry_password2.get()
        new_date_naissance = self.entry_date_naissance.get()
        selected_role = self.role_combobox.get()

        # Validation
        if not all([new_nom, new_prenom, new_email, selected_role, new_date_naissance]):
            messagebox.showwarning("Entrée manquante", "Veuillez remplir tous les champs obligatoires.")
            return

        if not self.is_valid_email(new_email):
            messagebox.showwarning("E-mail invalide", "Veuillez entrer une adresse e-mail valide.")
            return

        if new_password1:
            if new_password1 != new_password2:
                messagebox.showwarning("Mot de passe", "Les mots de passe ne correspondent pas.")
                return
            is_valid, msg = self.is_valid_password(new_password1)
            if not is_valid:
                messagebox.showwarning("Mot de passe invalide", msg)
                return

        if not re.match(r"\d{4}-\d{2}-\d{2}", new_date_naissance):
            messagebox.showwarning("Date de naissance", "Format de date invalide (YYYY-MM-DD).")
            return

        # Récupérer l'ID du rôle
        roles = self.update_roles()
        role_id = next((role[0] for role in roles if role[1] == selected_role), None)

        if role_id is None:
            messagebox.showwarning("Erreur", "Rôle sélectionné invalide.")
            return

        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir modifier cet utilisateur ?"):
            try:
                if new_password1:
                    encrypted_password = User.encrypt_password(new_password1)
                    cur.execute("""
                        UPDATE user 
                        SET mail=?, motdepasse=?, nom=?, prenom=?, date_naissance=?, role_id=? 
                        WHERE mail=?
                    """, (new_email, encrypted_password, new_nom, new_prenom, new_date_naissance, role_id, original_email))
                else:
                    cur.execute("""
                        UPDATE user 
                        SET mail=?, nom=?, prenom=?, date_naissance=?, role_id=? 
                        WHERE mail=?
                    """, (new_email, new_nom, new_prenom, new_date_naissance, role_id, original_email))

                conn.commit()
                messagebox.showinfo("Succès", "Utilisateur modifié avec succès.")
                self.update_user_list()
                self.clear_entries()
                self.save_button.pack_forget()
            
            except sqlite3.Error as e:
                messagebox.showerror("Erreur SQL", f"Erreur lors de la modification de l'utilisateur: {e}")

    def delete_user(self):
        selected_item = self.user_list.selection()
        if not selected_item:
            messagebox.showwarning("Aucune sélection", "Veuillez sélectionner un utilisateur à supprimer.")
            return
        
        if messagebox.askyesno("Confirmation", "Êtes-vous sûr de vouloir supprimer cet utilisateur ?"):
            try:
                email = self.user_list.item(selected_item)['values'][2]
                cur.execute("DELETE FROM user WHERE mail=?", (email,))
                conn.commit()
                messagebox.showinfo("Succès", "Utilisateur supprimé avec succès.")
                self.update_user_list()
            except sqlite3.Error as e:
                messagebox.showerror("Erreur SQL", f"Erreur lors de la suppression de l'utilisateur: {e}")

    def back_home(self):
        self.root.destroy()
        subprocess.Popen(["python", "home_page.py"])

    def clear_entries(self):
        for key in self.entries.keys():
            entry = getattr(self, f"entry_{key}")
            entry.delete(0, tk.END)
        self.role_combobox.set('')

    def setup_bindings(self):
        self.root.bind("<F11>", self.toggle_fullscreen)
        self.root.bind("<Escape>", self.end_fullscreen)

    def toggle_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", not self.root.attributes("-fullscreen"))

    def end_fullscreen(self, event=None):
        self.root.attributes("-fullscreen", False)

    @staticmethod
    def is_valid_email(email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None

    @staticmethod
    def is_valid_password(password):
        if len(password) < 8:
            return False, "Le mot de passe doit comporter au moins 8 caractères."
        if not re.search(r"[A-Z]", password):
            return False, "Le mot de passe doit comporter au moins une lettre majuscule."
        if not re.search(r"[a-z]", password):
            return False, "Le mot de passe doit comporter au moins une lettre minuscule."
        if not re.search(r"[0-9]", password):
            return False, "Le mot de passe doit comporter au moins un chiffre."
        if not re.search(r"[@$!%*?&]", password):
            return False, "Le mot de passe doit comporter au moins un caractère spécial (@$!%*?&)."
        return True, ""

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.mainloop()
    conn.close()
