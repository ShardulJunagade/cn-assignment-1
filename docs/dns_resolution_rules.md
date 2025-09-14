# DNS Resolution Rules and Implementation Details

## Server Configuration:
The server maintains a pool of 15 IP addresses for load balancing:

**IP Pool:** [
"192.168.1.1", "192.168.1.2", "192.168.1.3", "192.168.1.4", "192.168.1.5",
"192.168.1.6", "192.168.1.7", "192.168.1.8", "192.168.1.9", "192.168.1.10",
"192.168.1.11", "192.168.1.12", "192.168.1.13", "192.168.1.14", "192.168.1.15"
]

## Rules JSON File Structure:
```json
{
  "timestamp_rules": {
    "time_based_routing": {
      "morning": {
        "time_range": "04:00-11:59",
        "hash_mod": 5,
        "ip_pool_start": 0,
        "description": "Morning traffic routed to first 5 IPs"
      },
      "afternoon": {
        "time_range": "12:00-19:59",
        "hash_mod": 5,
        "ip_pool_start": 5,
        "description": "Afternoon traffic routed to middle 5 IPs"
      },
      "night": {
        "time_range": "20:00-03:59",
        "hash_mod": 5,
        "ip_pool_start": 10,
        "description": "Night traffic routed to last 5 IPs"
      }
    }
  }
}
```

## IP selection Algorithm on server side:

1. Extract timestamp from custom header: "HHMMSSID"
2. Apply these rules to the extracted header:
    - Extract the hour from the timestamp to determine the time period.
    - Use the ID and apply modulo 5 to get a specific IP.

c. Select IP from appropriate pool segment

## Report Format Requirements:

**Students must submit a table with the following columns:**

| Custom header value (HHMMSSID) | Domain name | Resolved IP address |
|--------------------------------|-------------|-------------------|
| 12105500 | www.abc.com | 192.168.1.6 |
| 21055409 | www.google.com | 192.168.1.15 |

## Explanation:

The header

• **12105500** is parsed as hour = 12, which falls in the **afternoon (12:00–19:59)** slot with **ip_pool_start = 5**. The session ID is **00**, so **00 % 5 = 0**. Adding this to the pool start index gives **5 + 0 = 5**, which corresponds to the IP at index 5, i.e., **192.168.1.6**.

• **21055409** → hour 21 ⇒ **night (20:00–03:59)** with **ip_pool_start = 10**; ID **09** ⇒ **09 % 5 = 4**; final index **10 + 4 = 14** ⇒ IP **192.168.1.15**.