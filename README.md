# cn-assignment-1

## Team Members
1. Shardul Junagade (23110297)
2. Rishabh Jogani (23110276)

PCAP file chosen: 3.pcap

> (297 + 276) % 10 = 3



## Installation and Setup Instructions
1. Ensure Python 3.x is installed on your system.
2. Create a virtual environment:
    ```powershell
    py -3 -m venv .venv
    ```
3. Activate the virtual environment:
    - On Windows:
    ```powershell
    .venv\Scripts\Activate.ps1
    ```
    - On macOS/Linux:
        ```bash
        source .venv/bin/activate
        ```
4. Install required packages:
        ```powershell
        pip install -r requirements.txt
        ```

## How to Run

1. Start the server (listens on TCP, default 9999). The server loads time-based routing rules from a JSON matching `docs/dns_resolution_rules.md`. If `--rules` is not provided, it defaults to `./docs/rules.json`:
    ```powershell
    # use the default rules file path
    python server.py --host 0.0.0.0 --port 9999

    # OR explicitly specify a JSON rules file path
    python server.py --host 0.0.0.0 --port 9999 --rules .\docs\rules.json
    ```

2. In a new terminal, run the client with your selected PCAP (e.g., `3.pcap`) and server address:
    ```powershell
    python client.py --pcap 3.pcap --server 127.0.0.1 --port 9999
    ```

## What the programs do

- Client parses the PCAP, filters DNS query packets, prepends an 8-byte custom header `HHMMSSID`, frames the payload (length + message), and sends to the server.
- Server extracts `HHMMSSID`, parses hour and sequence ID, applies time-based routing rules to pick an IP from a fixed pool of 15 addresses, and returns a JSON response with the resolved IP.

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
- The domain from the DNS question is parsed using `dnslib` on the server side.
