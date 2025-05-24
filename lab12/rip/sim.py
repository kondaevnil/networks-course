import json
import argparse

class Router:
    def __init__(self, ip):
        self.ip = ip
        self.neighbors = []
        self.routing_table = {ip: (ip, 0)}

    def update_table(self, from_router, from_table):
        updated = False
        for dest, (next_hop, metric) in from_table.items():
            if dest == self.ip:
                continue
            new_metric = metric + 1
            if dest not in self.routing_table or new_metric < self.routing_table[dest][1]:
                self.routing_table[dest] = (from_router.ip, new_metric)
                updated = True
        return updated

    def send_update(self):
        for neighbor in self.neighbors:
            neighbor.update_table(self, self.routing_table)


def load_network_from_file(filename):
    with open(filename) as f:
        data = json.load(f)
    routers = {entry["ip"]: Router(entry["ip"]) for entry in data["routers"]}
    for entry in data["routers"]:
        routers[entry["ip"]].neighbors = [routers[n_ip] for n_ip in entry["neighbors"]]
    return list(routers.values())


def simulate_rip(routers, max_rounds=10):
    for round in range(max_rounds):
        changes = False
        for router in routers:
            router.send_update()
        for router in routers:
            updated = any(router.update_table(n, n.routing_table) for n in router.neighbors)
            changes = changes or updated
        if not changes:
            break


def print_routing_tables(routers):
    for router in routers:
        print(f"\nFinal state of router {router.ip} table:")
        print(f"{'Source IP':<16} {'Destination IP':<18} {'Next Hop':<16} {'Metric'}")
        for dest, (next_hop, metric) in router.routing_table.items():
            print(f"{router.ip:<16} {dest:<18} {next_hop:<16} {metric}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Simulate RIP routing protocol.")
    parser.add_argument("filename", help="JSON file containing the network configuration")
    args = parser.parse_args()

    routers = load_network_from_file(args.filename)
    simulate_rip(routers)
    print_routing_tables(routers)
