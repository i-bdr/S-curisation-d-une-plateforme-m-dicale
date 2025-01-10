import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import Listbox
from assets.style import ModernButton, setup_styles
from gestion_inteface.getAllRessources import get_all_ressources
from user_session import UserSession
from gestion_inteface.getRessourceDetail import get_ressource_detail

class AccessInterface:

    def __init__(self, root, role):
        self.user_session = UserSession.get_instance()
        user_data = self.user_session.get_user()
        
        self.user_id = 1
        self.root = root
        self.role = role
        self.root.title("Gestion des Accès")
        self.root.geometry("1200x800")
        self.root.configure(bg="#ffffff")
        
        setup_styles()
        self.create_layout()


    def create_layout(self):
        # En-tête
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill="x", padx=0, pady=0)
        
        header_content = ttk.Frame(header, style="Header.TFrame")
        header_content.pack(fill="x", padx=40, pady=20)
        
        # Titre et description
        title_frame = ttk.Frame(header_content, style="Header.TFrame")
        title_frame.pack(side="left")

        title = tk.Label(title_frame,
                        text="Gestion des Ressources",
                        font=("Segoe UI", 24, "bold"),
                        bg="#1e293b",
                        fg="white")
        title.pack(anchor="w")

        description = tk.Label(title_frame,
                             text=f"Gérez vos ressources et les accès - {self.role.capitalize()}",
                             font=("Segoe UI", 14),
                             bg="#1e293b",
                             fg="#94a3b8")
        description.pack(anchor="w", pady=(5, 0))

        # Contenu principal
        main_content = ttk.Frame(self.root, style="Main.TFrame")
        main_content.pack(fill="both", expand=True, padx=40, pady=30)

        # Boutons d'action
        actions_frame = tk.Frame(main_content, bg="#ffffff")  # Utilisez tk.Frame au lieu de ttk.Frame
        actions_frame.pack(fill="x", pady=(0, 20))
        self.add_button = ModernButton(
            actions_frame,
            text="Ajouter",
            command=lambda: self.open_create_dossier_medical(),
            width=300,
            bg_color="#2563eb"
        )
        self.add_button.pack(side="left", padx=10)

        self.view_button = ModernButton(
            actions_frame,
            text="Voir les détails",
            command=lambda: self.show_resource_info(),
            width=300,
            bg_color="#1e293b"
        )
        self.view_button.pack(side="left", padx=10)

        # Table des ressources
        table_frame = ttk.Frame(main_content, style="Main.TFrame")
        table_frame.pack(fill="both", expand=True)

        # Création de la table
        self.tree = ttk.Treeview(
            table_frame,
            columns=("Nom", "Description", "Politique"),
            show="headings",
            style="Treeview"
        )

        # Configuration des colonnes
        columns = {
            "Nom": (300, "w"),
            "Description": (500, "w"),
            "Politique": (200, "center")
        }

        for col, (width, anchor) in columns.items():
            self.tree.heading(col, text=col, anchor="center")
            self.tree.column(col, width=width, anchor=anchor)

        # Scrollbar
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack des éléments
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Remplir la table
        self.populate_table()

    def show_resource_info(self):
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner une ressource.")
            return

        item = self.tree.item(selected_item, "values")
        res_id, res_name, res_policy = item

        # Vérifier si l'utilisateur a le droit "read"
        if "read" not in res_policy.lower() and "owner" not in res_policy.lower():
            messagebox.showwarning("Accès refusé", "Vous n'avez pas les droits nécessaires pour voir les détails de cette ressource.")
            return

        # Récupérer les détails du dossier médical
        data = get_ressource_detail(res_id)
        if not data:
            messagebox.showwarning("Erreur", "Aucun détail trouvé pour cette ressource.")
            return

        # Création de la fenêtre de détails
        detail_window = tk.Toplevel(self.root)
        detail_window.title(f"Détails de la ressource {res_name}")
        detail_window.geometry("800x600")
        detail_window.configure(bg="#ffffff")

        # En-tête
        header = ttk.Frame(detail_window, style="Header.TFrame")
        header.pack(fill="x")

        header_content = ttk.Frame(header, style="Header.TFrame")
        header_content.pack(fill="x", padx=40, pady=20)

        title = tk.Label(header_content,
                        text=f"Détails du dossier médical : {res_name}",
                        font=("Segoe UI", 24, "bold"),
                        bg="#1e293b",
                        fg="white")
        title.pack(anchor="w")

        # Contenu principal
        content = ttk.Frame(detail_window, style="Main.TFrame")
        content.pack(fill="both", expand=True, padx=40, pady=30)

        # Afficher les détails du dossier médical
        details = data[0]  # Récupérer la première ligne de données (supposons qu'il n'y a qu'une seule ligne)
        labels = [
            ("ID du dossier", details[0]),
            ("ID du patient", details[1]),
            ("Date de création", details[2]),
            ("Pathologies", details[3]),
            ("Traitements", details[4]),
            ("Allergies", details[5]),
            ("Antécédents", details[6]),
            ("Observations", details[7]),
            ("Dernière modification", details[8])
        ]

        # Dictionnaire pour stocker les champs modifiables
        self.editable_fields = {}

        for label, value in labels:
            frame = ttk.Frame(content, style="Main.TFrame")
            frame.pack(fill="x", pady=5)

            tk.Label(frame,
                    text=label,
                    font=("Segoe UI", 12, "bold"),
                    bg="#ffffff",
                    fg="#64748b").pack(anchor="w")

            # Si l'utilisateur a le droit "write", rendre les champs modifiables
            if "write" in res_policy.lower() and label in ["Pathologies", "Traitements", "Allergies", "Antécédents", "Observations"]:
                entry = tk.Entry(frame, font=("Segoe UI", 14), bg="#ffffff", fg="#1e293b")
                entry.insert(0, value)
                entry.pack(anchor="w", pady=(5, 0), fill="x")
                self.editable_fields[label] = entry
            else:
                tk.Label(frame,
                        text=value,
                        font=("Segoe UI", 14),
                        bg="#ffffff",
                        fg="#1e293b").pack(anchor="w", pady=(5, 0))

        # Bouton de sauvegarde si l'utilisateur a le droit "write"
        if "write" in res_policy.lower():
            save_button = ttk.Button(
                content,
                text="Enregistrer les modifications",
                command=lambda: self.save_changes(res_id),
                style="TButton"
            )
            save_button.pack(pady=20)

        # Section des politiques (si propriétaire)
        if res_policy == "owner":
            policy_frame = ttk.Frame(content, style="Main.TFrame")
            policy_frame.pack(fill="both", expand=True, pady=(20, 0))

            tk.Label(policy_frame,
                    text="Gestion des accès",
                    font=("Segoe UI", 18, "bold"),
                    bg="#ffffff",
                    fg="#1e293b").pack(anchor="w", pady=(0, 20))

            # Table des politiques
            policy_tree = ttk.Treeview(
                policy_frame,
                columns=("Utilisateur", "Politique"),
                show="headings",
                style="Treeview"
            )

            policy_tree.heading("Utilisateur", text="Utilisateur", anchor="center")
            policy_tree.heading("Politique", text="Politique", anchor="center")

            policy_tree.column("Utilisateur", width=300)
            policy_tree.column("Politique", width=300)

            policy_tree.pack(fill="both", expand=True)

            # Bouton de modification
            modify_button = ttk.Button(
                policy_frame,
                text="Modifier les accès",
                command=lambda: self.modify_policy(policy_tree),
                style="TButton"
            )
            modify_button.pack(pady=20)

    def save_changes(self, res_id):
        # Récupérer les valeurs modifiées
        updated_data = {
            "pathologies": self.editable_fields["Pathologies"].get(),
            "traitements": self.editable_fields["Traitements"].get(),
            "allergies": self.editable_fields["Allergies"].get(),
            "antecedents": self.editable_fields["Antécédents"].get(),
            "observations": self.editable_fields["Observations"].get()
        }

        # Mettre à jour la base de données
        try:
            from helpers.db_connection import connect

            conn = connect()
            cur = conn.cursor()
            cur.execute("""
                UPDATE dossier_medical
                SET pathologies = ?, traitements = ?, allergies = ?, antecedents = ?, observations = ?
                WHERE id_dossier = ?
            """, (updated_data["pathologies"], updated_data["traitements"], updated_data["allergies"],
                updated_data["antecedents"], updated_data["observations"], res_id))
            conn.commit()
            conn.close()
            messagebox.showinfo("Succès", "Les modifications ont été enregistrées avec succès.")
        except conn.Error as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour : {e}")
    def open_create_dossier_medical(self):
        import createDossierMedical
        createDossierMedical(self.root)
   

    def submit_new_resource(self, entries):
        # Récupérer les politiques sélectionnées
        selected_policies = [entries["Politique"].get(i) for i in entries["Politique"].curselection()]
        # Validation de l'entrée
        resource_name = entries["Nom"].get()
        description = entries["Description"].get()

        if not resource_name or not description or not selected_policies:
            messagebox.showerror("Erreur", "Tous les champs sont requis.")
            return

        # Ajouter la ressource à la base de données ou traitement
        messagebox.showinfo("Succès", "Ressource ajoutée avec succès!")
        self.populate_table()

    def populate_table(self):
        # Effacer la table existante avant de la remplir
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Remplir la table avec des données d'exemple
        for res in get_all_ressources(3):
            self.tree.insert("", "end", values=res)


    def modify_policy(self, policy_tree):
        # Logique pour modifier les politiques
        pass


def run_gui():
    root = tk.Tk()
    app = AccessInterface(root, role="admin")
    root.mainloop()


if __name__ == "__main__":
    run_gui()
