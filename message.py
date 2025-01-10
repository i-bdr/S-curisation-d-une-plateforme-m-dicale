import socket
import tkinter as tk
from threading import Thread

# Configuration de la connexion (vous pouvez adapter l'adresse IP et le port)
SERVER_IP = '127.0.0.1'  # Utiliser l'IP de votre serveur si nécessaire
SERVER_PORT = 12345

class MessageClient:
    def __init__(self, master):
        self.master = master
        self.master.title("Discussion Diffie-Hellman")
        
        self.text_area = tk.Text(master, state='disabled')
        self.text_area.pack()

        self.entry_message = tk.Entry(master)
        self.entry_message.pack()

        self.send_button = tk.Button(master, text="Envoyer", command=self.send_message)
        self.send_button.pack()

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((SERVER_IP, SERVER_PORT))

        self.receive_thread = Thread(target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self):
        message = self.entry_message.get()
        if message:
            self.client_socket.send(message.encode())
            self.entry_message.delete(0, tk.END)

    def receive_messages(self):
        while True:
            message = self.client_socket.recv(1024).decode()
            if message:
                self.text_area.config(state='normal')
                self.text_area.insert(tk.END, f"Autre: {message}\n")
                self.text_area.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    app = MessageClient(root)
    root.mainloop()
