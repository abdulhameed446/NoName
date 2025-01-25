from utils.helpers import clean_subdomains
import dns.resolver

def is_wildcard(subdomain):
    """
    Check if a subdomain is a wildcard (starts with "*.").
    """
    return subdomain.startswith("*.")

def is_valid_subdomain(subdomain):
    """
    Check if a subdomain resolves to an IP address.
    Skip wildcard subdomains.
    """
    if is_wildcard(subdomain):
        return False  # Skip wildcard subdomains
    try:
        dns.resolver.resolve(subdomain, 'A')  # Resolve to IPv4 address
        return True
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN, dns.resolver.Timeout, dns.resolver.NoNameservers):
        return False

def write_to_console(subdomains, colorize=True, ports=None, port_results=None, verbose=False):
    """
    Write subdomains to the console in a clean and readable format.
    Categorize subdomains into valid (with open ports), invalid, and wildcard groups.
    """
    # Clean and ensure subdomains are unique
    cleaned_subdomains = clean_subdomains(subdomains)
    unique_subdomains = set(cleaned_subdomains)  # Ensure uniqueness

    # Sort the subdomains alphabetically
    sorted_subdomains = sorted(unique_subdomains)

    # Separate subdomains into valid, invalid, and wildcard groups
    valid_subdomains = []
    invalid_subdomains = []
    wildcard_subdomains = []

    for subdomain in sorted_subdomains:
        if is_wildcard(subdomain):
            wildcard_subdomains.append(subdomain)
        elif is_valid_subdomain(subdomain):
            valid_subdomains.append(subdomain)
        else:
            invalid_subdomains.append(subdomain)

    # Print summary
    print(f"\n[+] Found {len(sorted_subdomains)} unique subdomains:\n")

    # Print valid subdomains with open ports
    print(f"[+] Valid Subdomains ({len(valid_subdomains)}):")
    for subdomain in valid_subdomains:
        if port_results and subdomain in port_results:
            open_ports = port_results[subdomain]
            print(f"{subdomain} (Open Ports: {', '.join(map(str, open_ports))})")
        else:
            print(subdomain)

    # Print invalid subdomains
    print(f"\n[+] Invalid Subdomains ({len(invalid_subdomains)}):")
    for subdomain in invalid_subdomains:
        print(subdomain)

    # Print wildcard subdomains
    print(f"\n[+] Wildcard Subdomains ({len(wildcard_subdomains)}):")
    for subdomain in wildcard_subdomains:
        print(subdomain)