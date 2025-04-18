import socket
import os
import platform

def get_ip_and_netmask():
    hostname = socket.gethostname()
    
    ip_address = socket.gethostbyname(hostname)
    print(f"IP address: {ip_address}")

    system = platform.system()
    if system == "Windows":
        output = os.popen("ipconfig").read()
        for line in output.splitlines():
            if "IPv4" in line and ip_address in line:
                print(line.strip())
            if "Subnet Mask" in line:
                print(f"{line.strip()}")
                break
    elif system in ("Linux", "Darwin"):  # Darwin = macOS
        output = os.popen("ifconfig" if system == "Darwin" else "ip addr").read()
        lines = output.splitlines()
        for i, line in enumerate(lines):
            if ip_address in line:
                if system == "Darwin":
                    for l in lines[i:i+5]:
                        if "netmask" in l:
                            print(l.strip())
                            break
                else:
                    for l in lines[i:i+5]:
                        if "inet" in l and "/" in l:
                            print(l.strip())
                            break
                break
    else:
        print("Unsupported OS for netmask retrieval.")

if __name__ == "__main__":
    get_ip_and_netmask()
