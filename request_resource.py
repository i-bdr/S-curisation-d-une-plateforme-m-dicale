from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Optional
from user_session import UserSession
from Connection import connect


class ModernCombobox(ttk.Combobox):
    def __init__(self, parent, values: List[str], **kwargs):
        super().__init__(parent, values=values, state='readonly', **kwargs)
        self.option_add('*TCombobox*Listbox.font', ("Inter", 11))
        self.option_add('*TCombobox*Listbox.background', "#ffffff")
        self.option_add('*TCombobox*Listbox.foreground', "#1e293b")
        self.option_add('*TCombobox*Listbox.selectBackground', "#e2e8f0")
        self.option_add('*TCombobox*Listbox.selectForeground', "#0f172a")
        self.configure(font=("Inter", 11))
        self.user_session = UserSession.get_instance()

    def set_values(self, values: List[str]):
        self.set_values(values)


class ModernButton(tk.Button):
    def __init__(self, parent, variant: str = "primary", **kwargs):
        super().__init__(parent, **kwargs)
        self.variant = variant

        # Configuration des styles selon le variant
        styles = {
            "primary": {
                "bg": "#0ea5e9",
                "fg": "white",
                "activebackground": "#0284c7",
                "activeforeground": "white"
            },
            "secondary": {
                "bg": "#f1f5f9",
                "fg": "#475569",
                "activebackground": "#e2e8f0",
                "activeforeground": "#334155"
            },
            "danger": {
                "bg": "#ef4444",
                "fg": "white",
                "activebackground": "#dc2626",
                "activeforeground": "white"
            }
        }

        style = styles.get(variant, styles["primary"])
        self.configure(**style, font=("Inter", 11), relief="flat", padx=20, pady=8)

        # Effet de survol
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, e):
        if self.variant == "primary":
            self.configure(bg="#0284c7")
        elif self.variant == "secondary":
            self.configure(bg="#e2e8f0")
        else:
            self.configure(bg="#dc2626")

    def _on_leave(self, e):
        if self.variant == "primary":
            self.configure(bg="#0ea5e9")
        elif self.variant == "secondary":
            self.configure(bg="#f1f5f9")
        else:
            self.configure(bg="#ef4444")


def create_tooltip(widget, text: str):
    """Crée un tooltip personnalisé pour un widget"""
    tooltip = tk.Label(
        widget.master,
        text=text,
        background="#1e293b",
        foreground="white",
        font=("Inter", 10),
        padx=10,
        pady=5,
        relief="flat"
    )

    def enter(event):
        tooltip.lift()
        x = widget.winfo_rootx() - tooltip.winfo_reqwidth() // 2 + widget.winfo_width() // 2
        y = widget.winfo_rooty() - tooltip.winfo_reqheight() - 5
        tooltip.place(x=x, y=y)

    def leave(event):
        tooltip.place_forget()

    widget.bind("<Enter>", enter)
    widget.bind("<Leave>", leave)


