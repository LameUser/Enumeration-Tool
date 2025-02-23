import os
import subprocess
import sys
import platform

def install_dependencies():
    dependencies = ["subfinder", "amass", "gobuster", "jq"]
    for dep in dependencies:
        if subprocess.run(["which", dep], capture_output=True).returncode != 0:
            print(f"[+] Installing {dep}...")
            if platform.system() == "Linux":
                subprocess.run(["sudo", "apt", "install", "-y", dep], check=True)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["brew", "install", dep], check=True)
            else:
                print(f"[-] Unsupported OS for automatic installation of {dep}")
                sys.exit(1)

    # Install anew manually (requires Go)
    if subprocess.run(["which", "anew"], capture_output=True).returncode != 0:
        print("[+] Installing anew...")
        subprocess.run(["go", "install", "github.com/tomnomnom/anew@latest"], check=True)
        # Add Go binary directory to PATH
        go_path = subprocess.run(["go", "env", "GOPATH"], capture_output=True, text=True).stdout.strip()
        os.environ["PATH"] += f":{go_path}/bin"

def enumerate_subdomains(domain):
    # Create a directory with the domain name
    os.makedirs(domain, exist_ok=True)
    os.chdir(domain)

    print(f"[+] Enumerating subdomains for {domain}...")

    # Define commands and their corresponding output files
    commands = [
        (["subfinder", "-d", domain, "-o", "subfinder.txt"], None),
        (["amass", "enum", "-active", "-norecursive", "-d", domain, "-o", "amass.txt"], None),
        (["gobuster", "dns", "-d", domain, "-w", "/usr/share/wordlists/amass/subdomains-top1mil-110000.txt", "-o", "gobuster.txt"], None),
        (["curl", "-s", f"https://crt.sh/?q=%.{domain}&output=json"], "crtsh.txt"),
        (["curl", "-s", f"https://otx.alienvault.com/api/v1/indicators/hostname/{domain}/passive_dns"], "alienvault_subs.txt"),
        (["curl", "-s", f"https://urlscan.io/api/v1/search/?q=domain:{domain}&size=10000"], "urlscan.txt"),
        (["curl", "-s", f"http://web.archive.org/cdx/search/cdx?url=*.{domain}/*&output=json&collapse=urlkey"], "webarchive_subs.txt")
    ]

    for cmd, output_file in commands:
        print(f"[+] Running: {' '.join(cmd)}")
        try:
            # Add a timeout of 10 minutes (600 seconds)
            result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=600)
            if output_file:
                with open(output_file, "w") as f:
                    f.write(result.stdout)
        except subprocess.TimeoutExpired:
            print(f"[-] Command timed out: {' '.join(cmd)}")
        except subprocess.CalledProcessError as e:
            print(f"[-] Error running command: {' '.join(cmd)}")
            print(e.stderr)
            continue

    # Combine all results into a unique final file
    print("[+] Generating final unique subdomains file...")
    subprocess.run("cat *.txt | anew mixed_final.txt", shell=True, check=True)

    print("[+] Enumeration complete. Results saved in mixed_final.txt")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 enum_tool.py <domain>")
        sys.exit(1)
    
    domain = sys.argv[1]
    install_dependencies()
    enumerate_subdomains(domain)
