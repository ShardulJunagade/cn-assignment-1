import argparse
import json
import logging
import socket
import os

import dpkt
from logger import setup_logging


setup_logging("server_dpkt")

DEFAULT_IP_POOL = [
    "192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5",
    "192.168.1.6", "192.168.1.7", "192.168.1.8", "192.168.1.9", "192.168.1.10",
    "192.168.1.11", "192.168.1.12", "192.168.1.13", "192.168.1.14", "192.168.1.15"
]


def load_rules_from_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data.setdefault("ip_pool", DEFAULT_IP_POOL)
    return data


def resolve_ip_address(rules, header: str) -> str:
    try:
        hour = int(header[0:2])
        session_id = int(header[6:8])
        time_rules = rules.get("timestamp_rules", {}).get("time_based_routing", {})
        if 4 <= hour <= 11:
            slot_cfg = time_rules.get("morning", {})
        elif 12 <= hour <= 19:
            slot_cfg = time_rules.get("afternoon", {})
        else:
            slot_cfg = time_rules.get("night", {})

        hash_mod = int(slot_cfg.get("hash_mod", 5))
        ip_pool_start = int(slot_cfg.get("ip_pool_start", 0))
        ip_pool = rules.get("ip_pool", DEFAULT_IP_POOL)
        index = ip_pool_start + (session_id % hash_mod)
        if not (0 <= index < len(ip_pool)):
            logging.warning(f"Calculated index {index} is out of bounds. Defaulting to index 0.")
            index = 0
        return ip_pool[index]
    except Exception as e:
        logging.error(f"Error processing header '{header}': {e}. Defaulting to first IP.")
        return rules.get("ip_pool", DEFAULT_IP_POOL)[0]


def handle_packet(data: bytes, client_addr, sock: socket.socket, rules):
    header = data[:8].decode('ascii', errors='ignore')
    dns_bytes = data[8:]
    dns = dpkt.dns.DNS(dns_bytes)
    domain = dns.qd[0].name.decode() if isinstance(dns.qd[0].name, bytes) else dns.qd[0].name
    domain = domain.rstrip('.')
    resolved_ip = resolve_ip_address(rules, header)
    response = f"{header}|{domain}|{resolved_ip}"
    sock.sendto(response.encode('utf-8'), client_addr)
    logging.info(f"Responded to {client_addr}: {response}")


def run_server(host: str, port: int, rules_path: str):
    rules = load_rules_from_json(rules_path)
    logging.info(f"Loaded rules from {rules_path}")
    logging.info(f"IP Pool Length: {len(rules.get('ip_pool', DEFAULT_IP_POOL))}")

    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))
    logging.info(f"DNS server (dpkt) listening on {host}:{port}")

    while True:
        data, addr = server.recvfrom(65535)
        handle_packet(data, addr, server, rules)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom DNS Server (dpkt) with Time-Based IP Resolution")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the DNS server (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=53535, help='UDP Port to bind the DNS server (default: 53535)')
    parser.add_argument('--rules', type=str, default='./rules.json', help='Path to rules JSON file (default: ./rules.json)')
    args = parser.parse_args()

    run_server(args.host, args.port, args.rules)
