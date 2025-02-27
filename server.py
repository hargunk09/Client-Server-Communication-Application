#IMPORTS
import socket
import threading
import datetime
import os

# configuring the server
HOST = "172.20.10.4"
PORT = 12345 
MAX_CLIENTS = 3  # this is the number of maximum clients allowed
FILE_DIRECTORY = "server_files"  # this is the folder where the server stores the files

# the following code is to store the clients that are connected
clients = {}
lock = threading.Lock()

# the following code is to make sure that the file directory is detected
if not os.path.exists(FILE_DIRECTORY):
    os.makedirs(FILE_DIRECTORY)

# the following function is to handle each connected client
def handle_client(client_socket, client_address, client_name):
    global clients
    with lock:
        clients[client_name] = {
            "address": client_address,
            "connected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    print(f"[+] {client_name} connected from {client_address}")

    while True:
        try:
            message = client_socket.recv(1024).decode("utf-8")
            if not message:
                break

            if message.lower() == "exit":
                print(f"[-] {client_name} disconnected.")
                break

            elif message.lower() == "status":
                status_message = "\n".join([f"{name} - {info['address']} - Connected at: {info['connected_at']}" for name, info in clients.items()])
                client_socket.sendall(status_message.encode("utf-8"))

		# the following code shows whether files are available or not
            elif message.lower() == "list":
                files = os.listdir(FILE_DIRECTORY)
                file_list = "\n".join(files) if files else "No files are available."
                client_socket.sendall(file_list.encode("utf-8"))

		# the following code is to request a file
            elif message.lower().startswith("get "):
                filename = message[4:].strip()
                file_path = os.path.join(FILE_DIRECTORY, filename)

                if os.path.exists(file_path):
                    client_socket.sendall(f"START {filename}".encode("utf-8"))
                    with open(file_path, "rb") as file:
                        while chunk := file.read(1024):
                            client_socket.sendall(chunk)
                    client_socket.sendall(b"END_OF_FILE")
                else:
                    client_socket.sendall("Error: File was not detected.".encode("utf-8"))

            else:
                response = f"ACK: {message}"
                client_socket.sendall(response.encode("utf-8"))

        except ConnectionResetError:
            break

    with lock:
        del clients[client_name]
    client_socket.close()

# initiating the server
def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(MAX_CLIENTS)
    print(f"[*] Server started on {HOST}:{PORT}")

    while True:
        if len(clients) < MAX_CLIENTS:
            client_socket, client_address = server_socket.accept()
            client_name = f"Client{len(clients) + 1:02d}"

            client_thread = threading.Thread(target=handle_client, args=(client_socket, client_address, client_name))
            client_thread.start()
        else:
            print("[!] Maximum number of clients reached. All new connections will be denied.")

if __name__ == "__main__":
    start_server()

# end of code