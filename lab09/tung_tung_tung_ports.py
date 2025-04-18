import socket
import argparse


def is_port_open(ip, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        result = s.connect_ex((ip, port))
        return result != 0


def find_free_ports(ip, start_port, end_port):
    free_ports = []
    print(f"Scanning ports {start_port}-{end_port} on {ip}...")
    for port in range(start_port, end_port + 1):
        if is_port_open(ip, port):
            free_ports.append(port)
    return free_ports


def main():
    parser = argparse.ArgumentParser(description="Tung Tung Tung free ports for a given IP in a port range.")
    parser.add_argument("ip", type=str, help="Target IP address")
    parser.add_argument("start_port", type=int, help="Start of the port range")
    parser.add_argument("end_port", type=int, help="End of the port range")
    args = parser.parse_args()

    if args.start_port < 1 or args.end_port > 65535 or args.start_port > args.end_port:
        print("Invalid port range. Valid ports are from 1 to 65535.")
        return

    free_ports = find_free_ports(args.ip, args.start_port, args.end_port)
    if free_ports:
        print("Free ports:")
        for port in free_ports:
            print(port)
    else:
        print("No free ports found in the specified range.")


if __name__ == "__main__":
    main()
