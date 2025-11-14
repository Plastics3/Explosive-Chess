import socket
import threading
import random

HOST = "127.0.0.1"
PORT = 65432

waiting_client = None
lock = threading.Lock()

def SendMassageToClients(clients, selected, to):
    Strip_Selected = selected[8:]  #removing "selected:"
    Strip_To = to[2:]              #removing "to:"
    message = f"move:{Strip_Selected}|{Strip_To}\n"
    print(message)
    for client in clients:
        try:
            client.sendall(message.encode())
        except OSError:
            pass

def handle_pair(client1, client2):
    """Forward every message from one client to both clients (echo)."""
    clients = [client1, client2]
    board =       [["WR","WN","WB","WQ","WK","WB","WN","WR"],
                      ["WP","WP","WP","WP","WP","WP","WP","WP"],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      ["BP","BP","BP","BP","BP","BP","BP","BP"],
                      ["BR","BN","BB","BQ","BK","BB","BN","BR"]]
    

    def forward(src, dsts):
        selected = None
        to = None
        try:
            while True:
                data = src.recv(1024)
                if not data:
                    break
                # Echo to ALL clients (including sender)
                if data.decode().startswith("selected"):
                    selected = data.decode() #get selected coordinate

                elif data.decode().startswith("to"):
                    to = data.decode() #Get to coordinates and then send it 
                    SendMassageToClients(clients, selected, to)

        except (ConnectionResetError, OSError):
            pass #catch disconnection
        finally:
            for c in dsts:
                try:
                    c.close() #close all clients if one disconnects
                except OSError:
                    pass

    # Start one thread per direction
    threading.Thread(target=forward, args=(client1, clients), daemon=True).start()
    threading.Thread(target=forward, args=(client2, clients), daemon=True).start()

def accept_clients(server_socket):
    global waiting_client
    while True:
        client, addr = server_socket.accept() #accepting
        print("Client connected:", addr)

        with lock:
            if waiting_client is None:
                waiting_client = client #when no waiting client, set the current client as waiting
                print("Waiting for another client...") 
            else:
                client1 = waiting_client #when there is a waiting client, pair them
                client2 = client
                waiting_client = None
                print("Pair created!")
                try:
                    client1.sendall(b"start\n") #send start message to both clients
                    client2.sendall(b"start\n")
                    num = random.randint(1, 2)
                    client1.sendall(f"num{num}\n".encode()) #send random player numbers
                    client2.sendall(f"num{3 - num}\n".encode())

                except OSError:
                    pass
                threading.Thread(target=handle_pair, args=(client1, client2), daemon=True).start() #handle the paired clients in a new thread

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #main function listening, binding and accepting clients
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        accept_clients(s)

if __name__ == "__main__":
    main()
