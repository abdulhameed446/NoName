import socket
from concurrent.futures import ThreadPoolExecutor
from utils.logging import setup_logger

logger = setup_logger()

class PortScanner:
    def __init__(self, subdomains, ports, verbose=False):
        """
        Initialize the PortScanner.
        
        :param subdomains: List of subdomains to scan.
        :param ports: List of ports to scan.
        :param verbose: If True, enable detailed logging. Default is False.
        """
        self.subdomains = subdomains
        self.ports = [int(port) for port in ports]  # Ensure ports are integers
        self.verbose = verbose  # Verbose flag

    def scan_port(self, host, port):
        """
        Scan a single port on a host.
        
        :param host: The host (subdomain) to scan.
        :param port: The port to scan.
        :return: The port if it is open, otherwise None.
        """
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((host, port))
            sock.close()
            return port if result == 0 else None
        except Exception as e:
            if self.verbose:  # Log errors only if verbose is enabled
                logger.error(f"Error scanning port {port} on {host}: {e}")
            return None

    def scan_subdomain(self, subdomain):
        """
        Scan all ports for a single subdomain.
        
        :param subdomain: The subdomain to scan.
        :return: A tuple of (subdomain, list of open ports).
        """
        open_ports = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.scan_port, subdomain, port) for port in self.ports]
            for future in futures:
                if future.result():
                    open_ports.append(future.result())
        if open_ports and self.verbose:  # Log open ports only if verbose is enabled
            logger.info(f"{subdomain} - Open ports: {', '.join(map(str, open_ports))}")
        return subdomain, open_ports

    def run(self):
        """
        Scan all subdomains and return a dictionary of results.
        
        :return: A dictionary where keys are subdomains and values are lists of open ports.
        """
        results = {}
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(self.scan_subdomain, subdomain) for subdomain in self.subdomains]
            for future in futures:
                subdomain, open_ports = future.result()
                if open_ports:  # Only include subdomains with open ports
                    results[subdomain] = open_ports
        return results