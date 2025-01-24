# output/file_writer.py
from utils.helpers import clean_subdomains

def write_to_file(filename, subdomains):
    """
    Write subdomains to a file in a clean and readable format.
    """
    # Clean and sort subdomains
    cleaned_subdomains = clean_subdomains(subdomains)
    sorted_subdomains = sorted(cleaned_subdomains)

    # Write to file
    with open(filename, "w") as f:
        f.write(f"# Subdomains for {sorted_subdomains[0].split('.')[-2]}.com\n\n")
        for subdomain in sorted_subdomains:
            f.write(subdomain + "\n")

    print(f"[+] Results saved to {filename}")