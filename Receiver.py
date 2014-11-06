#!/usr/bin/env python
import datetime
import signal
import socket
import sys


def unpack_packet(segment):
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
    packet_final = int(header[13])
    packet_window_size = 256 * int(header[14]) + int(header[15])
    packet_checksum = 256 * int(header[16]) + int(header[17])
    packet_contents = str(segment[20:])
    return packet_source_port, packet_dest_port,\
           packet_seqnum, packet_acknum, packet_final,\
           packet_window_size, packet_checksum, packet_contents


def make_ack(num):
    header = bytearray(20)

    header[0] = out_port / 256 # first two bytes are source port
    header[1] = out_port % 256

    header[2] = sender_port / 256 # second two bytes are destination port
    header[3] = sender_port % 256

    header[4] = num / 256 / 256 / 256 # next four bytes are sequence number
    header[5] = num / 256 / 256
    header[6] = num / 256
    header[7] = num % 256

    header[8] = num / 256 / 256 / 256 # next four bytes are ack number
    header[9] = num / 256 / 256
    header[10] = num / 256
    header[11] = num % 256

    header[12] = 5 * 16  # header size is always 5 words in our case
                         # multiply by 16 to leave unused bytes blank

    # header[13] is 2 empty bits + the flag field
    # In the receiver, it is always 16 because the ACK bit is the only
    # activated one.
    if final:
        header[13] = 17
    else:
        header[13] = 16

    header[14] = window_size / 256
    header[15] = window_size % 256

    header[16] = checksum / 256
    header[17] = checksum % 256

    header[18] = 0
    header[19] = 0

    return header


def shutdown(signum, frame):
    sock.close()
    ack_sock.close()
    exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, shutdown)

    try:
        filename = sys.argv[1]
        listen_port = int(sys.argv[2])
        sender_ip = socket.gethostbyname(sys.argv[3])
        sender_port = int(sys.argv[4])
        log_filename = sys.argv[5]

    except IndexError, TypeError:
        exit("usage: ./receiver.py <filename> <listening_port> <sender_IP> <sender_port> <log_filename>")

    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("", listen_port))

        ack_sock = socket.socket()
        ack_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error:
        exit("Error creating socket.")

    recv_file = open(filename, 'w')
    if log_filename == "stdout":
        log_file = sys.stdout
    else:
        log_file = open(log_filename , 'w')

    packet, addr = sock.recvfrom(576)
    source_port, dest_port, seqnum, acknum,\
        final, window_size, checksum, contents = unpack_packet(packet)

    recv_file.write(contents)
    log = str(datetime.datetime.now()) + " " + str(source_port) + " " + str(dest_port) + " " + str(seqnum) + " " + str(acknum)
    log_file.write(log + "\n")

    ack_sock.connect((sender_ip, sender_port))
    out_port = ack_sock.getsockname()[1]
    ack_segment = make_ack(seqnum)
    ack_sock.send(ack_segment)
    while True:
        packet, addr = sock.recvfrom(576)
        source_port, dest_port, seqnum, acknum,\
        final, window_size, checksum, contents = unpack_packet(packet)

        recv_file.write(contents)

        log = str(datetime.datetime.now()) + " " + str(source_port) + " " + str(dest_port) + " " + str(seqnum) + " " + str(acknum)
        if final:
            log += " FIN"
        log_file.write(log + "\n")

        ack_segment = make_ack(seqnum)
        ack_sock.send(ack_segment)
        if final == 1:
            break