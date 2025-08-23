import socket
import pygame
import sys

HOST = '127.0.0.1'
PORT = 65432

pygame.init()
screen = pygame.display.set_mode((400, 300))
pygame.display.set_caption('Explosive Chess Client 2')
font = pygame.font.SysFont(None, 36)

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.sendall(b'Hello from Client 2!')
    data = s.recv(1024)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    screen.fill((30, 30, 30))
    text = font.render(f'Received: {data.decode()}', True, (200, 200, 200))
    screen.blit(text, (20, 130))
    pygame.display.flip()

pygame.quit()
sys.exit()
