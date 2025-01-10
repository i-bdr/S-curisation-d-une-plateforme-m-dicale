import tkinter as tk
from tkinter import messagebox, ttk
import subprocess
import socket
from DiffieHelmanConfiguration import DiffieHelmanConfiguration
from DiffieHellmanInterface import DiffieHellmanInterface

class ModernButton(tk.Canvas):
    def __init__(self, parent, text, command, width=200, height=45, bg_color="#2563eb", **kwargs):
        self.pressed = False
        super().__init__(parent, **kwargs)
        self.configure(bg=parent["bg"], highlightthickness=0, height=height, width=width)
        self.text = text
        self.command = command
        self.bg_color = bg_color
        
        # Couleurs modernes
        self.default_color = bg_color
        self.hover_color = self.adjust_color(bg_color, -20)
        self.current_color = self.default_color
        
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)
        self.bind("<Button-1>", self.on_press)
        self.bind("<ButtonRelease-1>", self.on_release)
        
        self.draw()

    def adjust_color(self, color, amount):
        # Assombrir ou éclaircir une couleur hex
        hex_color = color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        new_rgb = tuple(max(0, min(255, c + amount)) for c in rgb)
        return '#{:02x}{:02x}{:02x}'.format(*new_rgb)
        
    def draw(self):
        self.delete("all")
        width = self.winfo_width()
        height = self.winfo_height()
        
        # Coins arrondis élégants
        radius = 12
        self.create_rounded_rect(0, 0, width, height, radius, self.current_color)
        
        # Texte avec ombre subtile
        self.create_text(width/2, height/2 + 1, text=self.text, fill="#666666", 
                        font=("Helvetica Neue", 12, "bold"))
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
        self.pressed = True
        
    def on_release(self, event):
        if self.pressed:
            self.pressed = False
            self.command()

class HomePage:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.server_address = ('127.0.0.1', 12345)

        # Configuration du socket
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect(self.server_address)
        self.client_socket.sendall(self.role.encode())

        self.trusted_party = None
        self.setup_home_page()

    def setup_home_page(self):
        """Configuration moderne de la page d'accueil"""
        self.root.title(f"Espace Médical - {self.role.capitalize()}")
        self.root.geometry("1200x800")
        self.root.configure(bg='#ffffff')

        # Style global
        self.setup_styles()
        
        # Layout principal avec grid
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # Création des sections
        self.create_sidebar()  # Colonne 0
        self.create_main_content()  # Colonne 1

    def setup_styles(self):
        style = ttk.Style()
        style.configure('Sidebar.TFrame', background='#1e293b')
        style.configure('Content.TFrame', background='#ffffff')

    def create_sidebar(self):
        sidebar = ttk.Frame(self.root, style='Sidebar.TFrame')
        sidebar.grid(row=0, column=0, sticky='nsew')

        # Logo et titre
        logo_frame = tk.Frame(sidebar, bg='#1e293b')
        logo_frame.pack(fill='x', pady=30)
        
        logo_label = tk.Label(logo_frame, 
                            text="🏥",
                            font=("Segoe UI Emoji", 32),
                            bg='#1e293b',
                            fg='white')
        logo_label.pack()
        
        title_label = tk.Label(logo_frame,
                             text="Espace Médical",
                             font=("Helvetica Neue", 16, "bold"),
                             bg='#1e293b',
                             fg='white')
        title_label.pack(pady=(10, 0))

        # Menu items avec icônes
        menu_items = [
            ("Gestion Ressource", "📊", self.open_gestionressource, "#10b981"),
            ("Gestion Employés", "👥", self.open_add_user_window, "#8b5cf6"),
            ("Déconnexion", "🚪", self.logout, "#ef4444")
        ]
        
        for text, icon, command, color in menu_items:
            self.create_menu_item(sidebar, text, icon, command, color)

    def create_menu_item(self, parent, text, icon, command, color):
        btn_frame = tk.Frame(parent, bg='#1e293b', padx=20)
        btn_frame.pack(fill='x', pady=2)
        btn_frame.bind('<Button-1>', lambda e: command())
        
        # Hover effects
        btn_frame.bind('<Enter>', lambda e: self.menu_hover(btn_frame, True))
        btn_frame.bind('<Leave>', lambda e: self.menu_hover(btn_frame, False))
        
        icon_label = tk.Label(btn_frame,
                            text=icon,
                            font=("Segoe UI Emoji", 20),
                            bg='#1e293b',
                            fg=color)
        icon_label.pack(side='left', pady=12)
        
        text_label = tk.Label(btn_frame,
                            text=text,
                            font=("Helvetica Neue", 13),
                            bg='#1e293b',
                            fg='#94a3b8')
        text_label.pack(side='left', padx=(15, 0), pady=12)

    def menu_hover(self, frame, entering):
        new_bg = '#2d3748' if entering else '#1e293b'
        frame.configure(bg=new_bg)
        for child in frame.winfo_children():
            if isinstance(child, tk.Label) and child.cget('fg') != '#94a3b8':
                continue
            child.configure(bg=new_bg)

    def create_main_content(self):
        content = ttk.Frame(self.root, style='Content.TFrame')
        content.grid(row=0, column=1, sticky='nsew')
        
        # En-tête
        header = tk.Frame(content, bg='white')
        header.pack(fill='x', padx=40, pady=30)
        
        welcome_text = tk.Label(header,
                              text=f"Bienvenue, {self.role.capitalize()}",
                              font=("Helvetica Neue", 28, "bold"),
                              bg='white',
                              fg='#1e293b')
        welcome_text.pack(side='left')

        # Zone des cartes
        cards_frame = tk.Frame(content, bg='white')
        cards_frame.pack(fill='x', padx=40)
        
        # Grille de cartes modernes
        self.create_feature_cards(cards_frame)

    def create_feature_cards(self, parent):
        features = [
            {
                "title": "Gestion des Ressources",
                "icon": "📊",
                "color": "#10b981",
                "command": self.open_gestionressource
            },
            {
                "title": "Gestion des Employés",
                "icon": "👥",
                "color": "#8b5cf6",
                "command": self.open_add_user_window
            }
        ]
        
        for feature in features:
            self.create_feature_card(parent, feature)

    def create_feature_card(self, parent, feature):
        card = tk.Frame(parent, bg='white', relief='solid', bd=1)
        card.pack(side='left', expand=True, fill='both', padx=10, pady=10)
        
        # Ombre portée
        card.configure(highlightbackground="#e5e7eb", highlightthickness=1)
        
        icon = tk.Label(card,
                       text=feature["icon"],
                       font=("Segoe UI Emoji", 48),
                       bg='white',
                       fg=feature["color"])
        icon.pack(pady=(30, 15))
        
        title = tk.Label(card,
                        text=feature["title"],
                        font=("Helvetica Neue", 16, "bold"),
                        bg='white',
                        fg='#1e293b')
        title.pack(pady=(0, 30))
        
        btn = ModernButton(card,
                          text="Accéder",
                          command=feature["command"],
                          bg_color=feature["color"],
                          width=150)
        btn.pack(pady=(0, 30))


    def open_gestionressource(self):
        subprocess.Popen(["python", "gestionressources_interface.py"])

    def open_add_user_window(self):
        subprocess.Popen(["python", "createuser2.py"])

    def logout(self):
        self.root.destroy()
        from Login import LoginPage
        new_root = tk.Tk()
        LoginPage(new_root)
        new_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = HomePage(root, "admin")
    root.mainloop()
