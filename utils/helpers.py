# utils/helpers.py
def clean_subdomains(subdomains):
    """
    Clean and filter subdomains.
    - Remove HTML-like tags (e.g., <BR>).
    - Filter out invalid entries (e.g., email addresses).
    """
    cleaned = set()
    for subdomain in subdomains:
        # Remove <BR> tags and split into individual subdomains
        for part in subdomain.split("<BR>"):
            part = part.strip()
            # Filter out invalid entries
            if "." in part and "@" not in part:
                cleaned.add(part)
    return cleaned