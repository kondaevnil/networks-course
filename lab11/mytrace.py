import socket
import struct
import time
import select
import sys


ICMP_ECHO_REQUEST = 8
ICMP_ECHO_REPLY = 0
ICMP_TIME_EXCEEDED = 11
DEFAULT_TIMEOUT = 3
TRIES_PER_HOP = 3
MAX_HOPS = 30


def checksum(source_string):
    total = 0
    count_to = (len(source_string) // 2) * 2
    for count in range(0, count_to, 2):
        val = source_string[count + 1] * 256 + source_string[count]
        total += val
        total = total & 0xffffffff

    if count_to < len(source_string):
        total += source_string[-1]
        total = total & 0xffffffff

    total = (total >> 16) + (total & 0xffff)
    total += (total >> 16)
    answer = ~total
    answer = answer & 0xffff
    return answer >> 8 | (answer << 8 & 0xff00)


def build_packet(identifier, sequence):
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, 0, identifier, sequence)
    payload = struct.pack("d", time.time())
    chksum = checksum(header + payload)
    header = struct.pack("bbHHh", ICMP_ECHO_REQUEST, 0, socket.htons(chksum), identifier, sequence)
    return header + payload


def traceroute(dest_name, max_hops=MAX_HOPS, tries=TRIES_PER_HOP):
    try:
        dest_addr = socket.gethostbyname(dest_name)
    except socket.gaierror:
        print(f"Cannot resolve host: {dest_name}")
        return

    print(f"Trace route to {dest_name} [{dest_addr}]:")

    for ttl in range(1, max_hops + 1):
        print(f"{ttl:2} ", end='')
        for try_count in range(tries):
            with socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as recv_socket, \
                 socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_ICMP) as send_socket:

                send_socket.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
                recv_socket.settimeout(DEFAULT_TIMEOUT)
                recv_socket.bind(("", 0))

                identifier = int((id(0) * time.time()) % 65535)
                sequence = ttl * tries + try_count
                packet = build_packet(identifier, sequence)

                send_time = time.time()
                send_socket.sendto(packet, (dest_addr, 0))

                try:
                    ready = select.select([recv_socket], [], [], DEFAULT_TIMEOUT)
                    if ready[0] == []:
                        print(" * ", end='')
                        continue

                    recv_packet, addr = recv_socket.recvfrom(512)
                    rtt = (time.time() - send_time) * 1000

                    icmp_header = recv_packet[20:28]
                    type, code, _, _, _ = struct.unpack("bbHHh", icmp_header)

                    curr_addr = addr[0]
                    try:
                        curr_name = socket.gethostbyaddr(curr_addr)[0]
                    except socket.herror:
                        curr_name = curr_addr

                    print(f"{rtt:.1f} ms", end=' ')
                    if type == ICMP_ECHO_REPLY:
                        print(f"\nTrace route completed. Reached {addr[0]}")
                        return
                except socket.timeout:
                    print(" * ", end='')
                    continue
        print(f"{curr_name} ({curr_addr}) ", end='')
        print()

    print("Maximum number of hops reached.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: sudo python3 mytrace.py <hostname>")
    else:
        traceroute(sys.argv[1])
