import asyncio
import argparse
import pyfiglet  # For creating ASCII banners
from termcolor import colored  # For adding color to the banner
from utils.config import load_config
from utils.logging import setup_logger
from plugins.plugin_loader import load_plugins
from output.file_writer import write_to_file
from output.console_writer import write_to_console
from scanners.port_scanner import PortScanner

# Banner display function with color and size adjustments
def display_banner():
    """
    Display a colorful ASCII banner with the tool name and developer information.
    """
    # Create a larger banner
    banner = pyfiglet.figlet_format("NoName", font="slant", width=100)  # Adjusted width for better readability
    colored_banner = colored(banner, "cyan")  # Set the banner color to cyan

    # Display the colored banner
    print(colored_banner)
    
    # Additional details like your name in a different color
    print(colored("Developed by Abdulhameed", "green"))

# Setup logger
logger = setup_logger()

def parse_args():
    """
    Parse command-line arguments.
    """
    parser = argparse.ArgumentParser(description="Subdomain Enumeration Tool")
    parser.add_argument(
        "-d", "--domain", required=True, help="Domain to enumerate subdomains for."
    )
    parser.add_argument(
        "-e", "--engines",
        default="google,bing,virustotal,yahoo,ask,baidu,netcraft,dnsdumpster,threatcrowd,crtsearch,passivedns",
        help="Comma-separated list of search engines to use (e.g., google,bing,virustotal). Default: all engines."
    )
    parser.add_argument(
        "-o", "--output", help="Output file to save results."
    )
    parser.add_argument(
        "-p", "--ports", help="Comma-separated list of ports to scan (e.g., 80,443)."
    )
    parser.add_argument(
        "-b", "--bruteforce", action="store_true", help="Enable subdomain brute-forcing."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable verbose output."
    )
    parser.add_argument(
        "-n", "--no-color", action="store_true", help="Disable colorized output."
    )
    return parser.parse_args()

async def main():
    """
    Main function to orchestrate subdomain enumeration and scanning.
    """
    # Display the banner when the script starts
    display_banner()

    # Parse command-line arguments
    args = parse_args()

    # Load configuration
    try:
        config = load_config("config.yaml")
    except FileNotFoundError:
        logger.error("Configuration file 'config.yaml' not found.")
        return
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return

    # Override config with command-line arguments
    config["domain"] = args.domain
    config["engines"] = {engine: True for engine in args.engines.split(",")}
    config["output_file"] = args.output
    config["ports"] = args.ports.split(",") if args.ports else None
    config["verbose"] = args.verbose

    # Disable color if requested
    if args.no_color:
        from output.console_writer import no_color
        no_color()

    # Load plugins
    try:
        plugins = load_plugins()
    except Exception as e:
        logger.error(f"Error loading plugins: {e}")
        return

    # Enumerate subdomains using selected engines
    tasks = []
    for engine_name, enabled in config["engines"].items():
        if enabled and engine_name in plugins:
            try:
                engine = plugins[engine_name](config["domain"], config["api_keys"].get(engine_name))
                tasks.append(engine.enumerate())
            except Exception as e:
                logger.error(f"Error initializing {engine_name} engine: {e}")

    # Gather results from all engines
    try:
        results = await asyncio.gather(*tasks)
        subdomains = set().union(*results)
    except Exception as e:
        logger.error(f"Error during subdomain enumeration: {e}")
        return

    # Brute-force subdomains if enabled
    if args.bruteforce:
        try:
            from utils.subbrute import SubBrute
            wordlist = "utils/wordlists/subdomains.txt"  # Path to wordlist
            resolvers = ["8.8.8.8", "8.8.4.4"]  # DNS resolvers
            subbrute = SubBrute(config["domain"], wordlist, resolvers, threads=config.get("threads", 30))
            brute_subdomains = subbrute.enumerate()
            subdomains.update(brute_subdomains)
        except Exception as e:
            logger.error(f"Error during brute-forcing: {e}")

    # Write results to file if output file is specified
    if config["output_file"]:
        try:
            write_to_file(config["output_file"], subdomains)
        except Exception as e:
            logger.error(f"Error writing to file: {e}")

    # Write results to console
    try:
        write_to_console(subdomains, colorize=not args.no_color)
    except Exception as e:
        logger.error(f"Error writing to console: {e}")

    # Scan ports if specified
    if config.get("ports"):
        try:
            scanner = PortScanner(subdomains, config["ports"])
            scanner.run()
        except Exception as e:
            logger.error(f"Error during port scanning: {e}")

if __name__ == "__main__":
    asyncio.run(main())