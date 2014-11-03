#!/usr/bin/env python
import socket
import sys

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        listen_port = int(sys.argv[2])
        sender_ip = socket.gethostbyname(sys.argv[3])
        sender_port = int(sys.argv[4])
        log_filename = sys.argv[5]

    except IndexError, TypeError:
        exit("usage: ./sender.py <filename> <listening_port> <sender_IP> <sender_port> <log_filename>")



    