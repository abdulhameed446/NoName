# engines/netcraft.py
import aiohttp
import asyncio
import re
from urllib.parse import urlparse
from utils.logging import setup_logger

logger = setup_logger()

class Engine:
    def __init__(self, domain, api_key=None):
        self.domain = domain
        self.api_key = api_key  # Not used for Netcraft
        self.base_url = "https://searchdns.netcraft.com/?restriction=site+ends+with&host={domain}"
        self.session = None

    async def fetch(self, url):
        async with self.session.get(url) as response:
            # Handle encoding properly
            content = await response.read()
            return content.decode('utf-8', errors='ignore')  # Ignore invalid UTF-8 characters

    async def enumerate(self):
        self.session = aiohttp.ClientSession()
        url = self.base_url.format(domain=self.domain)
        try:
            response = await self.fetch(url)
            subdomains = self.extract_domains(response)
            return subdomains
        finally:
            await self.session.close()

    def extract_domains(self, response):
        subdomains = set()
        link_regx = re.compile(r'<a class="results-table__host" href="(.*?)"')
        links = link_regx.findall(response)
        for link in links:
            subdomain = urlparse(link).netloc
            if subdomain and subdomain.endswith(self.domain):
                subdomains.add(subdomain)
        return list(subdomains)