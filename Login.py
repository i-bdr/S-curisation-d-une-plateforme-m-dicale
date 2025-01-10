import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from PIL import Image, ImageTk
from cryptography.fernet import Fernet
import hashlib
import os
import time
import random
from user_session import UserSession
from Connection import connect
from DiffieHellmanInterface import DiffieHellmanInterface
from home_page import HomePage

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=40, bg_color="#2563eb", state="normal", **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg=parent["bg"], highlightthickness=0, height=height, width=width)
        self.text = text
        self.command = command
        self.state = state
        
        self.default_color = bg_color
        self.hover_color = self.adjust_color(bg_color, -20)
        self.active_color = self.adjust_color(bg_color, -40)
        self.disabled_color = "#94a3b8"
        self.current_color = self.default_color if state == "normal" else self.disabled_color
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw()

    def adjust_color(self, color, amount):
        """Adjust color brightness"""
        hex_color = color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)
        
    def draw(self):
        """Draw the button"""
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        if not width or not height:
            self.update_idletasks()
            width = self.winfo_width()
            height = self.winfo_height()
        
        radius = 8
        color = self.disabled_color if self.state == "disabled" else self.current_color
        self.create_rounded_rect(0, 0, width, height, radius, color)
        self.create_text(width / 2, height / 2, text=self.text, fill="white", 
                        font=("Helvetica Neue", 12, "bold"))

    def create_rounded_rect(self, x1, y1, x2, y2, radius, color):
        """Create a rounded rectangle"""
        self.create_rectangle(x1 + radius, y1, x2 - radius, y2, fill=color, outline=color)
        self.create_rectangle(x1, y1 + radius, x2, y2 - radius, fill=color, outline=color)
        self.create_oval(x1, y1, x1 + 2 * radius, y1 + 2 * radius, fill=color, outline=color)
        self.create_oval(x2 - 2 * radius, y1, x2, y1 + 2 * radius, fill=color, outline=color)
        self.create_oval(x1, y2 - 2 * radius, x1 + 2 * radius, y2, fill=color, outline=color)
        self.create_oval(x2 - 2 * radius, y2 - 2 * radius, x2, y2, fill=color, outline=color)

    def on_enter(self, event):
        """Handle mouse enter event"""
        if self.state == "normal":
            self.current_color = self.hover_color
            self.draw()

    def on_leave(self, event):
        """Handle mouse leave event"""
        if self.state == "normal":
            self.current_color = self.default_color
            self.draw()

    def on_press(self, event):
        """Handle mouse press event"""
        if self.state == "normal":
            self.current_color = self.active_color
            self.draw()

    def on_release(self, event):
        """Handle mouse release event"""
        if self.state == "normal" and self.command:
            self.command()
        if self.state == "normal":
            self.current_color = self.default_color
            self.draw()

    def config(self, **kwargs):
        """Configure button properties"""
        if "state" in kwargs:
            self.state = kwargs["state"]
            self.current_color = self.default_color if self.state == "normal" else self.disabled_color
            self.draw()

