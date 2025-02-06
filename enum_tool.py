import os
import subprocess
import sys

def install_dependencies():
    dependencies = ["subfinder", "amass", "gobuster", "jq", "anew"]
    for dep in dependencies:
        if subprocess.run(["which", dep], capture_output=True).returncode != 0:
            print(f"[+] Installing {dep}...")
            subprocess.run(["sudo", "apt", "install", "-y", dep])
    
    # Check if ShodanX is installed
    if subprocess.run(["which", "shodanx"], capture_output=True).returncode != 0:
        print("[+] Installing ShodanX in a virtual environment...")
        os.makedirs(".venv", exist_ok=True)
        subprocess.run(["python3", "-m", "venv", ".venv"], shell=True)
        subprocess.run([".venv/bin/python", "-m", "pip", "install", "--upgrade", "pip"], shell=True)
        subprocess.run(["git", "clone", "https://github.com/RevoltSecurities/ShodanX.git"], shell=True)
        os.chdir("ShodanX")
        subprocess.run([".venv/bin/python", "-m", "pip", "install", "-r", "requirements.txt"], shell=True)
        subprocess.run([".venv/bin/python", "setup.py", "install"], shell=True)
        os.chdir("..")

def enumerate_subdomains(domain):
    # Create a directory with the domain name
    os.makedirs(domain, exist_ok=True)
    os.chdir(domain)

    print(f"[+] Enumerating subdomains for {domain}...")

    commands = [
        f"subfinder -d {domain} -o subfinder.txt",
        f".venv/bin/shodanx subdomain -d {domain} -ra -o shodanx.txt",
        f"amass enum -active -norecursive -d {domain} -o amass.txt",
        f"gobuster dns -d {domain} -w /usr/share/wordlists/amass/subdomains-top1mil-110000.txt -o gobuster.txt",
        f"curl -s https://crt.sh/?q=%.{domain}&output=json | jq -r '.[].name_value' | sort -u | tee crtsh.txt",
        f"curl -s \"https://otx.alienvault.com/api/v1/indicators/hostname/{domain}/passive_dns\" | jq -r '.passive_dns[]?.hostname' | grep -E '^[a-zA-Z0-9.-]+\\.{domain}$' | sort -u | tee alienvault_subs.txt",
        f"curl -s \"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=10000\" | jq -r '.results[].page.domain' | grep -E '^[a-zA-Z0-9.-]+\\.{domain}$' | sort -u | tee urlscan.txt",
        f"curl -s \"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&collapse=urlkey\" | jq -r '.[1:][] | .[2]' | grep -Eo '([a-zA-Z0-9-]+\\.)*{domain}' | sort -u | tee webarchive_subs.txt"
    ]

    for cmd in commands:
        print(f"[+] Running: {cmd}")
        subprocess.run(cmd, shell=True)

    # Combine all results into a unique final file
    print("[+] Generating final unique subdomains file...")
    subprocess.run("cat *.txt | anew mixed_final.txt", shell=True)

    print("[+] Enumeration complete. Results saved in mixed_final.txt")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 enum_tool.py <domain>")
        sys.exit(1)
    
    domain = sys.argv[1]
    install_dependencies()
    enumerate_subdomains(domain)
