import socket
from scapy.all import rdpcap, DNS, DNSQR
from datetime import datetime
import csv
import os

def build_header(seq_id):
    now = datetime.now()
    return f"{now.strftime('%H%M%S')}{seq_id:02d}"

def run_client(pcap_file, server_host="127.0.0.1", server_port=9999, report_file="dns_report.csv"):
    print("READING FILE")
    packets = rdpcap(pcap_file)
    print('Connecting Socket')
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    seq_id = 0
    report = []
    counter = 0
    for pkt in packets:
        if pkt.haslayer(DNS) and pkt.getlayer(DNS).qr == 0:  # DNS Query only
            query_name = pkt[DNSQR].qname.decode()
            if query_name.endswith(".local.") or query_name.startswith("_"): # skip mDNS discovery queries
                continue
            header = build_header(seq_id)
            message = header.encode() + query_name.encode()
            s.sendto(message, (server_host, server_port))

            data, _ = s.recvfrom(4096)
            header_val, domain, resolved_ip = data.decode().split("|")
            report.append([header_val, domain, resolved_ip])
            seq_id += 1
        counter += 1
        if counter % 50000 == 0:
            print(f"Processed {counter} packets...")

    # Print report to console
    print("\nFinal Report:")
    print("CustomHeader\tDomain\tResolvedIP")
    for row in report:
        print("\t".join(row))

    # Save report to CSV
    with open(report_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["CustomHeader", "Domain", "ResolvedIP"])
        writer.writerows(report)

    print(f"\nReport saved to {report_file}")

base_dir = os.path.dirname(os.path.abspath(__file__))
pcap_path = os.path.join(base_dir, "3.pcap")

run_client(pcap_path) 