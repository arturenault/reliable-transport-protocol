#!/usr/bin/env python
import signal
import socket
import struct
import sys

def make_packet(contents, final):
    header = bytearray(20)

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

    header[12] = 5 * 16  # header size is always 5 words in our case
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
        print ack

        acknum = 256 * 256 * 256 * ord(ack[8]) +\
                    256 * 256 * ord(ack[9]) +\
                    256 * ord(ack[10]) +\
                    ord(ack[11])

        if acknum == seqnum:

            text = send_file.read(556) # 576 - TCP header
            checksum = 0

            if text == "":
                last_packet = True


            seqnum += 1
            acknum += 1

            packet = make_packet(text, last_packet)

            send_sock.sendto(packet, (remote_ip, remote_port))

            if last_packet:
                break








