import pygame
import sys, os,re,time,math
import socket
import threading
import queue

HOST = "127.0.0.1"  
PORT = 65432
                                            
pygame.init()                               # screen setup

Square_Size = 160                           # all of the measurements
Row, Col = 8, 8
WIDTH, HEIGHT = Square_Size * Col, Square_Size * Row
screen = pygame.display.set_mode((WIDTH,HEIGHT))
font = pygame.font.SysFont("Arial", 48, bold=True)
small_font = pygame.font.SysFont("Arial", 32)
clock = pygame.time.Clock()
start_time = time.time()

class Button:
    def __init__(self, x, y, w, h, text, font, bg_color, hover_color, text_color):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.text_color = text_color

    def draw(self, screen):
        mouse = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse) else self.bg_color

        pygame.draw.rect(screen, color, self.rect, border_radius=8)

        txt = self.font.render(self.text, True, self.text_color)
        txt_rect = txt.get_rect(center=self.rect.center)
        screen.blit(txt, txt_rect)

    def clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False

def ask_for_name(screen):                   # your name input screen
    font = pygame.font.SysFont("Arial", 50)
    input_box = pygame.Rect(WIDTH//2 - 200, HEIGHT//2 - 40, 400, 60)
    user_text = ""
    active = True

    while active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return user_text if user_text != "" else "Player"
                elif event.key == pygame.K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    if len(user_text) < 20:
                        user_text += event.unicode

        screen.fill((20, 20, 20))

        # Draw prompt
        text = font.render("Enter your name:", True, (255,255,255))
        screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - 120))

        # Draw input box
        pygame.draw.rect(screen, (255,255,255), input_box, 3)

        name_surface = font.render(user_text, True, (255,255,255))
        screen.blit(name_surface, (input_box.x + 10, input_box.y ))

        pygame.display.flip()
        clock.tick(60)

my_name = ask_for_name(screen)               # get player name

lock = threading.Lock()
messages = queue.Queue()
start = False
board = []

font_small = pygame.font.SysFont(None, 30)

resign_button = Button(
    x=160*7 + 40, y=0,
    w=120, h=40,
    text="Resign",
    font=font_small,
    bg_color=(180, 50, 50),
    hover_color=(220, 80, 80),
    text_color=(255, 255, 255)
)

                                            # messages
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

                                            # connecting to server
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))
print("Connected to server, waiting for partner...")

                                            # Start listener thread
threading.Thread(target=listen_for_messages, args=(s,), daemon=True).start()
s.sendall(f"name:{my_name}\n".encode())

                                            # colors
LIGHT = (240, 217, 181)
DARK  = (181, 136, 99)
BG_TOP = (30, 30, 60)
BG_BOTTOM = (10, 10, 30)
TEXT_COLOR = (255, 255, 255)
CIRCLE_COLOR = (100, 200, 255)

                                            # waiting screen

                                            # waiting screen look
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

                                            # waiting to start
