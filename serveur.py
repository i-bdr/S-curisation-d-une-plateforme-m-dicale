import socket
import random
from threading import Thread

class ChatServer:
    def __init__(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('127.0.0.1', 12345))
        self.server_socket.listen(5)
        self.clients = []
        self.user_roles = []  

    def handle_client(self, client_socket):
        role = client_socket.recv(1024).decode()
        self.user_roles.append(role)
        
        while True:
            try:
                message = client_socket.recv(1024)
                if message == b"REQUEST_TRUSTED_PARTY":
                    trusted_party = random.choice(self.user_roles)
                    client_socket.sendall(trusted_party.encode())
                elif message:
                    self.broadcast(message)
                else:
                    break
            except:
                break

        # Déconnexion du client
        client_socket.close()
        self.clients.remove(client_socket)
        self.user_roles.remove(role)

    def broadcast(self, message):
        """Diffuse un message à tous les clients connectés."""
        for client in self.clients:
            try:
                client.send(message)
            except:
                pass  

    def run(self):
        print("Le serveur est en cours d'exécution...")
        while True:
            client_socket, addr = self.server_socket.accept()
            self.clients.append(client_socket)
            print(f"{addr} connecté.")
            thread = Thread(target=self.handle_client, args=(client_socket,))
            thread.start()

    def check_policy(self, role, resource, policy):
        """Vérifie si l'utilisateur a la politique sur la ressource."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        query = """
        SELECT COUNT(*) FROM permissions 
        WHERE user = ? AND resource = ? AND policy = ?
        """
        cursor.execute(query, (role, resource, policy))
        result = cursor.fetchone()
        conn.close()
        return "Accepted" if result[0] > 0 else "Denied"
    
if __name__ == "__main__":
    server = ChatServer()
    server.run()
