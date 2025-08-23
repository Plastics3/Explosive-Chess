import socket
import threading

HOST = "127.0.0.1"
PORT = 65432

waiting_client = None
lock = threading.Lock()

def handle_pair(client1, client2):
    """Forward every message from one client to both clients (echo)."""
    clients = [client1, client2]

    def forward(src, dsts):
        try:
            while True:
                data = src.recv(1024)
                if not data:
                    break
                # Echo to ALL clients (including sender)
                for d in dsts:
                    try:
                        d.sendall(data)
                    except OSError:
                        pass
        except (ConnectionResetError, OSError):
            pass
        finally:
            for c in dsts:
                try:
                    c.close()
                except OSError:
                    pass

    # Start one thread per direction
    threading.Thread(target=forward, args=(client1, clients), daemon=True).start()
    threading.Thread(target=forward, args=(client2, clients), daemon=True).start()

def accept_clients(server_socket):
    global waiting_client
    while True:
        client, addr = server_socket.accept()
        print("Client connected:", addr)

        with lock:
            if waiting_client is None:
                waiting_client = client
                print("Waiting for another client...")
            else:
                client1 = waiting_client
                client2 = client
                waiting_client = None
                print("Pair created!")
                try:
                    client1.sendall(b"start\n")
                    client2.sendall(b"start\n")
                except OSError:
                    pass
                threading.Thread(target=handle_pair, args=(client1, client2), daemon=True).start()

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        accept_clients(s)

if __name__ == "__main__":
    main()
