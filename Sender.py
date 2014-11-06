#!/usr/bin/env python
import datetime
import signal
import socket
import struct
import sys
HEADER_SIZE = 20


def unpack_ack(segment):
    header = bytearray(segment[:20])
    packet_source_port = int(header[0]) * 256 + int(header[1])
    packet_dest_port = int(header[2]) * 256 + int(header[3])
    packet_seqnum = 256 * 256 * 256 * int(header[4]) +\
                    256 * 256 * int(header[5]) +\
                    256 * int(header[6]) +\
                    int(header[7])
    packet_acknum = 256 * 256 * 256 * int(header[8]) +\
                    256 * 256 * int(header[9]) +\
                    256 * int(header[10]) +\
                    int(header[11])
    packet_final = int(header[13]) - 16
    packet_window_size = 256 * int(header[14]) + int(header[15])
    packet_checksum = 256 * int(header[16]) + int(header[17])
    return packet_source_port, packet_dest_port,\
           packet_seqnum, packet_acknum, packet_final,\
           packet_window_size, packet_checksum


def make_packet(contents, final):
    header = bytearray(HEADER_SIZE)

    header[0] = ack_port / 256 # first two bytes are source port
    header[1] = ack_port % 256

    header[2] = remote_port / 256 # second two bytes are destination port
    header[3] = remote_port % 256

    header[4] = seqnum / 256 / 256 / 256 # next four bytes are sequence number
    header[5] = seqnum / 256 / 256
    header[6] = seqnum / 256
    header[7] = seqnum % 256

    header[8] = acknum / 256 / 256 / 256 # next four bytes are ack number
    header[9] = acknum / 256 / 256
    header[10] = acknum / 256
    header[11] = acknum % 256

    header[12] = HEADER_SIZE/4 * 16  # header size is always 5 words in our case
                                    # multiply by 16 to leave unused bytes blank

    # header[13] is 2 empty bits + the flag field
    # In the sender, it only depends on FIN because the others aren't
    # implemented and it never sends ACKs
    if final:
        header[13] = 1
    else:
        header[13] = 0

    header[14] = window_size / 256
    header[15] = window_size % 256

    header[16] = checksum / 256
    header[17] = checksum % 256

    header[18] = 0
    header[19] = 0

    return header + contents


def shutdown(signum, frame):
    send_sock.close()
    ack_sock.close()
    exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, shutdown)

    try:
        filename = sys.argv[1]
        remote_ip = socket.gethostbyname(sys.argv[2])
        remote_port = int(sys.argv[3])
        ack_port = int(sys.argv[4])
        log_filename = sys.argv[5]
        try:
            window_size = int(sys.argv[6])
        except IndexError:
            window_size = 1
    except IndexError, TypeError:
        exit('usage: ./sender.py <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename> <window_size>')

    try:
        send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        send_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        send_sock.bind(("", ack_port))

        ack_sock = socket.socket()
        ack_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ack_sock.bind(("", ack_port))
        ack_sock.listen(1)
    except socket.error:
        exit('Error creating socket.')

    seqnum = 0
    acknum = 0
    last_packet = False

    send_file = open(filename)
    if log_filename == "stdout":
        log_file = sys.stdout
    else:
        log_file = open(log_filename, 'w')

    text = send_file.read(556) # 576 - TCP header
    checksum = 0
    if text == "":
        last_packet = True
    packet = make_packet(text, last_packet)
    send_sock.sendto(packet, (remote_ip, remote_port))

    recv_sock, addr = ack_sock.accept()

    while True:
        ack = recv_sock.recv(20)
        source_port, dest_port, ack_seqnum, ack_acknum, final,\
            window_size, checksum = unpack_ack(ack)

        log = str(datetime.datetime.now()) + " " + str(source_port) + " " + str(dest_port) + " " + str(ack_seqnum) + " " + str(ack_acknum) + " " + "ACK"

        if final == 1:
            log_file.write(log + " FIN\n")
            break

        log_file.write(log + "\n")

        if ack_acknum == seqnum:

            text = send_file.read(556) # 576 - TCP header
            checksum = 0

            if text == "":
                last_packet = True

            seqnum += 1
            acknum += 1

            packet = make_packet(text, last_packet)

            send_sock.sendto(packet, (remote_ip, remote_port))