class ModernEntry(tk.Frame):
    def __init__(self, parent, placeholder, show=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.configure(bg='white')
        
        self.placeholder = placeholder
        self.show = show
        self.placeholder_color = '#94a3b8'
        self.default_fg = '#1e293b'
        self.has_placeholder = True
        
        self.entry = tk.Entry(
            self,
            font=("Helvetica Neue", 12),
            bg='white',
            fg=self.placeholder_color,
            insertbackground=self.default_fg,
            relief='flat',
            highlightthickness=1,
            highlightbackground="#e2e8f0",
            highlightcolor="#2563eb"
        )
        self.entry.insert(0, placeholder)
        self.entry.pack(fill='x', pady=2, ipady=8, padx=1)
        
        self.entry.bind('<FocusIn>', self.on_focus_in)
        self.entry.bind('<FocusOut>', self.on_focus_out)

    def on_focus_in(self, event):
        """Handle focus in event"""
        if self.has_placeholder:
            self.entry.delete(0, tk.END)
            self.entry.config(fg=self.default_fg)
            if self.show:
                self.entry.config(show=self.show)
            self.has_placeholder = False

    def on_focus_out(self, event):
        """Handle focus out event"""
        if not self.entry.get():
            self.entry.insert(0, self.placeholder)
            self.entry.config(fg=self.placeholder_color)
            if self.show:
                self.entry.config(show='')
            self.has_placeholder = True

    def get(self):
        """Get entry value"""
        if self.has_placeholder:
            return ''
        return self.entry.get()

    def insert(self, index, string):
        """Insert text into entry"""
        self.entry.insert(index, string)

    def delete(self, first, last=None):
        """Delete text from entry"""
        self.entry.delete(first, last)
        
    def config(self, **kwargs):
        """Configure entry properties"""
        self.entry.config(**kwargs)

class SecureLandingPage:
    def __init__(self, root):
        self.root = root
        self.user_session = UserSession.get_instance()
        # Security variables
        self.attempts = 0
        self.locked_out_until = None
        self.challenge = self.generate_challenge()
        self.start_time = 0
        self.connected_user = {}
        
        # Initialize Fernet key
        self.setup_encryption()
        
        self.setup_ui()
    
    def setup_encryption(self):
        """Initialize encryption key and cipher"""
        key_file = 'key.key'
        try:
            if os.path.exists(key_file):
                with open(key_file, 'rb') as kf:
                    self.key = kf.read()
            else:
                self.key = Fernet.generate_key()
                with open(key_file, 'wb') as kf:
                    kf.write(self.key)
            
            self.cipher = Fernet(self.key)
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur d'initialisation du chiffrement : {str(e)}")
            raise
    
    def generate_challenge(self):
        """Generate a random challenge for authentication"""
        return str(random.randint(100000, 999999))
        
    def setup_ui(self):
        """Setup user interface"""
        self.root.title("Espace Médical - Accueil")
        self.root.geometry("1200x800")
        self.root.configure(bg='#ffffff')
        
        # Split view into two parts
        left_frame = tk.Frame(self.root, bg='#1e293b', width=600)
        left_frame.pack(side='left', fill='y')
        left_frame.pack_propagate(False)
        
        right_frame = tk.Frame(self.root, bg='white', width=600)
        right_frame.pack(side='right', fill='both', expand=True)
        
        self.setup_left_content(left_frame)
        self.setup_right_content(right_frame)
        
    def setup_left_content(self, parent):
        """Setup left side of the interface"""
        tk.Label(
            parent,
            text="🏥",
            font=("Segoe UI Emoji", 64),
            bg='#1e293b',
            fg='white'
        ).pack(pady=(100, 20))
        
        tk.Label(
            parent,
            text="Espace Médical",
            font=("Helvetica Neue", 32, "bold"),
            bg='#1e293b',
            fg='white'
        ).pack(pady=(0, 20))
        
        tk.Label(
            parent,
            text="Plateforme sécurisée de gestion\ndes dossiers médicaux",
            font=("Helvetica Neue", 16),
            bg='#1e293b',
            fg='#94a3b8',
            justify='center'
        ).pack(pady=20)
        
        features = [
            "🔒 Sécurité renforcée",
            "📊 Gestion simplifiée",
            "🔄 Synchronisation en temps réel",
            "📱 Accès multi-plateformes"
        ]
        features_frame = tk.Frame(parent, bg='#1e293b')
        features_frame.pack(pady=40)
        
        for feature in features:
            tk.Label(
                features_frame,
                text=feature,
                font=("Helvetica Neue", 14),
                bg='#1e293b',
                fg='#e2e8f0',
                pady=10
            ).pack()
        
    def setup_right_content(self, parent):
        """Setup right side of the interface"""
        login_frame = tk.Frame(parent, bg='white')
        login_frame.place(relx=0.5, rely=0.5, anchor='center')
        
        tk.Label(
            login_frame,
            text="Bienvenue",
            font=("Helvetica Neue", 24, "bold"),
            bg='white',
            fg='#1e293b'
        ).pack(pady=(0, 10))
        
        tk.Label(
            login_frame,
            text="Connectez-vous à votre compte",
            font=("Helvetica Neue", 14),
            bg='white',
            fg='#64748b'
        ).pack(pady=(0, 30))
        
        self.username_entry = ModernEntry(login_frame, "Nom d'utilisateur")
        self.username_entry.pack(pady=10, fill='x')
        
        password_frame = tk.Frame(login_frame, bg='white')
        password_frame.pack(fill='x', pady=10)
        
        self.password_entry = ModernEntry(password_frame, "Mot de passe", show="•")
        self.password_entry.pack(side='left', fill='x', expand=True)
        
        self.setup_password_visibility(password_frame)
        
        options_frame = tk.Frame(login_frame, bg='white')
        options_frame.pack(fill='x', pady=20)
        
        self.remember_var = tk.BooleanVar()
        ttk.Checkbutton(
            options_frame,
            text="Se souvenir de moi",
            variable=self.remember_var
        ).pack(side='left')
        
        forgot_pwd_label = tk.Label(
            options_frame,
            text="Mot de passe oublié ?",
            font=("Helvetica Neue", 11),
            bg='white',
            fg='#2563eb',
            cursor='hand2'
        )
        forgot_pwd_label.pack(side='right')
        forgot_pwd_label.bind("<Button-1>", lambda e: self.forgot_password())
        
        self.login_button = ModernButton(
            login_frame,
            text="Se connecter",
            command=self.login,
            width=300,
            bg_color="#2563eb"
        )
        self.login_button.pack(pady=20)
        
        self.setup_footer(login_frame)

    def setup_password_visibility(self, parent):
        """Setup password visibility toggle"""
        try:
            self.eye_icon = Image.open("oeil.png")
            self.eye_icon = self.eye_icon.resize((20, 20), Image.Resampling.LANCZOS)
            self.eye_icon = ImageTk.PhotoImage(self.eye_icon)
            
            self.eye_button = tk.Button(
                parent,
                image=self.eye_icon,
                bg='white',
                relief='flat',
                command=self.toggle_password_visibility
            )
            self.eye_button.pack(side='right', padx=(10, 0))
        except FileNotFoundError:
            pass

    def setup_footer(self, parent):
        """Setup footer section"""
        footer_frame = tk.Frame(parent, bg='white')
        footer_frame.pack(pady=20)
        
        tk.Label(
            footer_frame,
            text="Vous n'avez pas de compte ? ",
            font=("Helvetica Neue", 11),
            bg='white',
            fg='#64748b'
        ).pack(side='left')
        
        tk.Label(
            footer_frame,
            text="Contactez votre administrateur",
            font=("Helvetica Neue", 11),
            bg='white',
            fg='#2563eb',
            cursor='hand2'
        ).pack(side='left')

    def login(self):
        """Handle login process"""
        self.start_time = time.time()
        if self.is_locked_out():
            return

        username = self.username_entry.get()
        password = self.password_entry.get()

        if not self.validate_inputs(username, password):
            return

        connection = connect()
        if not connection:
            messagebox.showerror("Erreur", "Échec de la connexion à la base de données.")
            return

        try:
            cursor = connection.cursor()
            user_data = self.fetch_user_data(cursor, username)
            cursor.close()
            
            if not user_data:
                self.handle_failed_attempt()
                return

            iduser, nom, prenom, encrypted_password, role_id, date_naissance = user_data
            if self.verify_password(encrypted_password, password):
                self.handle_successful_login(iduser, nom, prenom, role_id, date_naissance)
            else:
                self.handle_failed_attempt()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la connexion : {str(e)}")


    def is_locked_out(self):
        """Check if the user is currently locked out"""
        if self.locked_out_until and time.time() < self.locked_out_until:
            remaining_time = int(self.locked_out_until - time.time())
            messagebox.showwarning("Verrouillé", 
                f"Vous devez attendre encore {remaining_time} secondes avant de réessayer.")
            return True
        return False

    def validate_inputs(self, username, password):
        """Validate user inputs"""
        if not username or not password:
            messagebox.showwarning("Erreur", "Veuillez remplir tous les champs.")
            return False
        return True

    def fetch_user_data(self, cursor, username):
        """Fetch user data from database"""
        cursor.execute("""
            SELECT u.iduser, u.nom, u.prenom, u.motDePasse, u.role_id, u.date_naissance 
            FROM user u 
            WHERE u.mail = ?
        """, (username,))
        return cursor.fetchone()

    def verify_password(self, encrypted_password, provided_password):
        """Verify user password using challenge-response"""
        try:
            decrypted_password = self.cipher.decrypt(encrypted_password).decode()
            chap_response = hashlib.md5((self.challenge + decrypted_password).encode()).hexdigest()
            user_response = hashlib.md5((self.challenge + provided_password).encode()).hexdigest()
            return chap_response == user_response
        except Exception:
            return False

    def handle_successful_login(self, iduser, nom, prenom, role_id, date_naissance):
        """Handle successful login attempt"""
        try:
                connection = connect()
                cursor = connection.cursor()
                cursor.execute("SELECT rolename FROM role WHERE idRole=?", (role_id,))
                role = cursor.fetchone()[0]
                cursor.close()

                # Store connected user info using UserSession
                user_data = {
                    "iduser": iduser,
                    "nom": nom,
                    "prenom": prenom,
                    "role": role
                }
                self.user_session.set_user(user_data)

                print(f"Utilisateur connecté : {user_data}")
                self.log_execution_time()
                self.verify_birth_date(date_naissance, role_id, role)
        except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la connexion : {str(e)}")


    def handle_failed_attempt(self):
        """Handle failed login attempt"""
        self.attempts += 1
        if self.attempts >= 3:
            self.lock_out_user()
        else:
            remaining_attempts = 3 - self.attempts
            messagebox.showwarning("Erreur", 
                f"Identifiant ou mot de passe incorrect. Il vous reste {remaining_attempts} tentatives.")

    def lock_out_user(self):
        """Lock out user after too many failed attempts"""
        messagebox.showerror("Verrouillé", "Trop de tentatives échouées. Vous devez attendre 5 minutes avant de réessayer.")
        self.locked_out_until = time.time() + 300
        self.login_button.config(state="disabled")
        self.root.after(300000, self.unlock_user)

    def unlock_user(self):
        """Unlock user after timeout period"""
        self.attempts = 0
        self.locked_out_until = None
        self.login_button.config(state="normal")

    def verify_birth_date(self, expected_date_naissance, role_id, role):
        """Verify user's birth date with improved UI"""
        birth_date_window = tk.Toplevel(self.root)
        birth_date_window.title("Vérification de la date de naissance")
        birth_date_window.geometry("400x200")
        birth_date_window.configure(bg="#f8fafc")
        birth_date_window.grab_set()  # Empêche de cliquer sur la fenêtre principale

        tk.Label(
            birth_date_window,
            text="Entrez votre date de naissance (AAAA-MM-JJ):",
            font=("Helvetica Neue", 14),
            bg="#f8fafc",
            fg="#1e293b"
        ).pack(pady=(20, 10))

        birth_date_entry = ModernEntry(birth_date_window, "AAAA-MM-JJ")
        birth_date_entry.pack(pady=10, padx=20)

        button_frame = tk.Frame(birth_date_window, bg="#f8fafc")
        button_frame.pack(pady=20)

        def validate_date():
            birth_date = birth_date_entry.get()
            if birth_date == expected_date_naissance:
                birth_date_window.destroy()
                if role_id == 1:
                    print("Bienvenue, Administrateur")
                    self.open_home_page(role)
                else:
                    print(f"Bienvenue, {role} {self.user_session.get_user()['prenom']} {self.user_session.get_user()['nom']}")
                    self.open_home_page(role)
            else:
                messagebox.showerror("Erreur", "Date de naissance incorrecte.")
                self.handle_failed_attempt()

        ModernButton(
            button_frame,
            text="Valider",
            command=validate_date,
            bg_color="#10b981",
            width=150
        ).pack(side="left", padx=10)

        ModernButton(
            button_frame,
            text="Annuler",
            command=birth_date_window.destroy,
            bg_color="#ef4444",
            width=150
        ).pack(side="right", padx=10)

        birth_date_window.mainloop()

    def log_execution_time(self):
        """Log the execution time of the login process"""
        end_time = time.time()
        execution_time = (end_time - self.start_time) * 1000
        print(f"Temps d'exécution: {execution_time:.2f} ms")

    def open_home_page(self, role):
        """Open the home page after successful login"""
        self.root.destroy()
        new_root = tk.Tk()
        HomePage(new_root, role)
        new_root.mainloop()

    def toggle_password_visibility(self):
        """Toggle password visibility"""
        current_show = self.password_entry.entry.cget('show')
        self.password_entry.entry.config(show='' if current_show == '•' else '•')

    def forgot_password(self):
        """Handle forgot password request"""
        messagebox.showinfo(
            "Réinitialisation du mot de passe",
            "Veuillez contacter votre administrateur système."
        )


if __name__ == "__main__":
    root = tk.Tk()
    app = SecureLandingPage(root)
    root.mainloop()