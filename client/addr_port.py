import socket
hostname = socket.gethostname()
addr = socket.gethostbyname(hostname)

gateway_addr_port = (addr, 1001)
client_addr_port = (addr, 1002)
authserv_addr_port = (addr, 1003)