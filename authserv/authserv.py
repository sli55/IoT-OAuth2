import socket
from message import Message
import json
import jwt
import time
from addr_port import client_addr_port, authserv_addr_port

# decrypt signed messages with the other's public key
gateway_public_key = open('gateway.key.pub', 'r').read()

# sign messages with the other's public key
authserv_private_key = open('authserv.key', 'r').read()

# token is avaliable for 10 mins
token_life_time = 600

class authorization_server():
    def __init__(self, name):
        self.name = name
        self.msg = str()

        # create socket
        try:
            self.sock_id = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            "socket creation failed: {}".format(socket.error)

        # assign ip address and port
        self.addr = authserv_addr_port[0]
        self.port = authserv_addr_port[1]

        # bind socket to ip address and port
        self.sock_id.bind((self.addr, self.port))

    # send message string
    def send_msg(self, msg, addr_port):
        self.sock_id.sendto(bytearray(msg, "utf-8"), addr_port)

    # receive message string
    def receive_msg(self, bytes):
        self.msg = self.sock_id.recvfrom(bytes)[0].decode()

    # generate encoded token
    def generate_token(self, authcode):
        # genrate payload
        payload = {
            "sub": {
                "authcode": authcode,
                "resource": "test resource" # resource can be an url link for unique password authentication or other types of data like data from a database
            },
            "exp": time.time() + token_life_time
        }

        # sign
        token = jwt.encode(
            payload=payload,
            key=authserv_private_key,
            algorithm='RS256'
        )

        return token

    def verify_authcode(self, authcode):
        verified_authcode = jwt.decode(
            jwt=authcode,
            key=gateway_public_key,
            algorithms=['RS256',]
        )

        return verified_authcode

if __name__ == "__main__":
    authserv = authorization_server("authserv")

    #
    print("0. Waiting for incoming authorization code from client")
    authserv.receive_msg(1024)
    authcode_message = json.loads(authserv.msg)
    authcode = authcode_message['content']

    #
    print("   Verifying authorization code")
    verified_authcode = authserv.verify_authcode(authcode)

    #
    print("4. Generating token and sending to client")
    token = authserv.generate_token(verified_authcode)
    
    token_message = Message(type="token", sender=(authserv.addr, authserv.port), recipient=client_addr_port, content=token)
    authserv.msg = json.dumps(token_message.__dict__)
    time.sleep(10)
    authserv.send_msg(authserv.msg, client_addr_port)