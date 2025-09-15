import socket
import json
from datetime import datetime
import os

# IP Pool
IP_POOL = [
    "192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5",
    "192.168.1.6", "192.168.1.7", "192.168.1.8", "192.168.1.9", "192.168.1.10",
    "192.168.1.11", "192.168.1.12", "192.168.1.13", "192.168.1.14", "192.168.1.15"
]

RULES = {
    "morning": {"start": 4, "end": 11, "pool_start": 0},   # 04:00–11:59
    "afternoon": {"start": 12, "end": 19, "pool_start": 5}, # 12:00–19:59
    "night": {"start": 20, "end": 3, "pool_start": 10}     # 20:00–03:59
}

def select_ip(header):
    hour = int(header[:2])
    query_id = int(header[-2:])  # last 2 chars = ID

    # Find time period
    if 4 <= hour <= 11:
        rule = RULES["morning"]
    elif 12 <= hour <= 19:
        rule = RULES["afternoon"]
    else:
        rule = RULES["night"]

    base = rule["pool_start"]
    ip_index = base + (query_id % 5)
    return IP_POOL[ip_index]

def start_server(host="127.0.0.1", port=9999):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((host, port))
    print(f"Server running on {host}:{port}")

    while True:
        data, addr = s.recvfrom(4096)
        header = data[:8].decode()
        dns_query = data[8:].decode(errors="ignore")  # Simplified
        ip = select_ip(header)

        print(f"Received: Header={header}, Query={dns_query}, Resolved={ip}")
        response = f"{header}|{dns_query}|{ip}"
        s.sendto(response.encode(), addr)

start_server()
