import socket
import threading
import requests
from queue import Queue
from colorama import Fore, Style, init

init(autoreset=True)

# ---------------- CONFIG ----------------
MAX_PORT = 65535
THREADS = 200
TIMEOUT = 0.5

# ---------------- FRONT END ----------------
print(Fore.CYAN + Style.BRIGHT + """
====================================================
        ADVANCED VULNERABILITY SCANNER
        Full Port Scan | Python | CLI Tool
====================================================
""")

target = input(Fore.YELLOW + "Enter Target IP / Domain: ").strip()
print(Fore.WHITE + Style.BRIGHT + f"\nTarget Selected ➜ {target}\n")

# ---------------- UI HELPERS ----------------
def section(title):
    print(Fore.MAGENTA + Style.BRIGHT + f"\n[ {title} ]")

def status(tag, msg, color):
    print(color + f"[{tag:<8}] " + Style.RESET_ALL + msg)

# ---------------- PORT SCANNING ----------------
section("FULL PORT SCANNING (1–65535)")
queue = Queue()
open_ports = []
lock = threading.Lock()

def scan_port(port):
    s = socket.socket()
    s.settimeout(TIMEOUT)
    try:
        s.connect((target, port))
        with lock:
            open_ports.append(port)
            status("OPEN", f"Port {port}", Fore.LIGHTGREEN_EX)
    except:
        pass
    finally:
        s.close()

def worker():
    while not queue.empty():
        port = queue.get()
        scan_port(port)
        queue.task_done()

for port in range(1, MAX_PORT + 1):
    queue.put(port)

threads = []
for _ in range(THREADS):
    t = threading.Thread(target=worker, daemon=True)
    t.start()
    threads.append(t)

queue.join()

# ---------------- SCAN SUMMARY ----------------
section("SCAN SUMMARY")
status("INFO", f"Total Open Ports Found: {len(open_ports)}", Fore.CYAN)

if open_ports:
    status("INFO", f"Open Ports List: {sorted(open_ports)}", Fore.WHITE)
else:
    status("SAFE", "No open ports detected", Fore.GREEN)

# ---------------- BASIC RISK ANALYSIS ----------------
section("BASIC RISK ANALYSIS")

common_risks = {
    21: "FTP – plaintext credentials",
    22: "SSH – check weak passwords",
    23: "Telnet – insecure service",
    80: "HTTP – missing security headers",
    445: "SMB – EternalBlue risk",
    3306: "MySQL – DB exposure",
    3389: "RDP – brute-force target"
}

risk_found = False
for port in open_ports:
    if port in common_risks:
        status("WARNING", f"Port {port}: {common_risks[port]}", Fore.RED)
        risk_found = True

if not risk_found:
    status("OK", "No common risky services detected", Fore.GREEN)

# ---------------- HTTP HEADERS ----------------
if 80 in open_ports:
    section("HTTP SECURITY HEADERS")
    try:
        r = requests.get(f"http://{target}", timeout=3)
        headers = r.headers
        checks = [
            "Content-Security-Policy",
            "X-Frame-Options",
            "X-XSS-Protection",
            "Strict-Transport-Security"
        ]
        for h in checks:
            if h in headers:
                status("OK", f"{h} present", Fore.LIGHTCYAN_EX)
            else:
                status("MISSING", f"{h} not set", Fore.YELLOW)
    except:
        status("ERROR", "HTTP service not reachable", Fore.RED)

# ---------------- FOOTER ----------------
print(Fore.CYAN + Style.BRIGHT + "\n====================================================")
print(Fore.LIGHTMAGENTA_EX + Style.BRIGHT + " Follow On Instagram:- codewithiitian")
print(Fore.CYAN + Style.BRIGHT + "====================================================")
