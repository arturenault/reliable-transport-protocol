#!/usr/bin/env python
import socket
import sys

if __name__ == '__main__':
    try:
        filename = sys.argv[1]
        remote_ip = socket.gethostbyname(sys.argv[2])
        remote_port = int(sys.argv[3])
        ack_port = int(sys.argv[4])
        log_filename = sys.argv[5]
        window_size = int(sys.argv[6])

    except IndexError, TypeError:
        exit("usage: ./sender.py <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size>")









