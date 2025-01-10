import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import scrolledtext
import sqlite3
from datetime import datetime
from assets.style import ModernUI, ModernEntry, ModernButton

# Connexion à la base de données
conn = sqlite3.connect('DBESante.db')
cur = conn.cursor()

# Fonction pour récupérer la liste des médecins traitants
def get_medecins_traitants():
    cur.execute("""
        SELECT iduser, nom, prenom FROM user WHERE role_id = 2
    """)
    return cur.fetchall()

# Fonction pour ajouter un patient et un dossier médical
def add_patient_and_dossier():
    # Récupérer les valeurs saisies dans les champs
    nom_patient = entry_nom_patient.get()
    prenom_patient = entry_prenom_patient.get()
    date_naissance = entry_date_naissance.get()
    email = entry_email.get()
    
    # Récupérer l'ID du médecin traitant sélectionné
    selected_index = combo_medecin_traitant.current()
    if selected_index == -1:  # Aucun médecin sélectionné
        messagebox.showwarning("Sélection manquante", "Veuillez sélectionner un médecin traitant.")
        return
    medecin_traitant_id = medecins_traitants[selected_index][0]  # Récupérer l'ID du médecin
    
    antecedents = entry_antecedents.get("1.0", tk.END).strip()
    pathologies = entry_pathologies.get("1.0", tk.END).strip()
    traitements = entry_traitements.get("1.0", tk.END).strip()
    allergies = entry_allergies.get("1.0", tk.END).strip()
    observations = entry_observations.get("1.0", tk.END).strip()

    # Validation des champs
    if not (nom_patient and prenom_patient and date_naissance):
        messagebox.showwarning("Entrée manquante", "Veuillez remplir tous les champs obligatoires.")
        return

    try:
        # Insertion du patient dans la table 'user'
        cur.execute("""
            INSERT INTO user (nom, prenom, date_naissance, mail, role_id)
            VALUES (?, ?, ?, ?, ?)
        """, (nom_patient, prenom_patient, date_naissance, email, 5))  
        conn.commit()

        # Récupérer l'ID du patient inséré
        id_patient = cur.lastrowid

        # Insertion du dossier médical dans la table 'dossier_medical'
        cur.execute("""
            INSERT INTO dossier_medical (id_patient, pathologies, traitements, allergies, antecedents, observations, date_creation)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (id_patient, pathologies, traitements, allergies, antecedents, observations, datetime.now().strftime("%Y-%m-%d")))
        conn.commit()

        # Récupérer l'ID du dossier médical inséré
        id_dossier = cur.lastrowid

        # Insérer une politique "owner" pour le médecin traitant
        cur.execute("""
            INSERT INTO user_dossier (id_user, id_dossier, nom_privilege)
            VALUES (?, ?, ?)
        """, (medecin_traitant_id, id_dossier, "owner"))
        print(medecin_traitant_id, id_dossier, "owner")
        conn.commit()

        messagebox.showinfo("Succès", "Patient, dossier médical et politique 'owner' ajoutés avec succès.")
        clear_entries()
        update_dossier_list()
    except sqlite3.IntegrityError:
        messagebox.showerror("Erreur", "Le numéro de dossier ou les informations sont invalides.")
    except sqlite3.Error as e:
        messagebox.showerror("Erreur SQL", f"Erreur lors de l'ajout: {e}")

# Fonction pour effacer les champs de saisie
def clear_entries():
    entry_nom_patient.delete(0, tk.END)
    entry_prenom_patient.delete(0, tk.END)
    entry_date_naissance.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    entry_antecedents.delete("1.0", tk.END)
    entry_pathologies.delete("1.0", tk.END)
    entry_traitements.delete("1.0", tk.END)
    entry_allergies.delete("1.0", tk.END)
    entry_observations.delete("1.0", tk.END)
    combo_medecin_traitant.current(0)  # Réinitialiser la liste déroulante

# Fonction pour mettre à jour la liste affichée des dossiers
def update_dossier_list():
    for i in dossier_list.get_children():
        dossier_list.delete(i)

    try:
        cur.execute("""
            SELECT d.id_dossier, u.nom, u.prenom, d.date_creation, d.pathologies, d.traitements, d.allergies, d.antecedents, d.observations
            FROM dossier_medical d
            JOIN user u ON d.id_patient = u.iduser
        """)
        rows = cur.fetchall()
        for row in rows:
            dossier_list.insert("", "end", values=row)
    except sqlite3.Error as e:
        messagebox.showerror("Erreur SQL", f"Erreur lors de la récupération des dossiers: {e}")

# Créer la fenêtre principale
root = tk.Tk()
root.title("Gestion des Dossiers Médicaux - E-Santé")
root.state('zoomed')  # Ouvrir en plein écran
root.configure(bg="#ffffff")
ModernUI.setup_styles()

# Cadre principal pour organiser les éléments
main_frame = ttk.Frame(root)
main_frame.pack(fill=tk.BOTH, expand=True)

# Cadre pour le formulaire (à gauche)
form_frame = ttk.Frame(main_frame, padding=20)
form_frame.grid(row=0, column=0, sticky="nsew")

# Cadre pour le tableau (à droite)
table_frame = ttk.Frame(main_frame, padding=10)
table_frame.grid(row=0, column=1, sticky="nsew")

# Configuration des poids des colonnes pour le redimensionnement
main_frame.columnconfigure(0, weight=1)  # Formulaire
main_frame.columnconfigure(1, weight=2)  # Tableau
main_frame.rowconfigure(0, weight=1)

# Formulaire (à gauche)
tk.Label(form_frame, text="Nom du Patient:", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=0, column=0, sticky="w", pady=5)
entry_nom_patient = ModernEntry(form_frame, placeholder="Entrez le nom", width=40)
entry_nom_patient.grid(row=0, column=1, pady=5)

tk.Label(form_frame, text="Prénom du Patient:", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=1, column=0, sticky="w", pady=5)
entry_prenom_patient = ModernEntry(form_frame, placeholder="Entrez le prénom", width=40)
entry_prenom_patient.grid(row=1, column=1, pady=5)

tk.Label(form_frame, text="Date de Naissance (YYYY-MM-DD):", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=2, column=0, sticky="w", pady=5)
entry_date_naissance = ModernEntry(form_frame, placeholder="YYYY-MM-DD", width=40)
entry_date_naissance.grid(row=2, column=1, pady=5)

tk.Label(form_frame, text="Email:", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=3, column=0, sticky="w", pady=5)
entry_email = ModernEntry(form_frame, placeholder="Entrez l'email", width=40)
entry_email.grid(row=3, column=1, pady=5)

# Liste déroulante pour le médecin traitant
tk.Label(form_frame, text="Médecin Traitant:", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=4, column=0, sticky="w", pady=5)
medecins_traitants = get_medecins_traitants()  # Récupérer les médecins traitants
combo_medecin_traitant = ttk.Combobox(form_frame, values=[f"{med[1]} {med[2]}" for med in medecins_traitants], font=("Helvetica Neue", 10), state="readonly")
combo_medecin_traitant.grid(row=4, column=1, pady=5)
combo_medecin_traitant.current(0)  # Sélectionner le premier médecin par défaut

tk.Label(form_frame, text="Antécédents Médicaux:", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=5, column=0, sticky="w", pady=5)
entry_antecedents = scrolledtext.ScrolledText(form_frame, font=("Helvetica Neue", 10), width=40, height=4)
entry_antecedents.grid(row=5, column=1, pady=5)

tk.Label(form_frame, text="Pathologies:", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=6, column=0, sticky="w", pady=5)
entry_pathologies = scrolledtext.ScrolledText(form_frame, font=("Helvetica Neue", 10), width=40, height=4)
entry_pathologies.grid(row=6, column=1, pady=5)

tk.Label(form_frame, text="Traitements:", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=7, column=0, sticky="w", pady=5)
entry_traitements = scrolledtext.ScrolledText(form_frame, font=("Helvetica Neue", 10), width=40, height=4)
entry_traitements.grid(row=7, column=1, pady=5)

tk.Label(form_frame, text="Allergies:", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=8, column=0, sticky="w", pady=5)
entry_allergies = scrolledtext.ScrolledText(form_frame, font=("Helvetica Neue", 10), width=40, height=4)
entry_allergies.grid(row=8, column=1, pady=5)

tk.Label(form_frame, text="Observations:", font=("Helvetica Neue", 12), bg='white', fg='#1e293b').grid(row=9, column=0, sticky="w", pady=5)
entry_observations = scrolledtext.ScrolledText(form_frame, font=("Helvetica Neue", 10), width=40, height=4)
entry_observations.grid(row=9, column=1, pady=5)

# Bouton pour ajouter le patient et le dossier médical
btn_add = ttk.Button(form_frame, text="Ajouter Patient et Dossier Médical", command=add_patient_and_dossier, style="Success.TButton")
btn_add.grid(row=10, columnspan=2, pady=10)

# Tableau des dossiers médicaux (à droite)
columns = ("ID Dossier", "Nom", "Prénom", "Date Création", "Pathologies", "Traitements", "Allergies", "Antécédents", "Observations")
dossier_list = ttk.Treeview(table_frame, columns=columns, show="headings", style="Treeview")

for col in columns:
    dossier_list.heading(col, text=col)
    dossier_list.column(col, anchor="center", width=120)

scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=dossier_list.yview)
dossier_list.configure(yscrollcommand=scrollbar.set)

dossier_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# Mise à jour initiale de la liste
update_dossier_list()

# Lancement de l'application
root.mainloop()