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

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", listen_port))
    except socket.error:
        exit("Error creating socket.")

    print("Listening at " + socket.gethostbyname(socket.gethostname()) + ":" + str(listen_port))

    while True:
        text, addr = sock.recvfrom(1024)
        print(text)