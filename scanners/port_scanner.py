# scanners/port_scanner.py
import socket
from concurrent.futures import ThreadPoolExecutor
from utils.logging import setup_logger

logger = setup_logger()

class PortScanner:
    def __init__(self, subdomains, ports):
        self.subdomains = subdomains
        self.ports = ports

    def scan_port(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return port if result == 0 else None
        except Exception:
            return None

    def scan_subdomain(self, subdomain):
        open_ports = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.scan_port, subdomain, port) for port in self.ports]
            for future in futures:
                if future.result():
                    open_ports.append(future.result())
        if open_ports:
            logger.info(f"{subdomain} - Open ports: {', '.join(map(str, open_ports))}")

    def run(self):
        with ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.scan_subdomain, self.subdomains)