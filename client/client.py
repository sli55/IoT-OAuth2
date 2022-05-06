import socket
import json
import time
from message import Message
from addr_port import gateway_addr_port, client_addr_port, authserv_addr_port

class client():
    def __init__(self, name):
        self.name = name
        self.msg = str()

        # create socket
        try:
            self.sock_id = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            "socket creation failed: {}".format(socket.error)

        # assign ip address and port
        self.addr = client_addr_port[0]
        self.port = client_addr_port[1]
        
        # bind socket to ip address and port
        self.sock_id.bind((self.addr, self.port))

    # send message string
    def send_msg(self, msg, addr_port):
        self.sock_id.sendto(bytearray(msg, "utf-8"), addr_port)

    # receive message string
    def receive_msg(self, bytes):
        self.msg = self.sock_id.recvfrom(bytes)[0].decode()

if __name__ == "__main__":
    cli = client(name="client")

    #
    request = "test"
    print("1. Requesting {} service from gateway".format(request))
    request_message = Message(type="request", sender=(cli.addr, cli.port), recipient=gateway_addr_port, content=request)
    cli.msg = json.dumps(request_message.__dict__)
    print("   Waiting for authorization code from gateway")
    time.sleep(10)
    cli.send_msg(cli.msg, gateway_addr_port)

    #
    cli.receive_msg(1024)
    authcode_message = json.loads(cli.msg)

    #
    print("3. Fowarding authorization code to authorization server")
    authcode_message['sender'] = (cli.addr, cli.port)
    authcode_message['recipient'] =authserv_addr_port
    cli.msg = json.dumps(authcode_message)
    print("   Waiting for token from authorization server")
    time.sleep(10)
    cli.send_msg(cli.msg, authserv_addr_port)
    
    #
    cli.receive_msg(1024)
    token_message = json.loads(cli.msg)

    #
    print("5. Fowarding token to gateway")
    token_message['sender'] = (cli.addr, cli.port)
    token_message['recipient'] =authserv_addr_port
    cli.msg = json.dumps(token_message)
    time.sleep(10)
    cli.send_msg(cli.msg, gateway_addr_port)

    #
    print("   Waiting for result from gateway")
    time.sleep(10)
    cli.receive_msg(1024)
    print("   Result: {}".format(cli.msg))