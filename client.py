#IMPORTS
import socket
import os
import platform

# details needed for the server
HOST = "172.20.10.4"  # Host needs to change to actual server IP if we’re running it on a network
PORT = 12345

# operating system detection and setting the relevant download directory
if platform.system() == "Windows":
    DOWNLOAD_DIR = os.path.join(os.environ["USERPROFILE"], "Downloads", "client_downloads")
else:
    DOWNLOAD_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "client_downloads")

# the following code is to make sure that the download directory is existing
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def start_client():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        client_socket.connect((HOST, PORT))
        print(f"[*] Connected successful to the server at {HOST}:{PORT}.")
        print("Type your messages and/or commands ('status', 'list', 'get <filename>', 'exit').")

        while True:
            message = input("You: ").strip()
            if not message:
                continue  # this is to ignore any empty input

            client_socket.sendall(message.encode("utf-8"))

		# disconnection from the server
            if message.lower() == "exit":
                print("[*] Disconnecting from server...")
                break

            response = client_socket.recv(1024).decode("utf-8")

            if response.startswith("START "):  # to receive a file
                filename = response.split(" ", 1)[1]
                filepath = os.path.join(DOWNLOAD_DIR, filename)
                print(f"[*] Receiving file: {filename}...")

                with open(filepath, "wb") as file:
                    while True:
                        chunk = client_socket.recv(1024)
                        if b"END_OF_FILE" in chunk:
                            file.write(chunk.replace(b"END_OF_FILE", b""))
                            print(f"[â] File '{filename}' successfully received at {filepath}.")
                            break
                        file.write(chunk)
		
		# print the following if the file isn’t detected
            elif response == "Error: File was not detected.":
                print("[!] The requested file was not detected on the server.")

            else:
                print(f"Server: {response}")

    except ConnectionRefusedError:
        print("[!] The server is not running or the connection was refused. Please make sure the server is active.")
    
    except Exception as e:
        print(f"[!] An error occurred: {e}")

    finally:
        client_socket.close()

if __name__ == "__main__":
    start_client()

# end of code