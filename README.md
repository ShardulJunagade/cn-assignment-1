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

To perform the traceroute analysis as documented in our report:

#### Windows (using Command Prompt or PowerShell):
```cmd
tracert www.google.com
```

#### macOS/Linux:
```bash
traceroute www.google.com
```

#### Packet Capture Commands:

For capturing traceroute traffic with Wireshark or tcpdump:

**Windows (tcpdump equivalent - requires Npcap):**
```cmd
# Start Wireshark GUI and filter: icmp
# Or use command line if available:
# tcpdump -i <interface> icmp
```

**macOS/Linux (tcpdump):**
```bash
sudo tcpdump -i en0 -w traceroute_capture.pcap &
traceroute www.google.com
```

## Outputs

### Task 1 Outputs

**Client Output:**
- `scapy_dns_report.csv` / `dpkt_dns_report.csv` with columns:
    - `Custom header value (HHMMSSID)`
    - `Domain name`
    - `Resolved IP address`

**Server Output:**
- Structured logging to console and log files
- Optional CSV logging with columns: `time,client_addr,header,domain,resolved_ip,time_slot`

**Sample CSV Output:**
```
Custom header value (HHMMSSID),Domain name,Resolved IP address
20464700,netflix.com,192.168.1.11
20464701,linkedin.com,192.168.1.12
20464702,example.com,192.168.1.13
```

### Task 2 Outputs

**Generated Analysis:**
- Terminal output screenshots from both Windows and macOS
- Wireshark packet captures showing protocol differences
- Comparative analysis of ICMP vs UDP traceroute behavior
- Documentation of missing hops and their causes

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
├── docs/                    # Documentation
│   ├── tasks.md            # Assignment requirements
│   └── dns_resolution_rules.md
├── latex/                   # LaTeX report source
│   └── main.tex            # Complete project report
└── logs/                    # Generated log files
```

## Dependencies

- Python 3.x
- scapy
- dpkt  
- tqdm (progress bars)
- Standard library: socket, csv, json, logging, datetime, argparse

## Notes

- The dpkt implementation is significantly faster than Scapy for processing large PCAP files
- Both implementations produce consistent results, demonstrating correctness
- All terminal outputs and execution logs are preserved in the `logs/` directory
- The complete analysis and findings are documented in the LaTeX report: `latex/main.tex`
- Wireshark captures and screenshots are referenced in the final report

## Repository

**GitHub**: [https://github.com/ShardulJunagade/cn-assignment-1](https://github.com/ShardulJunagade/cn-assignment-1)

All source code, documentation, and generated reports are available in the public repository.