while(start == False):
    elapsed = time.time() - start_time      # draw waiting screen
    draw_gradient_background()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:       # quit event
            pygame.quit
            quit()
    text_surface = font.render("Waiting for Partner...", True, TEXT_COLOR) # render text
    text_rect = text_surface.get_rect(center=(WIDTH//2, HEIGHT//2 - 300))  # get text rect
    screen.blit(text_surface, text_rect)

    draw_loading_circles(elapsed)           # draw loading circles

    hint_surface = small_font.render("Please wait...", True, TEXT_COLOR)
    hint_rect = hint_surface.get_rect(center=(WIDTH//2, HEIGHT//2 + 150))
    screen.blit(hint_surface, hint_rect)

    while not messages.empty():
        msg = messages.get()
        if msg == "start":
            start = True
        elif msg.startswith("num"):
            Player_number = int(msg[3:])
            print(f"Assigned as Player {Player_number}")
            Player = f"Player {Player_number}"

    pygame.display.flip()
    clock.tick(120)

                                            # layout
Run = True
selected = None

piece_images = {}
piece_names = ["P", "R", "N", "B", "Q", "K"]

for name in piece_names:                    # mapping piece names to images
    piece_images["W"+name] = pygame.image.load(os.path.join("pieces", f"W{name}.png"))
    piece_images["B"+name] = pygame.image.load(os.path.join("pieces", f"B{name}.png"))


                                            # Scale images to tile size
for key in piece_images:
    piece_images[key] = pygame.transform.smoothscale(piece_images[key], (Square_Size, Square_Size))


                                            # Starting position (FEN-like layout)
def StartBoard():
    
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
    return board
board = StartBoard()


                                            # Tile color
def Tile_Color(ColAndRow):
    if Player_number == 1:
        return LIGHT if ColAndRow % 2 == 0 else DARK

    return LIGHT if ColAndRow % 2 == 1 else DARK

                                            # board
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

def EndGame(board):
    white_king = False
    black_king = False
    for row in board:
        for piece in row:
            if piece == "WK":
                white_king = True
            elif piece == "BK":
                black_king = True
    if not white_king:
        return "Black wins!"
    if not black_king:
        return "White wins!"
    return ""

def Explotion(to, board):
    """Remove non-pawn pieces in the 3x3 area centered at `to` (row,col)."""
    print("Explosion at:", to)
    to_row, to_col = to[0], to[1]
    for r in range(to_row - 1, to_row + 2):
        for c in range(to_col - 1, to_col + 2):
            # check bounds first
            if 0 <= r < 8 and 0 <= c < 8:
                piece = board[r][c]
                # remove if tile not empty and not a pawn
                if piece != " " and len(piece) >= 2 and piece[1] != "P":
                    board[r][c] = " "

    center_x = to_col * Square_Size + Square_Size // 2
    center_y = to_row * Square_Size + Square_Size // 2
    for i in range(6):
        # redraw board and pieces (simple)
        Board(screen)
        # draw expanding translucent circle
        radius = 10 + i * 20
        surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        alpha = max(0, 180 - i*30)
        pygame.draw.circle(surf, (255, 80, 60, alpha), (radius, radius), radius)
        screen.blit(surf, (center_x - radius, center_y - radius))
        # redraw UI elements that should remain visible
        draw_player_info(screen, my_name, opponent_name, white_time, black_time, my_color)
        resign_button.draw(screen)
        pygame.display.flip()
        pygame.time.delay(40)

def IsValidMove(selected, to, board):
    sel_row, sel_col = selected[0], selected[1]
    to_row, to_col = to[0], to[1]
    piece = board[sel_row][sel_col]
    endPiece = board[to_row][to_col]

    if piece == " ":
        return False
    
    if piece[0] == endPiece[0]:
        return False
    
    if piece[1] == "P":  #pawn movement
        direction = -1 if piece[0] == "W" else 1
        start_row = 6 if piece[0] == "W" else 1
        if Player_number == 2:
            direction = -direction
            start_row = 7 - start_row

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

def game_over(screen, board, winner):
    """Displays the final board and allows player to return to matchmaking or exit."""

    font_big = pygame.font.SysFont("Arial", 90, bold=True)
    font_mid = pygame.font.SysFont("Arial", 50, bold=True)

    # Draw final board
    Board(screen)

    # Winner text
    msg = winner if winner != "Draw" else "It's a Draw!"
    text_surface = font_big.render(msg, True, (255, 215, 0))
    text_rect = text_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 200))

    # Overlay
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(170)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    # Draw text
    screen.blit(text_surface, text_rect)

    # --- Buttons ---
    play_text = font_mid.render("Play Again", True, (255, 255, 255))
    exit_text = font_mid.render("Exit Game", True, (255, 255, 255))

    play_rect = play_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
    exit_rect = exit_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 120))

    pygame.draw.rect(screen, (50, 150, 50), play_rect.inflate(40, 20), border_radius=20)
    pygame.draw.rect(screen, (150, 50, 50), exit_rect.inflate(40, 20), border_radius=20)

    screen.blit(play_text, play_rect)
    screen.blit(exit_text, exit_rect)

    pygame.display.flip()

    # --- Wait for click ---
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "exit"

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                if play_rect.inflate(40, 20).collidepoint(mx, my):
                    return "matchmaking"

                if exit_rect.inflate(40, 20).collidepoint(mx, my):
                    return "exit"

        pygame.time.delay(10)



def StripStringFromMove(msg: str):
                                            # Expect: "move:row,col|row,col"
    move = msg[5:]                          # remove the "move:" part
    parts = move.split("|") 
    return parts[0], parts[1]

                                            # getting the coords
def String_with_letters_to_tuple(msg: str):
    nums = re.findall(r"\d+", msg)
    if len(nums) != 2:
        print("Bad message:", msg)
        return None
    return int(nums[0]), int(nums[1])

my_color = "W" if Player_number == 1 else "B"
mouse_x, mouse_y = 0,0    
Turn = True if my_color == "W" else False
clock = pygame.time.Clock()
white_time = 5 * 60     # 5 minutes
black_time = 5 * 60
last_tick = time.time()
opponent_name = "Opponent"


def matchmaking():
    global s, messages, start, Player_number, board, my_color, Turn, selected, start_time

    # reset states
    messages = queue.Queue()
    start = False
    selected = None
    start_time = time.time()

    # reconnect to server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    print("Reconnected to server, waiting for partner...")

    threading.Thread(target=listen_for_messages, args=(s,), daemon=True).start()
    s.sendall(f"name:{my_name}\n".encode())

    # show same waiting screen you already have
    while start == False:
        elapsed = time.time() - start_time
        draw_gradient_background()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

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

            elif msg.startswith("num"):
                Player_number = int(msg[3:])
                print(f"Assigned as Player {Player_number}")

        pygame.display.flip()
        clock.tick(120)

    # after matchmaking finishes  
    board = StartBoard()
    my_color = "W" if Player_number == 1 else "B"
    Turn = True if my_color == "W" else False
                                            # game

