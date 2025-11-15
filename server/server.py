import socket
import threading
import random

HOST = "127.0.0.1"
PORT = 65432

waiting_client = None
lock = threading.Lock()

def StripSelectedAndTo(selected, to):
    Strip_Selected = selected[8:]  #removing "selected:"
    Strip_To = to[2:]              #removing "to:"
    return Strip_Selected, Strip_To

def BoardAfterMove(selected, to, board):
    selected, to = StripSelectedAndTo(selected, to)
    sel_row, sel_col = int(selected[0]), int(selected[2])
    to_row, to_col = int(to[0]), int(to[2])
    piece = board[sel_row][sel_col]
    board[to_row][to_col] = piece
    board[sel_row][sel_col] = " "
    return board

def IsValidMove(selected, to, board, turn):
    selected, to = StripSelectedAndTo(selected, to)
    sel_row, sel_col = int(selected[0]), int(selected[2])
    to_row, to_col = int(to[0]), int(to[2])
    piece = board[sel_row][sel_col]
    endPiece = board[to_row][to_col]

    if piece == " ":
        return False
    
    if piece[0] == endPiece[0]:
        return False

    if (piece[0] == "B" and turn != 2) or (piece[0] == "W" and turn != 1):
        return False
    
    if piece[1] == "P":  #pawn movement
        direction = -1 if piece[0] == "W" else 1
        start_row = 6 if piece[0] == "W" else 1

        if sel_col == to_col:
            if endPiece != " ":
                return False
            if to_row - sel_row == direction:
                return True
            if sel_row == start_row and to_row - sel_row == 2 * direction:
                between_row = sel_row + direction
                if board[between_row][sel_col] == " " and endPiece == " ":
                    return True
        elif abs(sel_col - to_col) == 1 and to_row - sel_row == direction:
            if endPiece != " ":
                return True
        return False
    
    if piece[1] == "R":  #rook movement
        if sel_row != to_row and sel_col != to_col:
            return False
        step_row = 0 if sel_row == to_row else (1 if to_row > sel_row else -1)
        step_col = 0 if sel_col == to_col else (1 if to_col > sel_col else -1)
        curr_row, curr_col = sel_row + step_row, sel_col + step_col
        while (curr_row != to_row or curr_col != to_col):
            if board[curr_row][curr_col] != " ":
                return False
            curr_row += step_row
            curr_col += step_col
        return True
    
    if piece[1] == "K":  #king movement
        if abs(sel_row - to_row) <= 1 and abs(sel_col - to_col) <= 1:
            return True
        return False
    
    if piece[1] == "B":  #bishop movement
        if abs(sel_row - to_row) != abs(sel_col - to_col):
            return False
        step_row = 1 if to_row > sel_row else -1
        step_col = 1 if to_col > sel_col else -1
        curr_row, curr_col = sel_row + step_row, sel_col + step_col
        while (curr_row != to_row and curr_col != to_col):
            if board[curr_row][curr_col] != " ":
                return False
            curr_row += step_row
            curr_col += step_col
        return True
    
    if piece[1] == "Q":  #queen movement
        if sel_row == to_row or sel_col == to_col:
            step_row = 0 if sel_row == to_row else (1 if to_row > sel_row else -1)
            step_col = 0 if sel_col == to_col else (1 if to_col > sel_col else -1)
        elif abs(sel_row - to_row) == abs(sel_col - to_col):
            step_row = 1 if to_row > sel_row else -1
            step_col = 1 if to_col > sel_col else -1
        else:
            return False
        curr_row, curr_col = sel_row + step_row, sel_col + step_col
        while (curr_row != to_row or curr_col != to_col):
            if board[curr_row][curr_col] != " ":
                return False
            curr_row += step_row
            curr_col += step_col
        return True
    
    if piece[1] == "N":  #knight movement
        if (abs(sel_row - to_row) == 2 and abs(sel_col - to_col) == 1) or (abs(sel_row - to_row) == 1 and abs(sel_col - to_col) == 2):
            return True
        return False
    
    return True
    


def SendMassageToClients(clients, selected, to):
    Strip_Selected, Strip_To = StripSelectedAndTo(selected, to)
    message = f"move:{Strip_Selected}|{Strip_To}\n"
    print(message)
    for client in clients:
        try:
            client.sendall(message.encode())
        except OSError:
            pass

def handle_pair(client1, client2, num):
    """Forward every message from one client to both clients (echo)."""
    clients = [client1, client2]
    turn = 1 if num == 1 else 2

    board =       [["BR","BN","BB","BQ","BK","BB","BN","BR"],
                      ["BP","BP","BP","BP","BP","BP","BP","BP"],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      ["WP","WP","WP","WP","WP","WP","WP","WP"],
                      ["WR","WN","WB","WQ","WK","WB","WN","WR"]]
    selected = None
    to = None
    turn = 1        # #1 for white, #2 for black

    def forward(src, dsts):
        nonlocal board, turn, selected, to
        try:
            while True:
                data = src.recv(1024)
                if not data:
                    break
                print("Received:", data.decode().strip())
                # Echo to ALL clients (including sender)

                if data.decode().startswith("selected"):
                    selected = data.decode() #get selected coordinate
                    to = None

                elif data.decode().startswith("to"):
                    to = data.decode() #Get to coordinates and then send it 
                    print(IsValidMove(selected, to, board, turn))
                    if IsValidMove(selected, to, board, turn):
                    
                        SendMassageToClients(clients, selected, to)
                        print(board)
                        board = BoardAfterMove(selected, to, board)
                        print(board)
                        turn = 3 - turn  #switch turn

                    selected = None
                    to = None



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
                threading.Thread(target=handle_pair, args=(client1, client2, num), daemon=True).start() #handle the paired clients in a new thread

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #main function listening, binding and accepting clients
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")
        accept_clients(s)

if __name__ == "__main__":
    main()
