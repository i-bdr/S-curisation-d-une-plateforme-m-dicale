import sys
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from PIL import Image, ImageTk
import socket
from Connection import connect
from user_session import UserSession

def setup_database():
    """Create the demande table if it doesn't exist"""
    connection = connect()
    if connection:
        try:
            cursor = connection.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS demande (
                    id_demande INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_dossier INTEGER NOT NULL,
                    id_user INTEGER NOT NULL,
                    date_demande DATETIME DEFAULT CURRENT_TIMESTAMP,
                    politiques TEXT NOT NULL,
                    etat VARCHAR(20) DEFAULT 'En attente',
                    FOREIGN KEY (id_dossier) REFERENCES dossier_medical(id_dossier),
                    FOREIGN KEY (id_user) REFERENCES user(iduser)
                )
            """)
            
            connection.commit()
            print("Table demande créée ou déjà existante")
            
        except Exception as e:
            print(f"Erreur lors de la création de la table: {str(e)}")
        finally:
            cursor.close()
            connection.close()

class ModernTable(ttk.Treeview):
    def __init__(self, parent, columns, **kwargs):
        super().__init__(parent, columns=columns, show="headings", style="Modern.Treeview", **kwargs)
        
        # Configuration du style
        style = ttk.Style()
        style.configure("Modern.Treeview",
                       background="#ffffff",
                       foreground="#1e293b",
                       rowheight=45,
                       fieldbackground="#ffffff",
                       borderwidth=0,
                       font=("Helvetica Neue", 11))
        
        style.configure("Modern.Treeview.Heading",
                       background="#f8fafc",
                       foreground="#64748b",
                       padding=(10, 10),
                       font=("Helvetica Neue", 12, "bold"))
        
        style.map("Modern.Treeview",
                 background=[("selected", "#e2e8f0")],
                 foreground=[("selected", "#1e293b")])

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=40, bg_color="#2563eb", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=parent["bg"], highlightthickness=0, height=height, width=width)
        self.text = text
        self.command = command
        
        self.default_color = bg_color
        self.hover_color = self.adjust_color(bg_color, -20)
        self.active_color = self.adjust_color(bg_color, -40)
        self.current_color = self.default_color
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw()

    def adjust_color(self, color, amount):
        hex_color = color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)
        
    def draw(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        if not width or not height:
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
        
        radius = 8
        self.create_rounded_rect(0, 0, width, height, radius, self.current_color)
        self.create_text(width/2, height/2, text=self.text, fill="white", 
                        font=("Helvetica Neue", 12, "bold"))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, color):
        points = [
            x1+radius, y1,
            x2-radius, y1,
            x2, y1,
            x2, y1+radius,
            x2, y2-radius,
            x2, y2,
            x2-radius, y2,
            x1+radius, y2,
            x1, y2,
            x1, y2-radius,
            x1, y1+radius,
            x1, y1
        ]
        return self.create_polygon(points, smooth=True, fill=color)

    def on_enter(self, event):
        self.current_color = self.hover_color
        self.draw()

    def on_leave(self, event):
        self.current_color = self.default_color
        self.draw()

    def on_press(self, event):
        self.current_color = self.active_color
        self.draw()

    def on_release(self, event):
        if self.command:
            self.command()
        self.current_color = self.default_color
        self.draw()

class AccessPage(tk.Frame):
    def __init__(self, root):
        super().__init__(root, bg='#ffffff')
        self.root = root
        iduser, nom, prenom, role = sys.argv[1:5]

        # Initialisez user_session dans une variable d'instance
        self.user_session = UserSession.get_instance()
        self.user_session.set_user({
            "iduser": iduser,
            "nom": nom,
            "prenom": prenom,
            "role": role
        })

        print(f"Utilisateur dans AccessPage : {self.user_session.get_user()}")
        self.current_filter = "Mes demandes"

        
        # Initialisation de la base de données
        setup_database()
        self.pack(fill='both', expand=True)
        self.setup_ui()
        self.load_data()
        self.schedule_refresh()

    def setup_ui(self):
        self.create_header()
        self.create_main_content()
        self.create_filters()
        self.create_table()
        self.create_status_bar()

    def create_header(self):
        header_frame = tk.Frame(self, bg='#ffffff')
        header_frame.pack(fill='x', padx=40, pady=(40, 20))

        title_label = tk.Label(header_frame,
                             text="Tableau des Demandes d'Accès",
                             font=("Helvetica Neue", 28, "bold"),
                             bg='#ffffff',
                             fg='#1e293b')
        title_label.pack(side='left')

    def create_main_content(self):
        self.content_frame = tk.Frame(self, bg='#ffffff')
        self.content_frame.pack(fill='both', expand=True, padx=40)

    def create_filters(self):
        filters_frame = tk.Frame(self.content_frame, bg='#ffffff')
        filters_frame.pack(fill='x', pady=(0, 20))

        # Search
        search_frame = tk.Frame(filters_frame, bg='#ffffff')
        search_frame.pack(side='left')

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(search_frame,
                              textvariable=self.search_var,
                              font=("Helvetica Neue", 12),
                              bd=1,
                              relief='solid',
                              width=30)
        search_entry.pack(side='left', padx=(0, 10))
        search_entry.insert(0, "Rechercher...")
        search_entry.bind('<KeyRelease>', self.on_search)

        # Filter buttons
        buttons = [
            ("Mes demandes", "#3b82f6"),
            ("Demandes sur mes dossiers", "#f59e0b")
        ]

        for text, color in buttons:
            ModernButton(filters_frame, text=text, command=lambda t=text: self.filter_requests(t),
                        width=220, height=35, bg_color=color).pack(side='left', padx=5)

    def create_table(self):
        columns = ("date", "utilisateur", "dossier_medical", "politiques", "etat", "actions")
        self.tree = ModernTable(self.content_frame, columns=columns, height=20)
        
        # Configure columns
        self.tree.heading("date", text="Date")
        self.tree.heading("utilisateur", text="Utilisateur")
        self.tree.heading("dossier_medical", text="Dossier demandé")
        self.tree.heading("politiques", text="Politiques")
        self.tree.heading("etat", text="État")
        self.tree.heading("actions", text="Actions")

        # Column widths
        self.tree.column("date", width=150)
        self.tree.column("utilisateur", width=200)
        self.tree.column("dossier_medical", width=250)
        self.tree.column("politiques", width=200)
        self.tree.column("etat", width=100)
        self.tree.column("actions", width=100)

        # Bind click event
        self.tree.bind('<Double-1>', self.voir_details)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def create_status_bar(self):
        status_frame = tk.Frame(self, bg='#f8fafc')
        status_frame.pack(fill='x', side='bottom')

        self.status_label = tk.Label(status_frame,
                                   text="Chargement...",
                                   font=("Helvetica Neue", 11),
                                   bg='#f8fafc',
                                   fg='#64748b',
                                   pady=10)
        self.status_label.pack(side='left', padx=40)

    from datetime import datetime

    def load_data(self):
        """Charger les données depuis la base de données"""
        connection = connect()
        if not connection:
            messagebox.showerror("Erreur", "Impossible de se connecter à la base de données")
            return

        user_data = self.user_session.get_user()
        if not user_data:
            messagebox.showerror("Erreur", "Aucun utilisateur connecté. Veuillez vous reconnecter.")
            return
        user_id = user_data["iduser"]

        try:
            cursor = connection.cursor()

            # Effacer les données existantes
            for item in self.tree.get_children():
                self.tree.delete(item)

            # Base de la requête SQL
            base_query = """
                SELECT 
                    d.id_demande, 
                    d.date_demande, 
                    u.nom, 
                    u.prenom, 
                    r.id_dossier, 
                    d.politiques, 
                    d.etat
                FROM demande d
                JOIN user u ON d.id_user = u.iduser
                JOIN dossier_medical r ON d.id_dossier = r.id_dossier
                WHERE 1=1
            """
            
            params = []

            # Appliquer les filtres selon le bouton cliqué
            if self.current_filter == "Mes demandes":
                base_query += " AND d.id_user = ?"
                params.append(user_id)
            elif self.current_filter == "Demandes sur mes dossiers":
                base_query += """ AND d.id_dossier IN (
                    SELECT ud.id_dossier
                    FROM user_dossier ud
                    WHERE ud.id_user = ?
                ) AND d.id_user != ?"""  # Exclure les propres demandes de l'utilisateur
                params.extend([user_id, user_id])

            # Recherche par texte
            search_text = self.search_var.get()
            if search_text and search_text != "Rechercher...":
                base_query += """ AND (
                    u.nom LIKE ? OR 
                    u.prenom LIKE ? OR 
                    r.id_dossier LIKE ? OR 
                    d.politiques LIKE ?
                )"""
                search_pattern = f"%{search_text}%"
                params.extend([search_pattern] * 4)

            # Tri par date
            base_query += " ORDER BY d.date_demande DESC"

            # Exécution de la requête
            cursor.execute(base_query, params)

            # Insérer les données dans le Treeview
            for row in cursor.fetchall():
                id_demande, date_demande, nom, prenom, dossier_medical, politiques, etat = row

                # Formatage de la date
                try:
                    date_formattee = datetime.strptime(date_demande, "%Y-%m-%d %H:%M:%S.%f").strftime("%d/%m/%Y %H:%M")
                except ValueError:
                    date_formattee = "Format invalide"

                # Couleurs selon l'état
                etat_colors = {
                    "Accepté": "#10b981",
                    "En attente": "#f59e0b",
                    "Refusé": "#ef4444"
                }

                # Déterminer l'action à afficher
                action = "-" if (self.current_filter == "Mes demandes") else "Voir détails"
                
                self.tree.insert("", "end",
                    values=(date_formattee, f"{prenom} {nom}", dossier_medical, politiques, etat, action),
                    tags=(etat_colors.get(etat, "#64748b"),)
                )

            self.update_status_bar()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors du chargement des données : {str(e)}")
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def filter_requests(self, filter_type):
        """Filtrer les demandes selon le type"""
        self.current_filter = filter_type
        self.load_data()

    def on_search(self, event=None):
        """Gérer la recherche en temps réel"""
        self.load_data()

    def schedule_refresh(self):
        """Programmer le rafraîchissement automatique"""
        self.load_data()
        self.root.after(30000, self.schedule_refresh)

    def update_status_bar(self):
        """Mettre à jour la barre de statut"""
        self.status_label.config(
            text=f"Dernière mise à jour: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    def voir_details(self, event):
        """Afficher les détails d'une demande"""
        selection = self.tree.selection()
        if not selection:
            return

        try:
            item = selection[0]
            demande_values = self.tree.item(item)['values']
            
            details_window = tk.Toplevel(self.root)
            details_window.title("Détails de la demande")
            details_window.geometry("500x400")
            details_window.configure(bg='#ffffff')
            
            # Frame principal
            main_frame = tk.Frame(details_window, bg='#ffffff', padx=20, pady=20)
            main_frame.pack(fill='both', expand=True)
            
            # Titre
            tk.Label(main_frame, 
                    text="Détails de la demande",
                    font=("Helvetica Neue", 18, "bold"),
                    bg='#ffffff',
                    fg='#1e293b').pack(pady=(0, 20))
            
            # Informations détaillées
            details = [
                ("Date", demande_values[0]),
                ("Utilisateur", demande_values[1]),
                ("dossier_medical", demande_values[2]),
                ("Politiques", demande_values[3]),
                ("État", demande_values[4])
            ]
            
            for label, value in details:
                detail_frame = tk.Frame(main_frame, bg='#ffffff')
                detail_frame.pack(fill='x', pady=5)
                
                tk.Label(detail_frame,
                        text=f"{label}:",
                        font=("Helvetica Neue", 12, "bold"),
                        bg='#ffffff',
                        fg='#64748b',
                        width=15,
                        anchor='e').pack(side='left', padx=(0, 10))
                
                tk.Label(detail_frame,
                        text=str(value),
                        font=("Helvetica Neue", 12),
                        bg='#ffffff',
                        fg='#1e293b',
                        wraplength=300,
                        justify='left').pack(side='left', fill='x', expand=True)
            
                buttons_frame = tk.Frame(main_frame, bg='#ffffff')
                buttons_frame.pack(pady=20)
                
                ModernButton(buttons_frame,
                          text="Accepter",
                          command=lambda: self.update_request_status("Accepté", demande_values),
                          bg_color="#10b981",
                          width=100,
                          height=35).pack(side='left', padx=5)
                ModernButton(buttons_frame,
                          text="Refuser",
                          command=lambda: self.update_request_status("Refusé", demande_values),
                          bg_color="#ef4444",
                          width=100,
                          height=35).pack(side='left', padx=5)

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'affichage des détails : {str(e)}")

    def update_request_status(self, new_status, demande_values):
        """Mettre à jour le statut d'une demande"""
        try:
            connection = connect()
            if not connection:
                raise Exception("Impossible de se connecter à la base de données")

            cursor = connection.cursor()

            # Supposons que demande_values[1] = "Jean Dupont"
            nom_prenom = demande_values[1].split()

            # Vérification : S'assurer que le format est correct
            if len(nom_prenom) == 2:
                prenom = nom_prenom[0]  # Première partie : prénom
                nom = nom_prenom[1]     # Deuxième partie : nom
            else:
                messagebox.showerror("Erreur", "Format du nom complet incorrect.")
                return
            
            from datetime import datetime

            # Convertir la date au format ISO 8601
            try:
                demande_date = datetime.strptime(demande_values[0], "%d/%m/%Y %H:%M").strftime("%Y-%m-%d %H:%M:%S")
            except ValueError:
                messagebox.showerror("Erreur", "Format de la date incorrect.")
                return

            # Vérification : Affichage de toutes les demandes pour la date et utilisateur
            print("Recherche des demandes existantes pour la date et utilisateur...")
            
            cursor.execute("""
                SELECT id_demande, date_demande, etat 
                FROM demande 
                WHERE DATE(date_demande) = DATE(?) 
                AND (
                    id_user = (SELECT iduser FROM user WHERE LOWER(nom) = LOWER(?) AND LOWER(prenom) = LOWER(?))
                    OR id_dossier IN (SELECT id_dossier FROM user_dossier WHERE id_user = (SELECT iduser FROM user WHERE LOWER(nom) = LOWER(?) AND LOWER(prenom) = LOWER(?)))
                )
            """, (demande_date, nom, prenom, nom, prenom))

            # Affichage des résultats pour débogage
            demandes_existantes = cursor.fetchall()
            if not demandes_existantes:
                print(f"Aucune demande trouvée pour {nom} {prenom} à la date {demande_date}.")
            else:
                print(f"Demandes trouvées :")
                for row in demandes_existantes:
                    print(row)

            # Si une demande a été trouvée, on effectue la mise à jour
            if demandes_existantes:
                id_demande = demandes_existantes[0][0]  # Prendre le premier résultat

                # Mise à jour du statut dans la base de données
                cursor.execute("""
                    UPDATE demande 
                    SET etat = ? 
                    WHERE id_demande = ?
                """, (new_status, id_demande))

                # Confirmer les changements
                connection.commit()
                messagebox.showinfo("Succès", f"La demande a été marquée comme {new_status}")

                # Rafraîchir les données
                self.load_data()

            else:
                messagebox.showerror("Erreur", "Aucune demande trouvée pour cette date et utilisateur.")
                
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la mise à jour du statut : {str(e)}")
        finally:
            if connection:
                cursor.close()
                connection.close()


if __name__ == "__main__":
    root = tk.Tk()
    app = AccessPage(root)
    root.mainloop()