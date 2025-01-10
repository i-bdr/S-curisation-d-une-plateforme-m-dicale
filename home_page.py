import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import socket
from PIL import Image, ImageTk, ImageDraw
from access_page import AccessPage
from user_session import UserSession
from gestion_inteface.getAllStats import get_all_stats


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
        
        radius = 12
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


class HomePage:
    def __init__(self, root, role):
        self.root = root
        self.role = role
        self.user_session = UserSession.get_instance()
        self.server_address = ('127.0.0.1', 12345)
        self.client_socket = self.connect_to_server()
        self.setup_ui()
        
    def connect_to_server(self):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(self.server_address)
            client_socket.sendall(self.role.encode())
            return client_socket
        except ConnectionRefusedError:
            messagebox.showerror("Erreur", "Connexion au serveur impossible.")
            return None
        
    def setup_ui(self):
        self.root.title(f"Espace Médical - {self.role.capitalize()}")
        self.root.geometry("1200x800")
        self.root.configure(bg='#ffffff')
        
        self.setup_styles()
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        self.create_sidebar()
        self.create_main_content()
        
    def setup_styles(self):
        style = ttk.Style()
        style.configure('Sidebar.TFrame', background='#1e293b')
        style.configure('Content.TFrame', background='#ffffff')
        style.configure('Card.TFrame', background='#ffffff')
        
    def create_sidebar(self):
        sidebar = ttk.Frame(self.root, style='Sidebar.TFrame')
        sidebar.grid(row=0, column=0, sticky='nsew')

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

        menu_items = [
            ("Management", "📊", self.open_management, "#3b82f6"),
            ("Historique", "📝", self.open_historique, "#10b981"),
            ("Accès", "🔒", self.open_access, "#f59e0b"),
            ("Déconnexion", "🚪", self.logout, "#ef4444")
        ]

        for text, icon, command, color in menu_items:
            self.create_menu_item(sidebar, text, icon, command, color)

    def create_menu_item(self, parent, text, icon, command, color):
        btn_frame = tk.Frame(parent, bg='#1e293b')
        btn_frame.pack(fill='x', pady=2, padx=10)

        inner_frame = tk.Frame(btn_frame, bg='#1e293b')
        inner_frame.pack(fill='x', padx=10, pady=5)

        for frame in (btn_frame, inner_frame):
            frame.bind('<Button-1>', lambda e: command())
            frame.bind('<Enter>', lambda e: self.menu_hover(inner_frame, True))
            frame.bind('<Leave>', lambda e: self.menu_hover(inner_frame, False))

        icon_label = tk.Label(inner_frame,
                            text=icon,
                            font=("Segoe UI Emoji", 20),
                            bg='#1e293b',
                            fg=color)
        icon_label.pack(side='left', padx=(20, 10))

        text_label = tk.Label(inner_frame,
                            text=text,
                            font=("Helvetica Neue", 13),
                            bg='#1e293b',
                            fg='#94a3b8')
        text_label.pack(side='left')

    def menu_hover(self, frame, entering):
        new_bg = '#2d3748' if entering else '#1e293b'
        frame.configure(bg=new_bg)
        for child in frame.winfo_children():
            child.configure(bg=new_bg)
            if isinstance(child, tk.Label) and not child.cget('fg').startswith('#'):
                child.configure(fg='white' if entering else '#94a3b8')

    def create_main_content(self):
        main_frame = ttk.Frame(self.root, style='Content.TFrame')
        main_frame.grid(row=0, column=1, sticky='nsew', padx=40, pady=40)

        header_frame = tk.Frame(main_frame, bg='white')
        header_frame.pack(fill='x', pady=(0, 30))

        user_data = self.user_session.get_user()
        if user_data:
            welcome_label = tk.Label(header_frame,
                                text=f"Bienvenue, {user_data['role']} {user_data['prenom']} {user_data['nom']}",
                                font=("Helvetica Neue", 28, "bold"),
                                bg='white',
                                fg='#1e293b')
        else:
            welcome_label = tk.Label(header_frame,
                                text="Bienvenue",
                                font=("Helvetica Neue", 28, "bold"),
                                bg='white',
                                fg='#1e293b')
        welcome_label.pack(side='left')

        self.create_stats_section(main_frame)

    def create_stats_section(self, parent):
        stats_frame = tk.Frame(parent, bg='white')
        stats_frame.pack(fill='x', pady=20)
        data = get_all_stats()
        print(data)
        stats = [
            ("Demandes en cours", data['nombre_demandes'], "#3b82f6", "📈"),
            ("Ressources actives", data['nombre_ressources_actives'], "#10b981", "📊"),
            ("Notifications", "3", "#f59e0b", "🔔")
        ]

        for title, value, color, icon in stats:
            self.create_stat_card(stats_frame, title, value, color, icon)

    def create_stat_card(self, parent, title, value, color, icon):
        card = tk.Frame(parent, bg='white')
        card.pack(side='left', expand=True, fill='both', padx=10)
        
        card.configure(relief='solid', bd=1, highlightbackground="#e5e7eb", highlightthickness=1)

        icon_frame = tk.Frame(card, bg='white')
        icon_frame.pack(fill='x', padx=20, pady=(20, 0))

        icon_label = tk.Label(icon_frame,
                            text=icon,
                            font=("Segoe UI Emoji", 24),
                            bg='white',
                            fg=color)
        icon_label.pack(side='left')

        value_label = tk.Label(card,
                             text=value,
                             font=("Helvetica Neue", 36, "bold"),
                             bg='white',
                             fg=color)
        value_label.pack(pady=(10, 5))

        title_label = tk.Label(card,
                             text=title,
                             font=("Helvetica Neue", 14),
                             bg='white',
                             fg='#64748b')
        title_label.pack(pady=(0, 20))

    def open_management(self):
        try:
            subprocess.Popen(["python", "home_page2.py"])
        except FileNotFoundError:
            messagebox.showerror("Erreur", "Fichier 'home_page2.py' introuvable.")

    def open_historique(self):
        user_data = self.user_session.get_user()
        if not user_data:
            messagebox.showerror("Erreur", "Aucun utilisateur connecté. Veuillez vous reconnecter.")
            return

        subprocess.Popen([
            "python", "access_page.py",
            str(user_data['iduser']),
            user_data['nom'],
            user_data['prenom'],
            user_data['role']
        ])



    def open_access(self):
        if self.client_socket:
            from request_resource import open_request_resource
            open_request_resource(self.root, self.client_socket, self.role)
        else:
            messagebox.showerror("Erreur", "Connexion au serveur non établie.")


    def logout(self):
        self.user_session.clear_user()
        self.root.destroy()
        from Login import SecureLandingPage  
        new_root = tk.Tk()
        SecureLandingPage(new_root)
        new_root.mainloop()

if __name__ == "__main__":
    root = tk.Tk()
    app = HomePage(root, "admin")
    root.mainloop()