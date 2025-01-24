# engines/dnsdumpster.py
import aiohttp
import asyncio
import re
from urllib.parse import urlparse
from utils.logging import setup_logger

logger = setup_logger()

class Engine:
    def __init__(self, domain, api_key=None):
        self.domain = domain
        self.api_key = api_key  # Not used for DNSDumpster
        self.base_url = "https://dnsdumpster.com/"
        self.session = None

    async def fetch(self, url):
        async with self.session.get(url) as response:
            # Handle encoding properly
            content = await response.read()
            return content.decode('utf-8', errors='ignore')  # Ignore invalid UTF-8 characters

    async def enumerate(self):
        self.session = aiohttp.ClientSession()
        try:
            response = await self.fetch(self.base_url)
            subdomains = self.extract_domains(response)
            return subdomains
        finally:
            await self.session.close()

    def extract_domains(self, response):
        subdomains = set()
        link_regx = re.compile(r'<td class="col-md-4">(.*?)<br>')
        links = link_regx.findall(response)
        for link in links:
            subdomain = link.strip()
            if subdomain and subdomain.endswith(self.domain):
                subdomains.add(subdomain)
        return list(subdomains)