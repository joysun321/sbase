#!/home/nick/.cache/pypoetry/virtualenvs/selbase-env-ElBpnQdt-py3.10/bin/python3
"""
Web Scraper using SeleniumBase
Fetches content from websites with bot detection and CAPTCHA handling
"""

import sys
import argparse
import logging
from seleniumbase import SB  # type: ignore


def fetch_page(url, output_filename=None):
    """
    Fetch HTML content from URL using SeleniumBase with undetected Chrome mode

    Args:
        url: Target URL to scrape
        output_filename: Optional filename to save the HTML content. If None, prints to stdout.

    Returns:
        True if successful, False otherwise
    """
    logging.info(f"Target URL: {url}")

    try:
        # Create SeleniumBase context with undetected Chrome mode
        with SB(uc=True, test=True, headed=True) as sb:
            logging.info("Activating CDP mode...")
            # Activate Chrome DevTools Protocol mode for better control
            sb.activate_cdp_mode(url)

            # Initial wait for page load
            logging.info("Waiting for initial page load...")
            sb.sleep(2)

            # Check and handle CAPTCHA if present
            logging.info("Checking for CAPTCHA...")
            try:
                # However, this is unreliable
                sb.uc_gui_click_captcha()
                logging.info("CAPTCHA detected and handled")
                # Wait for CAPTCHA processing
                sb.sleep(2)
            except Exception:
                logging.info("No CAPTCHA detected or already solved")

            # Extract page source
            logging.info("Extracting page content...")
            html_content = sb.get_page_source()

            if output_filename:
                # Save HTML content to file
                logging.info(f"Saving content to {output_filename}...")
                with open(output_filename, "w", encoding="utf-8") as f:
                    f.write(html_content)
            else:
                print(html_content)

            return True

    except KeyboardInterrupt:
        logging.warning("Operation cancelled by user")
        return False

    except Exception as e:
        logging.error(f"Error occurred: {type(e).__name__}: {str(e)}")
        return False


def main():
    """Main entry point"""
    # Configure logging
    logging.basicConfig(
        stream=sys.stdout,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True,  # Ensure configuration is applied if previously configured
    )

    parser = argparse.ArgumentParser(description="SeleniumBase Web Scraper")
    parser.add_argument("url", help="Target URL to scrape")
    parser.add_argument(
        "-o",
        "--output",
        help="Output filename to save HTML content instead of printing to stdout",
    )

    args = parser.parse_args()

    # Validate URL format
    if not args.url.startswith(("http://", "https://")):
        print("Error: URL must start with http:// or https://", file=sys.stderr)
        sys.exit(1)

    # Fetch the page
    success = fetch_page(args.url, args.output)

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
