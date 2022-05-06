import socket
import json
from message import Message
import random
import jwt
import time
from addr_port import gateway_addr_port, client_addr_port

# decrypt signed messages with the other's public key
authserv_public_key = open('authserv.key.pub', 'r').read()

# sign messages with its own private key
gateway_private_key = open('gateway.key', 'r').read()

class gateway():
    def __init__(self, name):
        self.name = name
        self.msg = str()
        self.authcode = int()

        # create socket
        try:
            self.sock_id = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        except socket.error:
            "Socket creation failed: {}".format(socket.error)

        # assign ip address and port
        self.addr = gateway_addr_port[0]
        self.port = gateway_addr_port[1]

        # bind socket to ip address and port
        self.sock_id.bind((self.addr, self.port))

    # send message string
    def send_msg(self, msg, addr_port):
        self.sock_id.sendto(bytearray(msg, "utf-8"), addr_port)

    # receive message string
    def receive_msg(self, bytes):
        self.msg = self.sock_id.recvfrom(bytes)[0].decode()

    def generate_authcode(self):
        # get random auth code
        self.authcode = random.randint(0,99999)
        
        # genrate payload
        payload = {
            "sub": self.authcode,
        }

        # sign
        authcode = jwt.encode(
            payload=payload,
            key=gateway_private_key,
            algorithm='RS256'
        )

        return authcode

    def verify_token(self, token):
        # try to decode token
        try:
            verified_token = jwt.decode(
                jwt=token,
                key=authserv_public_key,
                algorithms=['RS256',]
            )
        
        # change resource value to indicate an invalid token
        except jwt.exceptions.ExpiredSignatureError:
            verified_token["sub"]["resource"] = "Token expired"
        except verified_token['sub']['authcode'] is not self.authcode:
            verified_token["sub"]["resource"] = "Authorization code does not match"

        return verified_token


if __name__ == "__main__":
    gate = gateway(name="gateway")

    #
    print("0. Waiting for request from client")
    gate.receive_msg(1024)
    request_message = json.loads(gate.msg)
    request = request_message['content']
    print("   Client is requesting {} service".format(request))

    #
    print("2. Generating authorization code and sending to client")
    authcode = gate.generate_authcode()
    auth_code_message = Message(type="authcode", sender=(gate.addr, gate.port), recipient=client_addr_port, content=authcode)
    gate.msg = json.dumps(auth_code_message.__dict__)
    print("   Waiting for encoded token forwarded by client from authorization server")
    time.sleep(10)
    gate.send_msg(gate.msg, auth_code_message.recipient)

    #
    gate.receive_msg(1024)
    token_message = json.loads(gate.msg)
    token = token_message['content']
    
    #
    print("6. Verifying encoded token and sending result back to client")
    decoded_token = gate.verify_token(token)
    gate.send_msg(decoded_token['sub']['resource'], client_addr_port)