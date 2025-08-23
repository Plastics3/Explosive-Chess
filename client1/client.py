import pygame
import sys, os,re,time,math
import socket
import threading
import queue

Player_number = 1
Player = f"Player {Player_number}"

HOST = "127.0.0.1"  
PORT = 65432
    
lock = threading.Lock()
messages = queue.Queue()
start = False
#messages
def listen_for_messages(sock):
    buffer = ""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                print("Disconnected from server")
                break
            buffer += data.decode()
            while "\n" in buffer:
                msg, buffer = buffer.split("\n", 1)
                messages.put(msg)
        except:
            break

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Connected to server, waiting for partner...")

# Start listener thread
threading.Thread(target=listen_for_messages, args=(s,), daemon=True).start()

#colors
LIGHT = (240, 217, 181)
DARK  = (181, 136, 99)
BG_TOP = (30, 30, 60)
BG_BOTTOM = (10, 10, 30)
TEXT_COLOR = (255, 255, 255)
CIRCLE_COLOR = (100, 200, 255)

#waiting screen
pygame.init()

Square_Size = 160
Row, Col = 8, 8
WIDTH, HEIGHT = Square_Size * Col, Square_Size * Row
screen = pygame.display.set_mode((WIDTH,HEIGHT))
font = pygame.font.SysFont("Arial", 48, bold=True)
small_font = pygame.font.SysFont("Arial", 32)
clock = pygame.time.Clock()
start_time = time.time()
#waiting screen look
def draw_gradient_background():
    # vertical gradient
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = BG_TOP[0] * (1 - ratio) + BG_BOTTOM[0] * ratio
        g = BG_TOP[1] * (1 - ratio) + BG_BOTTOM[1] * ratio
        b = BG_TOP[2] * (1 - ratio) + BG_BOTTOM[2] * ratio
        pygame.draw.line(screen, (int(r), int(g), int(b)), (0, y), (WIDTH, y))

def draw_loading_circles(elapsed):
    # Animate circles in a circular orbit
    num_circles = 8
    radius = 100
    center_x, center_y = WIDTH // 2, HEIGHT // 2 + 50

    for i in range(num_circles):
        angle = elapsed * 2 + i * (2 * math.pi / num_circles)
        x = int(center_x + radius * math.cos(angle))
        y = int(center_y + radius * math.sin(angle))
        pygame.draw.circle(screen, CIRCLE_COLOR, (x, y - 100), 15)

#waiting to start
while(start == False):
    elapsed = time.time() - start_time
    draw_gradient_background()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit
            quit()
    text_surface = font.render("Waiting for Partner...", True, TEXT_COLOR)
    text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 300))
    screen.blit(text_surface, text_rect)

    draw_loading_circles(elapsed)

    hint_surface = small_font.render("Please wait...", True, TEXT_COLOR)
    hint_rect = hint_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))
    screen.blit(hint_surface, hint_rect)

    while not messages.empty():
        msg = messages.get()
        if msg == "start":
            start = True

    pygame.display.flip()
    clock.tick(120)


#layout
Run = True
selected = None

piece_images = {}
piece_names = ["P", "R", "N", "B", "Q", "K"]
for name in piece_names:
    piece_images["W"+name] = pygame.image.load(os.path.join("pieces", f"W{name}.png"))
    piece_images["B"+name] = pygame.image.load(os.path.join("pieces", f"B{name}.png"))


# Scale images to tile size
for key in piece_images:
    piece_images[key] = pygame.transform.smoothscale(piece_images[key], (Square_Size, Square_Size))


# Starting position (FEN-like layout)
if Player_number == 1:
    board =           [["BR","BN","BB","BQ","BK","BB","BN","BR"],
                      ["BP","BP","BP","BP","BP","BP","BP","BP"],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      ["WP","WP","WP","WP","WP","WP","WP","WP"],
                      ["WR","WN","WB","WQ","WK","WB","WN","WR"]]
else:
    board =           [["WR","WN","WB","WQ","WK","WB","WN","WR"],
                      ["WP","WP","WP","WP","WP","WP","WP","WP"],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      ["BP","BP","BP","BP","BP","BP","BP","BP"],
                      ["BR","BN","BB","BQ","BK","BB","BN","BR"]]

