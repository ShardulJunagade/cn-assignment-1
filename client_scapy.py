import argparse, socket, time, csv, logging
from scapy.all import DNS, PcapReader
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def run_client(pcap_path, server_ip, server_port, out_csv):
    dns_pkts = []
    counter=0
    for pkt in PcapReader(pcap_path):
        if (pkt.haslayer(DNS) and pkt[DNS].qr == 0):
            qname = pkt[DNS].qd.qname.decode()
            if not qname.endswith(".local.") and not qname.startswith("_"):
                dns_pkts.append(pkt)
        counter += 1
        if counter % 20000 == 0:
            logging.info(f"Processed {counter} packets, found {len(dns_pkts)} DNS queries so far...")

    logging.info(f"Found {len(dns_pkts)} DNS query packets in {pcap_path}")
    if not dns_pkts:
        logging.warning("No DNS query packets found. Exiting.")
        return
    
    # Use UDP to match the server's protocol (8-byte header + raw DNS packet)
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    logging.info(f"Using UDP to communicate with server at {server_ip}:{server_port}")

    results_data = [] # (header, domain, ip)

    for i, pkt in enumerate(dns_pkts):
        dns_bytes = bytes(pkt[DNS])
        txid = pkt[DNS].id
        domain = pkt[DNS].qd.qname.decode().rstrip('.')

        # custom header HHMMSS + 2-digit sequence id
        hhmmss = datetime.now().strftime("%H%M%S")
        sid = f"{i:02d}"
        header = hhmmss + sid
        header_bytes = header.encode('ascii')
        payload = header_bytes + dns_bytes

        client.sendto(payload, (server_ip, server_port))
        logging.info(f"Sent query txid={txid} header={header} domain={domain}")

        # Receive plain text response bytes
        resp_bytes, _ = client.recvfrom(65535)
        resp_text = resp_bytes.decode('utf-8', errors='ignore').strip()
        parts = resp_text.split('|')
        if len(parts) != 3:
            logging.warning(f"Unexpected response format for domain {domain}: {resp_text}")
            continue
        r_header, r_domain, r_ip = parts
        results_data.append((r_header, r_domain, r_ip))
        logging.info(f"Resolved {r_domain} -> {r_ip}")
    
    logging.info("All queries sent. Waiting for any remaining responses...")

    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Custom header value (HHMMSSID)', 'Domain name', 'Resolved IP address'])
        writer.writerows(results_data)
    logging.info(f"Results written to {out_csv}")

    client.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client to send DNS queries from PCAP to custom DNS server")
    parser.add_argument('--pcap', default='./3.pcap', help='Path to input PCAP file with DNS queries')
    parser.add_argument('--server-ip', default='127.0.0.1', help='IP address of the DNS server to query')
    parser.add_argument('--server-port', type=int, default=53535, help='Port of the DNS server to query')
    parser.add_argument('--out-csv', default='scapy_dns_report.csv', help='Path to output CSV file for DNS responses')
    args = parser.parse_args()

    run_client(args.pcap, args.server_ip, args.server_port, args.out_csv)
