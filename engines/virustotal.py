# engines/virustotal.py
import aiohttp
import asyncio
import json
from utils.logging import setup_logger

logger = setup_logger()

class Engine:
    def __init__(self, domain, api_key=None):  # Add api_key as an optional argument
        self.domain = domain
        self.api_key = api_key  # Store the API key (if provided)
        self.base_url = f"https://www.virustotal.com/api/v3/domains/{domain}/subdomains"
        self.session = None

    async def fetch(self, url):
        headers = {"x-apikey": self.api_key} if self.api_key else {}
        async with self.session.get(url, headers=headers) as response:
            return await response.text()

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
        data = json.loads(response)
        for item in data.get("data", []):
            subdomain = item.get("id")
            if subdomain and subdomain.endswith(self.domain):
                subdomains.add(subdomain)
        return list(subdomains)