#!/usr/bin/env python
import signal
import socket
import sys


def shutdown(signum, frame):
    sock.close()
    exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, shutdown)

    try:
        filename = sys.argv[1]
        remote_ip = socket.gethostbyname(sys.argv[2])
        remote_port = int(sys.argv[3])
        ack_port = int(sys.argv[4])
        log_filename = sys.argv[5]
        window_size = int(sys.argv[6])

    except IndexError, TypeError:
        exit("usage: ./sender.py <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size>")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error:
        exit("Error creating socket.")

    fp = open(filename)
    while True:
        text = fp.read(1024)
        if text == "":
            break

        sock.sendto(text, (remote_ip, remote_port))








