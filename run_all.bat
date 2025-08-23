@echo off
start "Server" cmd /k "python server/server.py"
start "Client1" cmd /k "python client1/client.py"
start "Client2" cmd /k "python client2/client.py"

