from tkinter import ttk
import tkinter as tk

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


def setup_styles():
    style = ttk.Style()
    
    # Style principal
    style.configure("Main.TFrame", background="#ffffff")
    
    # Style pour l'en-tête
    style.configure("Header.TFrame", background="#1e293b")
    
    # Style pour la table
    style.configure("Treeview",
                    background="#ffffff",
                    foreground="#1e293b",
                    fieldbackground="#ffffff",
                    rowheight=40,
                    font=("Segoe UI", 11))
                    
    style.configure("Treeview.Heading",
                    background="#f8fafc",
                    foreground="#1e293b",
                    relief="flat",
                    font=("Segoe UI", 11, "bold"))
                    
    style.map("Treeview.Heading",
                background=[("active", "#f1f5f9")])
                
    # Style pour les Combobox
    style.configure("Custom.TCombobox",
                    background="#ffffff",
                    arrowcolor="#2563eb",
                    foreground="#1e293b")
    
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
        
        # Forcer la mise à jour des dimensions avant de dessiner
        self.update_idletasks()
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
        
        # Si les dimensions ne sont pas disponibles, utiliser les dimensions par défaut
        if not width or not height:
            width = 200  # Largeur par défaut
            height = 40  # Hauteur par défaut
        
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