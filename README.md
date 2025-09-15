# cn-assignment-1

## Team Members
1. Shardul Junagade (23110297)
2. Rishabh Jogani (23110276)

PCAP file chosen: `3.pcap`

> (297 + 276) % 10 = 3

## Overview

This repository contains the implementation of two computer networking tasks:
- **Task 1 (80 marks)**: Custom DNS Resolver with time-based IP selection
- **Task 2 (20 marks)**: Traceroute Protocol Behavior Analysis

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

### Task 1: DNS Resolver

We implemented two versions of the DNS resolver: Scapy-based and dpkt-based. The dpkt version is significantly faster for large PCAP files.

#### 1) Scapy-based implementation:

- Start server:
    ```bash
    python server_scapy.py
    ```

- Run client:
    ```bash
    python client_scapy.py
    ```

#### 2) dpkt-based implementation (Recommended for large files):

- Start server:
    ```bash
    python server_dpkt.py --host 0.0.0.0 --port 53535 --rules ./rules.json
    ```

- Run client:
    ```bash
    python client_dpkt.py --pcap ./3.pcap --server-ip 127.0.0.1 --server-port 53535 --out-csv dpkt_dns_report.csv
    ```

### Task 2: Traceroute Analysis


```cmd
tracert www.google.com    # Windows

traceroute www.google.com   # macOS/Linux
```

#### Steps to run packet capture

1. **macOS (using tcpdump):**
    ```bash
    # Start packet capture in background
    sudo tcpdump -i en0 host www.google.com -w TracerouteMac.pcap &

    # Run traceroute in another terminal
    traceroute www.google.com

    # Stop capture (Ctrl+C the tcpdump process)
    ```

2. **Windows (using tshark):**
    ```bash
    # Start packet capture (replace "5" with your network interface number)
    tshark -i 5 -f "host www.google.com" -w TracertWin.pcap

    # In another terminal/command prompt, run:
    tracert www.google.com

    # Stop tshark capture with Ctrl+C
    ```


Open the generated `.pcap` files (`TracerouteMac.pcap` and `TracertWin.pcap`) in Wireshark to analyze:
- Protocol differences (ICMP vs UDP)
- TTL progression
- Response patterns
- Missing hops analysis

## Outputs

### Task 1 Outputs

**Client Output:**
- `scapy_dns_report.csv` / `dpkt_dns_report.csv` with columns:
    - `Custom header value (HHMMSSID)`
    - `Domain name`
    - `Resolved IP address`

- All terminal outputs and execution logs are preserved in the `logs/` directory


**Sample CSV Output:**
```
Custom header value (HHMMSSID),Domain name,Resolved IP address
20464700,netflix.com,192.168.1.11
20464701,linkedin.com,192.168.1.12
20464702,example.com,192.168.1.13
```


## Project Structure

```
├── client_scapy.py          # Scapy-based DNS client
├── server_scapy.py          # Scapy-based DNS server  
├── client_dpkt.py           # dpkt-based DNS client (faster)
├── server_dpkt.py           # dpkt-based DNS server (faster)
├── logger.py                # Shared logging configuration
├── rules.json               # Time-based routing rules
├── requirements.txt         # Python dependencies
├── 3.pcap                   # Input PCAP file
├── latex/                   # LaTeX report source
│   └── main.tex             # Complete project report
└── logs/                    # Generated log files
```
