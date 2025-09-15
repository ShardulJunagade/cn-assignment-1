import argparse, csv, logging, socket
from datetime import datetime
import dpkt
from tqdm import tqdm

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")


def iter_dns_queries(pcap_path):
    """Yield (raw_dns_bytes, domain) for DNS queries to UDP port 53."""
    with open(pcap_path, "rb") as f:
        pcap = dpkt.pcap.Reader(f)
        for ts, buf in tqdm(pcap, desc="Processing packets"):
            try:
                eth = dpkt.ethernet.Ethernet(buf)
                ip = eth.data
                udp = ip.data
                if not isinstance(udp, dpkt.udp.UDP) or udp.dport != 53:  # must be DNS query going *to* port 53
                    continue
                dns = dpkt.dns.DNS(udp.data)
                domain = dns.qd[0].name.decode() if isinstance(dns.qd[0].name, bytes) else dns.qd[0].name
                domain = domain.rstrip('.')
                # if domain.endswith(".local") or domain.startswith("_"):
                #     continue  # skip mDNS / service discovery
                yield udp.data, domain
            except Exception:
                logging.warning("Failed to parse a packet, skipping.")
                continue


def run_client(pcap_path, server_ip, server_port, out_csv):
    queries = list(iter_dns_queries(pcap_path))
    logging.info(f"Found {len(queries)} DNS query packets in {pcap_path}")
    if not queries:
        return

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    results = []

    for i, (dns_bytes, domain) in enumerate(queries):
        header = datetime.now().strftime("%H%M%S") + f"{i % 100:02d}"
        payload = header.encode("ascii") + dns_bytes
        sock.sendto(payload, (server_ip, server_port))
        logging.info(f"Sent query #{i} header={header} domain={domain}")
        resp, _ = sock.recvfrom(65535)
        r_header, r_domain, r_ip = resp.decode().strip().split("|")
        results.append((r_header, r_domain, r_ip))
        logging.info(f"Resolved {r_domain} -> {r_ip}")

    with open(out_csv, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Custom header value (HHMMSSID)", "Domain name", "Resolved IP address"])
        writer.writerows(results)

    logging.info(f"Results written to {out_csv}")
    sock.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Client (dpkt) to send DNS queries from PCAP to custom server")
    parser.add_argument("--pcap", default="./3.pcap", help="Path to input PCAP file")
    parser.add_argument("--server-ip", default="127.0.0.1", help="IP address of the DNS server")
    parser.add_argument("--server-port", type=int, default=53535, help="Port of the DNS server")
    parser.add_argument("--out-csv", default="dpkt_dns_report.csv", help="Path to output CSV file")
    args = parser.parse_args()

    run_client(args.pcap, args.server_ip, args.server_port, args.out_csv)