def Start():
    if Player_number == 1:
        board =       [["BR","BN","BB","BQ","BK","BB","BN","BR"],
                      ["BP","BP","BP","BP","BP","BP","BP","BP"],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      ["WP","WP","WP","WP","WP","WP","WP","WP"],
                      ["WR","WN","WB","WQ","WK","WB","WN","WR"]]
    else:
        board =       [["WR","WN","WB","WQ","WK","WB","WN","WR"],
                      ["WP","WP","WP","WP","WP","WP","WP","WP"],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      [" "," "," "," "," "," "," "," "],
                      ["BP","BP","BP","BP","BP","BP","BP","BP"],
                      ["BR","BN","BB","BQ","BK","BB","BN","BR"]]

#Tile color
def Tile_Color(ColAndRow):
    if Player_number == 1:
        return LIGHT if ColAndRow % 2 == 0 else DARK

    return LIGHT if ColAndRow % 2 == 1 else DARK

#board
def Board(surf):
    pygame.image.load(os.path.join("pieces", "BQ.png"))
    for row in range(8):
        for col in range(8):
            color = Tile_Color(col+row)
            rect = (col * Square_Size, row * Square_Size, Square_Size, Square_Size)
            pygame.draw.rect(surf, color, rect)

            piece = board[row][col]
            if piece != " ":
                surf.blit(piece_images[piece], (col*Square_Size, row*Square_Size))

#getting the coords
def String_with_letters_to_tuple(msg: str):
    nums = re.findall(r"\d+", msg)
    if len(nums) != 2:
        print("Bad message:", msg)
        return None
    return int(nums[0]), int(nums[1])

my_color = "W" if Player_number == 1 else "B"
mouse_x, mouse_y = 0,0        
Turn = True
clock = pygame.time.Clock()
Turn = (my_color == "W") 

#game

while Run:
#sending
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            Run = False

        elif event.type == pygame.MOUSEBUTTONDOWN and Turn:
            mouse_x, mouse_y = event.pos
            col, row = mouse_x // Square_Size, mouse_y // Square_Size

            if selected is None:
                piece = board[row][col]
                if piece != " " and piece[0] == my_color:
                    selected = (row, col)
                    if Player_number == 2:
                        s.sendall(f"selected{7-row},{col}\n".encode())
                        print(f"Sent selection {7-row},{col}")
                    else:
                        s.sendall(f"selected{row},{col}\n".encode())
                        print(f"Sent selection {row},{col}")
            else:
                to_row, to_col = row, col
                from_row, from_col = selected

                if (to_row, to_col) == (from_row, from_col):
                    selected = None 
                else:
                    if Player_number == 2:
                        s.sendall(f"to{7-to_row},{to_col}\n".encode())
                        print(f"Sent move to {7-to_row},{to_col}")
                    else:
                        s.sendall(f"to{to_row},{to_col}\n".encode())
                        print(f"Sent move to {to_row},{to_col}")
                    selected = None
                    Turn = False

#reciving
    while not messages.empty():
        msg = messages.get()

        if msg.startswith("selected"):
            coords = String_with_letters_to_tuple(msg)
            if coords:
                remote_selected = coords
                print("Partner selected", coords)

        elif msg.startswith("to"):
            to_coords = String_with_letters_to_tuple(msg)
            if to_coords and remote_selected is not None:
                fr = remote_selected
                tr = to_coords
                if Player_number == 2:
                    piece = board[7-fr[0]][fr[1]]
                    board[7-fr[0]][fr[1]] = " "
                    board[7-to_coords[0]][to_coords[1]] = piece
                else:
                    piece = board[fr[0]][fr[1]]
                    board[fr[0]][fr[1]] = " "
                    board[to_coords[0]][to_coords[1]] = piece
                remote_selected = None
                Turn = True  
                print("Partner moved to", tr)
        

    
    Board(screen)
    pygame.display.flip()
    clock.tick(60)


pygame.quit()