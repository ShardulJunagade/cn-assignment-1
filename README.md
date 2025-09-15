# cn-assignment-1

## Team Members
1. Shardul Junagade (23110297)
2. Rishabh Jogani (23110276)

PCAP file chosen: `3.pcap`

> (297 + 276) % 10 = 3



## Installation and Setup Instructions
1. Ensure Python 3.x is installed on your system.
2. Create a virtual environment:
    ```bash
    python -m venv .venv
    ```
3. Activate the virtual environment:
    - On Windows:
        ```bash
        .venv\Scripts\Activate.ps1
        ```
    - On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
4. Install required packages:
    ```bash
    pip install -r requirements.txt
    ```

## How to Run

1) Original Scapy-based implementation:

    - Start server:
        ```bash
        python server_scapy.py --host 0.0.0.0 --port 53535 --rules .\rules.json
        ```

    - Run client:
        ```bash
        python client_scapy.py --pcap .\3.pcap --server-ip 127.0.0.1 --server-port 53535 --out-csv scapy_dns_report.csv
        ```

2) dpkt-based implementation, which directly parses the PCAP and DNS:

    - Start server:
        ```bash
        python server_dpkt.py --host 0.0.0.0 --port 53535 --rules .\rules.json
        ```

    - Run client:
        ```bash
        python client_dpkt.py --pcap .\3.pcap --server-ip 127.0.0.1 --server-port 53535 --out-csv dpkt_dns_report.csv
        ```

## What the programs do

- Client parses the PCAP, filters UDP port 53 DNS query packets, prepends an 8-byte custom header `HHMMSSID`, and sends to the server over UDP.
- Server extracts `HHMMSSID`, parses hour and sequence ID, applies time-based routing rules to pick an IP from a fixed pool of 15 addresses, and returns a text response `header|domain|ip`.

## Outputs

- Client creates `client_report.csv` with columns:
    - `Custom header value (HHMMSSID)`
    - `Domain name`
    - `Resolved IP address`

- Server appends to `server_log.csv` with columns:
    - `time,client_addr,header,domain,resolved_ip,time_slot`

## Notes

- The time-based IP selection follows the given rules:
    - Morning (04:00–11:59): pool indices 0–4
    - Afternoon (12:00–19:59): pool indices 5–9
    - Night (20:00–03:59): pool indices 10–14
    - Offset = ID % 5, final index = pool_start + offset
- The Scapy version uses Scapy for parsing DNS. The alternative version uses `dpkt` for PCAP/DNS parsing.