def open_request_resource(root: tk.Tk, client_socket, role: str):
    request_window = tk.Toplevel(root)
    request_window.title("Demande d'Accès")
    request_window.geometry("800x700")
    request_window.configure(bg='#ffffff')
    request_window.resizable(False, False)

    # Obtenir l'instance de UserSession
    user_session = UserSession.get_instance()

    # Style global
    style = ttk.Style()
    style.configure('Main.TFrame', background='#ffffff')
    style.configure('Card.TFrame', background='#f8fafc')
    style.configure('Card.Header.TFrame', background='#f1f5f9')

    # Container principal avec ombre
    outer_container = ttk.Frame(request_window, style='Main.TFrame')
    outer_container.pack(expand=True, fill='both', padx=40, pady=40)

    # En-tête avec badge de rôle
    header_frame = ttk.Frame(outer_container, style='Main.TFrame')
    header_frame.pack(fill='x', pady=(0, 30))

    title_frame = ttk.Frame(header_frame, style='Main.TFrame')
    title_frame.pack(side='left')

    icon_label = tk.Label(
        title_frame,
        text="🔐",
        font=("Segoe UI Emoji", 48),
        bg='#ffffff',
        fg='#0f172a'
    )
    icon_label.pack(side='left', padx=(0, 20))

    title_label = tk.Label(
        title_frame,
        text="Demande d'Accès",
        font=("Inter", 32, "bold"),
        bg='#ffffff',
        fg='#0f172a'
    )
    title_label.pack(side='left')

    # Badge de rôle
    role_badge = tk.Label(
        header_frame,
        text=f"Rôle: {role}",
        font=("Inter", 11),
        bg='#0ea5e9',
        fg='white',
        padx=12,
        pady=6
    )
    role_badge.pack(side='right', pady=15)

    # Carte principale avec ombre
    main_card = ttk.Frame(outer_container, style='Card.TFrame')
    main_card.pack(fill='x', pady=20, padx=1)

    # En-tête de la carte
    card_header = ttk.Frame(main_card, style='Card.Header.TFrame')
    card_header.pack(fill='x', pady=(0, 20))

    header_title = tk.Label(
        card_header,
        text="Détails de la demande",
        font=("Inter", 14, "bold"),
        bg='#f1f5f9',
        fg='#0f172a',
        pady=15,
        padx=20
    )
    header_title.pack(anchor='w')

    # Section ressource
    resource_section = ttk.Frame(main_card, style='Card.TFrame')
    resource_section.pack(fill='x', padx=20, pady=10)

    resource_label = tk.Label(
        resource_section,
        text="Ressource",
        font=("Inter", 12, "bold"),
        bg='#f8fafc',
        fg='#475569'
    )
    resource_label.pack(anchor='w', pady=(0, 5))

    def fetch_medical_records(cursor):
        """Récupère les dossiers médicaux avec les informations des patients"""
        query = """
            SELECT 
                dm.id_dossier,
                dm.id_patient,
                u.nom,
                u.prenom
            FROM dossier_medical dm
            JOIN user u ON u.iduser = dm.id_patient
            ORDER BY u.nom, u.prenom
        """
        cursor.execute(query)
        records = cursor.fetchall()

        # Formatage des options pour la combobox
        options = [f"Dossier #{r[0]} - Patient: {r[2]} {r[3]}" for r in records]
        # Stockage des IDs pour une utilisation ultérieure
        return options, {opt: record[0] for opt, record in zip(options, records)}

    connection = connect()
    cursor = connection.cursor()
    resource_options, resource_ids = fetch_medical_records(cursor)

    resource_var = tk.StringVar()
    resource_combo = ModernCombobox(
        resource_section,
        resource_options,
        textvariable=resource_var
    )
    resource_combo.pack(fill='x', pady=(0, 5))

    # Stockage des IDs dans une variable de la fenêtre pour utilisation ultérieure
    request_window.resource_ids = resource_ids

    # Texte d'aide pour la ressource
    resource_help = tk.Label(
        resource_section,
        text="Sélectionnez la ressource à laquelle vous souhaitez accéder",
        font=("Inter", 10),
        bg='#f8fafc',
        fg='#64748b'
    )
    resource_help.pack(anchor='w', pady=(0, 10))

    # Section type d'accès
    policy_section = ttk.Frame(main_card, style='Card.TFrame')
    policy_section.pack(fill='x', padx=20, pady=10)

    policy_label = tk.Label(
        policy_section,
        text="Type d'Accès",
        font=("Inter", 12, "bold"),
        bg='#f8fafc',
        fg='#475569'
    )
    policy_label.pack(anchor='w', pady=(0, 5))

    policy_var = tk.StringVar()
    policy_combo = ModernCombobox(
        policy_section,
        ["Lecture", "Écriture", "Exécution", "owner"],
        textvariable=policy_var
    )
    policy_combo.pack(fill='x', pady=(0, 5))

    # Texte d'aide pour le type d'accès
    policy_help = tk.Label(
        policy_section,
        text="Définissez le niveau d'accès requis pour cette ressource",
        font=("Inter", 10),
        bg='#f8fafc',
        fg='#64748b'
    )
    policy_help.pack(anchor='w', pady=(0, 10))

    # Section des boutons avec séparateur
    separator = ttk.Separator(main_card, orient='horizontal')
    separator.pack(fill='x', pady=20)

    buttons_frame = ttk.Frame(main_card, style='Card.TFrame')
    buttons_frame.pack(fill='x', padx=20, pady=(0, 20))

    def validate_form() -> bool:
        """Valide le formulaire avant d'envoyer la demande."""
        if not resource_var.get() or not policy_var.get():
            messagebox.showerror(
                "Champs manquants",
                "Veuillez remplir tous les champs obligatoires.",
                parent=request_window
            )
            return False
        return True

    def send_request():
        """Envoyer la requête au serveur."""
        if validate_form():
            try:
                user_data = user_session.get_user()
                cursor.execute("""
                    INSERT INTO demande (id_user, id_dossier, politiques, date_demande, etat)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    user_data['iduser'],
                    request_window.resource_ids[resource_var.get()],
                    policy_var.get(),
                    datetime.now(),
                    "En attente"
                ))
                connection.commit()

                messagebox.showinfo(
                    "Demande envoyée",
                    "Votre demande a été traitée avec succès.",
                    parent=request_window
                )
                request_window.destroy()
            except Exception as e:
                messagebox.showerror(
                    "Erreur",
                    f"Impossible d'envoyer la demande : {str(e)}",
                    parent=request_window
                )

    # Boutons avec le nouveau style
    cancel_btn = ModernButton(
        buttons_frame,
        text="Annuler",
        command=request_window.destroy,
        variant="secondary"
    )
    cancel_btn.pack(side='left', padx=(0, 10))

    validate_btn = ModernButton(
        buttons_frame,
        text="Envoyer la demande",
        command=send_request,
        variant="primary"
    )
    validate_btn.pack(side='left')

    # Centrer la fenêtre
    request_window.update_idletasks()
    x = (request_window.winfo_screenwidth() // 2) - (800 // 2)
    y = (request_window.winfo_screenheight() // 2) - (700 // 2)
    request_window.geometry(f"800x700+{x}+{y}")

    # Focus initial
    resource_combo.focus_set()
