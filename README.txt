README
Programming Assignment 2
CSEE 4119 - Computer Networks
Artur Upton Renault
aur2103

This program implements a TCP-like transport layer protocol on top of the unreliable UDP protocol. It guarantees in-order, uncorrupted delivery of all packets irrespective of delays or losses, and does its job pretty well.

All messages are sent with a standard 20-byte TCP header, containing the following information

[Source port 	][Dest port		]
[		Sequence Number			]
[	Acknowledgement Number		]
[HL ][   ][Flags][Receive window]
[	Checksum	][	Urgent ptr	]

				Scale: [ 1 byte ]

This information is used to ensure reliable delivery.
The source port indicates the port the packet was sent from; dest the one it is being sent to. The sequence number identifies the packet, and the acknowledgement number contains the sequence number of the next acknowledgement the sender expects. HL contains the header length, which in our case is always 20. Flags contain additional options. I only implemented FIN (indicating this is the last packet) and ACK (indicating the packet identified by the ACK number is valid). The receive window indicates the number of packets the receiver is willing to accept at once (I only implemented 1). The checksum is used in checking for corruption, and the urgent pointer, in this implementation, was unused.

With a window size of 1, this essentially is a stop-and-wait protocol. The sender sends a packet, then waits for an ack confirming that packet. If he receives that ack, he sends the next packet. If he times out before receiving that packet, or receives a NAK, he resends the packet. The receiver waits for a connection; once he has received one, he makes a TCP connection to the sender for ACK transmission. If he receives a valid packet, he writes it to the file and waits for the next one. If he receives an invalid one, he sends a NAK. The process ends when the sender reaches EOF on his end and sends a FIN packet. When the receiver gets the FIN, he sends an ACK and shuts down. When the sender receives the final ACK, he shuts down too.

This system is able to recover from a lost packet through the timeout system. If the sender receives no response before his timeout period, he assumes the packet has been lost and resends it. The process repeats until he receives an ACK. This timeout period is adjusted based on a weighted average of the past estimated round trip times (measured, in this case, from the moment a packet is sent to the moment it is ACKed). The equations I used follow exactly those in the book.

The receiver is invoked, self-explanatorily, using
./receiver.py <filename> <listening_port> <sender_IP> <sender_port> <log_filename>

The sender is invoked with 
./sender.py <filename> <remote_IP> <remote_port> <ack_port_num> <log_filename>

If log_filename is stdout, it will log to stdout.

Both files log each packet it receives
<timestamp> <source_port> <destination_port> <seqnum> <acknum> <flags>

The sender additionally logs the estimated RTT in seconds every time it receives an ACK (which is when it calculates a new value). 

In my tests, the receiver has been able to rewrite the sent file (tested using cmp and diff) on his end perfectly. I tested with both scripts running on the same computer, and on different computers. I also tested using the provided proxy on various settings. The performance of the program in terms of speed and retransmission efficiency was not perfect due to the window size, but fairly good, diminishing over less reliable channels and larger file sizes, which is to be expected. 