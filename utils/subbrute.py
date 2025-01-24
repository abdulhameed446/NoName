# utils/subbrute.py
import dns.resolver
from concurrent.futures import ThreadPoolExecutor
from utils.logging import setup_logger

logger = setup_logger()

class SubBrute:
    def __init__(self, domain, wordlist, resolvers, threads=30):
        self.domain = domain
        self.wordlist = wordlist
        self.resolvers = resolvers
        self.threads = threads

    def resolve_subdomain(self, subdomain):
        try:
            resolver = dns.resolver.Resolver()
            resolver.nameservers = self.resolvers
            answers = resolver.resolve(subdomain, 'A')
            return subdomain if answers else None
        except Exception:
            return None

    def enumerate(self):
        subdomains = set()
        with open(self.wordlist, 'r') as f:
            words = f.read().splitlines()

        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = [executor.submit(self.resolve_subdomain, f"{word}.{self.domain}") for word in words]
            for future in futures:
                result = future.result()
                if result:
                    subdomains.add(result)
                    logger.info(f"Found subdomain: {result}")
        return list(subdomains)