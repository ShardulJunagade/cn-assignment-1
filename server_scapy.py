import argparse, socket, json, logging
from scapy.all import DNS

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

DEFAULT_IP_POOL = [
 "192.168.1.1","192.168.1.2","192.168.1.3","192.168.1.4","192.168.1.5",
 "192.168.1.6","192.168.1.7","192.168.1.8","192.168.1.9","192.168.1.10",
 "192.168.1.11","192.168.1.12","192.168.1.13","192.168.1.14","192.168.1.15"
]

def load_rules_from_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    data.setdefault("ip_pool", DEFAULT_IP_POOL)
    return data


def resolve_ip_address(rules, header):
    """Selects an IP address based on the custom header and rules."""
    try:
        hour = int(header[0:2])
        session_id = int(header[6:8])
        time_rules = rules.get("timestamp_rules", {}).get("time_based_routing", {})        
        if 4 <= hour <= 11:
            slot_cfg = time_rules.get("morning")
        elif 12 <= hour <= 19:
            slot_cfg = time_rules.get("afternoon")
        else: # Covers 20:00 to 03:59
            slot_cfg = time_rules.get("night")
        
        # Get the parameters from the selected rule
        hash_mod = int(slot_cfg.get("hash_mod", 5))
        ip_pool_start = int(slot_cfg.get("ip_pool_start", 0))
        ip_pool = rules.get("ip_pool", DEFAULT_IP_POOL)
        index = ip_pool_start + (session_id % hash_mod)
        
        # Make sure the calculated index is valid
        if not (0 <= index < len(ip_pool)):
            logging.warning(f"Calculated index {index} is out of bounds. Defaulting to index 0.")
            index = 0

        return ip_pool[index]

    except (ValueError, TypeError, KeyError) as e:
        logging.error(f"Error processing header '{header}': {e}. Defaulting to first IP.")
        return rules.get("ip_pool", DEFAULT_IP_POOL)[0]


def handle_packet(data, client_addr, sock, rules):
    """Parses a received packet and sends a DNS response."""
    header = data[:8].decode('ascii', errors='ignore')
    dns_bytes = data[8:]
    
    try:
        dns_query = DNS(dns_bytes)
        qname_bytes = dns_query.qd.qname if dns_query.qd else b""
        qname_str = qname_bytes.decode(errors='ignore')
        if qname_str.endswith(".local.") or qname_str.startswith("_"):
            logging.info(f"Ignoring non-standard DNS query for {qname_str} from {client_addr}")
            return

        resolved_ip = resolve_ip_address(rules, header)

        # Send a plain text response instead of a raw DNS packet: "header|domain|ip"
        response = f"{header}|{qname_str.rstrip('.')}|{resolved_ip}"
        sock.sendto(response.encode('utf-8'), client_addr)
        logging.info(f"Responded to {client_addr}: {response}")

    except Exception as e:
        logging.error(f"Failed to process packet from {client_addr}: {e}")


def run_server(host, port, rules_path):
    rules = load_rules_from_json(rules_path)
    logging.info(f"Loaded rules from {rules_path}")
    logging.info(f"Rules: {rules}")
    logging.info(f"IP Pool Length: {len(rules.get('ip_pool', DEFAULT_IP_POOL))}")
    logging.info(f"IP Pool: {rules.get('ip_pool', DEFAULT_IP_POOL)}")

    # Create a UDP socket.
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server.bind((host, port))
    logging.info(f"DNS server listening on {host}:{port}")

    while True:
        data, addr = server.recvfrom(65535)
        handle_packet(data, addr, server, rules)

    # server.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Custom DNS Server with Time-Based IP Resolution")
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind the DNS server (default: 0.0.0.0)')
    parser.add_argument('--port', type=int, default=53535, help='UDP Port to bind the DNS server (default: 53535)')
    parser.add_argument('--rules', type=str, default='./rules.json', help='Path to rules JSON file (default: ./rules.json)')
    args = parser.parse_args()


    run_server(args.host, args.port, args.rules)
