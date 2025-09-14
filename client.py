import argparse, socket, time, csv, logging
from scapy.all import rdpcap, DNS, UDP, PcapReader
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    
def run_client(pcap_path, server_ip, server_port, out_csv):
    dns_pkts = []
    for pkt in PcapReader(pcap_path):
        if (pkt.haslayer(DNS) and pkt[DNS].qr == 0):
            qname = pkt[DNS].qd.qname.decode()
            if not qname.endswith(".local.") and not qname.startswith("_"):
                dns_pkts.append(pkt)

    logging.info(f"Found {len(dns_pkts)} DNS query packets in {pcap_path}")
    if not dns_pkts:
        logging.warning("No DNS query packets found. Exiting.")
        return
    
    # Use UDP to match the server's protocol (8-byte header + raw DNS packet)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(3.0)
    logging.info(f"Using UDP to communicate with server at {server_ip}:{server_port}")

    results_data = [] # (header, domain, ips)

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

        sock.sendto(payload, (server_ip, server_port))
        logging.info(f"Sent query txid={txid} header={header} domain={domain}")

        # Receive raw DNS response bytes
        try:
            resp_bytes, _ = sock.recvfrom(65535)
        except socket.timeout:
            logging.warning(f"Timeout waiting for response for domain {domain} (txid={txid})")
            continue

        # Parse DNS response and extract resolved IP
        try:
            dns_resp = DNS(resp_bytes)
            resolved_ip = None
            if dns_resp.an:
                # Collect chained answers
                answers = []
                ans = dns_resp.an
                while ans is not None:
                    answers.append(ans)
                    ans = ans.payload if hasattr(ans, 'payload') else None
                for rr in answers:
                    # type 1 == A record
                    if getattr(rr, 'type', None) == 1 and hasattr(rr, 'rdata'):
                        resolved_ip = rr.rdata
                        break
            if not resolved_ip:
                logging.warning(f"No A record found in response for domain {domain} (txid={txid})")
                continue

            results_data.append((header, domain, str(resolved_ip)))
            logging.info(f"Resolved {domain} -> {resolved_ip}")
        except Exception as e:
            logging.error(f"Failed to parse DNS response for {domain}: {e}")
    
    logging.info("All queries sent. Waiting for any remaining responses...")

    with open(out_csv, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Custom header value (HHMMSSID)', 'Domain name', 'Resolved IP address'])
        writer.writerows(results_data)
    logging.info(f"Results written to {out_csv}")

    sock.close()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client to send DNS queries from PCAP to custom DNS server")
    parser.add_argument('--pcap', default='./3.pcap', help='Path to input PCAP file with DNS queries')
    parser.add_argument('--server-ip', default='127.0.0.1', help='IP address of the DNS server to query')
    parser.add_argument('--server-port', type=int, default=53535, help='Port of the DNS server to query')
    parser.add_argument('--out-csv', default='dns_report.csv', help='Path to output CSV file for DNS responses')
    args = parser.parse_args()

    run_client(args.pcap, args.server_ip, args.server_port, args.out_csv)
