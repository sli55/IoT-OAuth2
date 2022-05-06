# CS45203 Computer Network Security
A simple demonstration of OAuth 2.0

## Requirements
`pip install -r requirements.txt`

## Instructions
- Clone to your VMs and use each of the three repositories to host on each VM
- Run `python3 gateway/gateway.py` and `python3 authserv/authserv.py` before running `python3 client/client.py`
- Run `python3 client/client.py` to check the message flow indicated by the number from 1 to 6

## Overview
        authserv            client              gateway
                                1 ----------------> request
                         authcode <---------------- 2
     authcode <---------------- 3
     verify authcode
            4 ----------------> token
                                5 ----------------> token
                                                    verify token
                           result <---------------- 6

## Future Work
- Enable multi threading to process multiple requests
- Set up databse to support multiple clients