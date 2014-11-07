import socket
import struct

HEADER_FORMAT = "!HHIIBBHHH"
HEADER_SIZE = 5


def get_checksum(data):
    i = len(data)

    # Handle the case where the length is odd
    if (i & 1):
        i -= 1
        sum = ord(data[i])
    else:
        sum = 0

    # Iterate through chars two by two and sum their byte values
    while i > 0:
        i -= 2
        sum += (ord(data[i + 1]) << 8) + ord(data[i])

    # Wrap overflow around
    sum = (sum >> 16) + (sum & 0xffff)

    result = (~ sum) & 0xffff  # One's complement
    result = result >> 8 | ((result & 0xff) << 8)  # Swap bytes
    return result


def make_packet(source_port, dest_port,
                seqnum, acknum, ack,
                final, window_size,
                contents):
    if final:
        flags = 1
    else:
        flags = 0

    if ack:
        flags += 16

    header = struct.pack(HEADER_FORMAT, source_port,
                         dest_port, seqnum, acknum,
                         HEADER_SIZE, flags,
                         window_size, 0, 0)

    check = get_checksum(header + contents)

    header = struct.pack(HEADER_FORMAT, source_port,
                         dest_port, seqnum, acknum,
                         HEADER_SIZE, flags,
                         window_size, check, 0)

    return header + contents


def unpack(segment):
    header = segment[:20]
    packet_source_port, packet_dest_port, packet_seqnum, \
    packet_acknum, packet_header_length, packet_flags, \
    packet_window_size, packet_checksum, \
    packet_urgent = struct.unpack(HEADER_FORMAT, header)

    packet_ack = (packet_flags >> 4) == 1
    packet_final = int(packet_flags % 2 == 1)
    packet_contents = segment[20:]

    return packet_source_port, packet_dest_port, \
           packet_seqnum, packet_acknum, packet_header_length, \
           packet_ack, packet_final, packet_window_size, \
           packet_contents


def timeout(signum, frame):
    raise socket.timeout