#!/usr/bin/env python
import datetime
import signal
import socket
import sys
import util

WINDOW_SIZE = 1

if __name__ == '__main__':
    signal.signal(signal.SIGINT, util.shutdown)

    # Process command line args
    try:
        filename = sys.argv[1]
        remote_ip = socket.gethostbyname(sys.argv[2])
        remote_port = int(sys.argv[3])
        ack_port = int(sys.argv[4])
        log_filename = sys.argv[5]

    except IndexError, TypeError:
        exit('usage: ./sender.py <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename>')

    # Create sockets
    try:
        # UDP socket for packets
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        send_sock.bind(("", ack_port))

        # TCP socket for acks
        ack_sock = socket.socket()
        ack_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ack_sock.bind(("", ack_port))
        ack_sock.listen(1)
    except socket.error:
        exit('Error creating socket.')

    # Initialize acknum and seqnum to 0
    seqnum = 0
    acknum = 0
    final = False # Boolean indicating that this is the last packet

    # Open files to reading and writing
    send_file = open(filename)
    if log_filename == "stdout":
        log_file = sys.stdout
    else:
        log_file = open(log_filename, 'w')

    tcp_established = False
    text = send_file.read(556)  # 576 - TCP header

    while(not tcp_established):
        try:
            packet = util.make_packet(ack_port, remote_port, seqnum, acknum, False, False, WINDOW_SIZE, text)
            send_sock.sendto(packet, (remote_ip, remote_port))

            signal.signal(signal.SIGALRM, util.timeout)
            signal.alarm(1)

            recv_sock, addr = ack_sock.accept()
            tcp_established = True
            recv_sock.settimeout(1)
        except socket.timeout:
            continue

    while True:
        try:
            ack = recv_sock.recv(20)
            ack_source_port, ack_dest_port, ack_seqnum, ack_acknum, ack_header_length, \
                ack_valid, ack_final, ack_window_size, ack_contents = util.unpack(ack)

            log = str(datetime.datetime.now()) + " " + \
                  str(ack_source_port) + " " + \
                  str(ack_dest_port) + " " + \
                  str(ack_seqnum) + " " + \
                  str(ack_acknum)

            if ack_valid:
                log = log + " ACK"
            if ack_final:
                log_file.write(log + " FIN\n")
                break

            log_file.write(log + "\n")

            if ack_acknum == acknum and ack_valid:

                text = send_file.read(556)  # 576 - TCP header

                if text == "":
                    final = True

                seqnum += 1
                acknum += 1

                packet = util.make_packet(ack_port, remote_port,
                                          seqnum, acknum, False,
                                          final, WINDOW_SIZE,
                                          text)

                send_sock.sendto(packet, (remote_ip, remote_port))

            else:
                raise socket.timeout

        except socket.timeout:
            packet = util.make_packet(ack_port, remote_port,
                                      seqnum, acknum, False,
                                      final, WINDOW_SIZE,
                                      text)

            send_sock.sendto(packet, (remote_ip, remote_port))










