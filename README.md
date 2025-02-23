# Advanced Subdomain Enumeration Tool

## Overview

This is an **advanced subdomain enumeration tool** that leverages multiple open-source intelligence (OSINT) tools and APIs to gather subdomain information for a given target domain. The tool automates the installation of dependencies and utilizes various enumeration methods to provide comprehensive results.

## Features

- **Automated Dependency Installation**: Ensures that all required tools are installed before execution.
- **Multiple Enumeration Techniques**:
  - `subfinder` – Passive subdomain discovery
  - `amass` – Active enumeration and OSINT data collection
  - `gobuster` – DNS bruteforcing
  - `crt.sh` – Extracting subdomains from Certificate Transparency logs
  - `AlienVault OTX` – Gathering subdomains from AlienVault's passive DNS database
  - `urlscan.io` – Extracting subdomains from web scans
  - `Wayback Machine` – Fetching archived subdomains
- **Result Aggregation**: Merges and filters unique subdomains into a final output file.

## Installation

Before running the tool, ensure that your system has **Python 3** installed.


## How It Works

1. **Dependency Installation**  
   - Checks if the required tools (`subfinder`, `amass`, `gobuster`, `jq`, `anew`) are installed.  
   - Installs missing dependencies using `apt`.   

2. **Subdomain Enumeration**  
   - Runs various OSINT-based enumeration tools.  
   - Stores individual results in separate files.  
   - Aggregates and deduplicates all subdomains into `mixed_final.txt`.  

## Dependencies

The following tools are required and automatically installed:

- [Subfinder](https://github.com/projectdiscovery/subfinder)
- [Amass](https://github.com/owasp-amass/amass)
- [Gobuster](https://github.com/OJ/gobuster)
- [jq](https://stedolan.github.io/jq/)
- [Anew](https://github.com/tomnomnom/anew)

### Clone the Repository

`git clone https://github.com/yourusername/enum-tool.git && cd enum-tool`

### Command example

`python3 enum_tool.py <domain>`


## Output

All discovered subdomains are stored in the respective tool output files, and the final merged and deduplicated results are saved in:

`<mixed_final.txt>`

## Example output

```
[+] Enumerating subdomains for example.com...
[+] Running: subfinder -d example.com -o subfinder.txt
[+] Running: amass enum -active -norecursive -d example.com -o amass.txt
[+] Running: gobuster dns -d example.com -w /usr/share/wordlists/amass/subdomains-top1mil-110000.txt -o gobuster.txt
[+] Running: curl -s https://crt.sh/?q=%.example.com&output=json | jq -r '.[].name_value' | sort -u | tee crtsh.txt
...
[+] Generating final unique subdomains file...
[+] Enumeration complete. Results saved in mixed_final.txt
```
