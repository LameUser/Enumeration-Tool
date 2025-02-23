import os
import subprocess
import sys
import platform

def install_dependencies():
    dependencies = ["subfinder", "amass", "gobuster", "jq", "anew"]
    for dep in dependencies:
        if subprocess.run(["which", dep], capture_output=True).returncode != 0:
            print(f"[+] Installing {dep}...")
            if platform.system() == "Linux":
                subprocess.run(["sudo", "apt", "install", "-y", dep])
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["brew", "install", dep])
            else:
                print(f"[-] Unsupported OS for automatic installation of {dep}")
                sys.exit(1)
    
    # Check if ShodanX is installed
    if subprocess.run(["which", "shodanx"], capture_output=True).returncode != 0:
        print("[+] Installing ShodanX in a virtual environment...")
        os.makedirs(".venv", exist_ok=True)
        subprocess.run(["python3", "-m", "venv", ".venv"])
        subprocess.run([".venv/bin/python", "-m", "pip", "install", "--upgrade", "pip"])
        subprocess.run(["git", "clone", "https://github.com/RevoltSecurities/ShodanX.git"])
        os.chdir("ShodanX")
        subprocess.run([".venv/bin/python", "-m", "pip", "install", "-r", "requirements.txt"])
        subprocess.run([".venv/bin/python", "setup.py", "install"])
        os.chdir("..")

def enumerate_subdomains(domain):
    # Create a directory with the domain name
    os.makedirs(domain, exist_ok=True)
    os.chdir(domain)

    print(f"[+] Enumerating subdomains for {domain}...")

    commands = [
        ["subfinder", "-d", domain, "-o", "subfinder.txt"],
        [".venv/bin/shodanx", "subdomain", "-d", domain, "-ra", "-o", "shodanx.txt"],
        ["amass", "enum", "-active", "-norecursive", "-d", domain, "-o", "amass.txt"],
        ["gobuster", "dns", "-d", domain, "-w", "/usr/share/wordlists/amass/subdomains-top1mil-110000.txt", "-o", "gobuster.txt"],
        ["curl", "-s", f"https://crt.sh/?q=%.{domain}&output=json"],
        ["curl", "-s", f"https://otx.alienvault.com/api/v1/indicators/hostname/{domain}/passive_dns"],
        ["curl", "-s", f"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=10000"],
        ["curl", "-s", f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&collapse=urlkey"]
    ]

    for cmd in commands:
        print(f"[+] Running: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"[-] Error running command: {' '.join(cmd)}")
            print(result.stderr)
            continue

        if cmd[0] == "curl":
            output_file = f"{cmd[4].split('=')[1].split('&')[0]}.txt"
            with open(output_file, "w") as f:
                f.write(result.stdout)

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