def draw_player_info(screen, my_name, opponent_name, white_time, black_time, my_color):
    font = pygame.font.SysFont("Arial", 40)

    # Format time
    def fmt(t):
        m = int(t) // 60
        s = int(t) % 60
        return f"{m:02d}:{s:02d}"

    # White info top-left
    white_text = font.render(f"{opponent_name if my_color=='B' else my_name}  •  {fmt(white_time)}", True, (200,200,200))
    screen.blit(white_text, (20, 20))

    # Black info top-right
    black_text = font.render(f"{my_name if my_color=='B' else opponent_name}  •  {fmt(black_time)}", True, (200,200,200))
    screen.blit(black_text, (20, HEIGHT - 60))

while Run:
                                            # sending
    for event in pygame.event.get():
        if event.type == pygame.QUIT:       # quit event
            Run = False

        elif resign_button.clicked(event):
            s.sendall(f"{'Black wins!' if my_color == 'W' else 'White wins!'}".encode())

        elif event.type == pygame.MOUSEBUTTONDOWN: # getting the position of the mouse click by a square
                mouse_x, mouse_y = event.pos
                col, row = mouse_x // Square_Size, mouse_y // Square_Size

                if selected is None:            # first click - select piece
                    piece = board[row][col]

                    if piece != " " and piece[0] == my_color: # check if the piece belongs to the player
                        selected = (row, col)

                        if Player_number == 2:  # sending selected coords as black (player 2)
                            s.sendall(f"selected{7-row},{col}".encode())
                            print(f"Sent selection {7-row},{col}")

                        else:                   # sending selected coords as white (player 1) as selected(row,col)
                            s.sendall(f"selected{row},{col}".encode())
                            print(f"Sent selection {row},{col}")
                    
                    else:
                        selected = None

                elif selected != None and IsValidMove(selected, (row,col), board):  # second click - move piece or deselect
                    to_row, to_col = row, col
                    from_row, from_col = selected

                    if (to_row, to_col) == (from_row, from_col): #deselect if clicked same square
                        selected = None 

                    else:                       # send move as to(row,col)
                        Turn = False
                        if Player_number == 2:
                            s.sendall(f"to{7-to_row},{to_col}".encode())
                            print(f"Sent move to {7-to_row},{to_col}")

                        else:                   # sending move as white (player 1)
                            s.sendall(f"to{to_row},{to_col}".encode())
                            print(f"Sent move to {to_row},{to_col}")
                        selected = None
                        Turn = False

                else:
                    selected = None
                    

                                            # reciving
    while not messages.empty():
        
        msg = messages.get()
        print("Received message:", msg)
        if msg.startswith("move:"):         # removing "move:" and splitting to select and to
            selected_coords_String, to_coords_String = StripStringFromMove(msg)
            print(selected_coords_String)
            print(to_coords_String)

            coords = (int(selected_coords_String[0]),int(selected_coords_String[2])) # getting selected coords
            print(coords)
            if coords:
                remote_selected = coords
                print("Partner selected", coords)

            to_coords = (int(to_coords_String[0]),int(to_coords_String[2])) #getting to coords
            print(to_coords)
            if to_coords and remote_selected is not None:
                fr = remote_selected
                tr = to_coords

                if Player_number == 2:
                    # For player 2 the board indexing is flipped vertically in your code.
                    src_r, src_c = 7 - fr[0], fr[1]
                    dst_r, dst_c = 7 - to_coords[0], to_coords[1]
                else:
                    # Player 1 uses direct indexing
                    src_r, src_c = fr[0], fr[1]
                    dst_r, dst_c = to_coords[0], to_coords[1]

                # read destination piece BEFORE we overwrite it
                endPiece = board[dst_r][dst_c]

                # move piece
                piece = board[src_r][src_c]
                board[src_r][src_c] = " "
                board[dst_r][dst_c] = piece

                # If destination had a piece -> capture happened -> explode centered on that destination square
                if endPiece != " ":
                    board[dst_r][dst_c] = " "  # remove captured piece before explosion
                    Explotion((dst_r, dst_c), board)

                IsEnded = EndGame(board)
                if IsEnded != "":
                    game_over(screen, board, IsEnded)

                remote_selected = None
                Turn = not Turn
                print("Current Turn:", Turn)
                print("Partner moved to", tr)


        elif msg.startswith("Black wins!") or msg.startswith("White wins!"):
            GameOverOrReturn = game_over(screen, board, msg)
            if GameOverOrReturn == "exit":
                Run = False
            elif GameOverOrReturn == "matchmaking":
                # Reset game state for matchmaking
                matchmaking()

        elif msg.startswith("name:"):
            opponent_name = msg[5:]
    now = time.time()
    delta = now - last_tick

    if Turn:
        if my_color == "W":
            white_time -= delta
        else:
            black_time -= delta

    else:
        if my_color == "W":
            black_time -= delta
        else:
            white_time -= delta

    last_tick = now

    # clamp to 0
    white_time = max(0, white_time)
    black_time = max(0, black_time)

    # detect time over
    if white_time <= 0:
        game_over(screen, board, "Black wins (White timed out)")
    elif black_time <= 0:
        game_over(screen, board, "White wins (Black timed out)")
    
    Board(screen)
    draw_player_info(screen, my_name, opponent_name, white_time, black_time, my_color)
    resign_button.draw(screen)
    pygame.display.flip()
    clock.tick(60)


pygame.quit()