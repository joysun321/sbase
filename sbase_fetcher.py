"""
Web Scraper using SeleniumBase
Fetches content from websites with bot detection and CAPTCHA handling
"""

import sys
import argparse
import logging
from seleniumbase import SB  # type: ignore


def normalize_surrogates(content):
    """Convert UTF-16 surrogate pairs and replace malformed lone surrogates."""
    try:
        content.encode("utf-8")
        return content
    except UnicodeEncodeError:
        logging.warning("Page content contains UTF-16 surrogates; normalizing them")
        return content.encode("utf-16", errors="surrogatepass").decode(
            "utf-16", errors="replace"
        )


def fetch_page(
    url, output_filename=None, captcha_timeout_seconds=15, captcha_attempts=2
):
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
        # with SB(uc=True, test=True, headed=True) as sb:
        with SB(uc=True) as sb:
            logging.info("Activating CDP mode...")
            # Activate Chrome DevTools Protocol mode for better control
            sb.activate_cdp_mode(url)

            # Initial wait for page load
            logging.info("Waiting for initial page load...")
            sb.sleep(4)

            # Check and handle CAPTCHA if present
            logging.info("Checking for CAPTCHA...")
            try:
                sb.uc_gui_click_captcha()
                # Wait for CAPTCHA processing
                sb.sleep(2)
            except Exception:
                logging.info("No CAPTCHA detected or already solved")

            # Extract page source
            logging.info("Extracting page content...")

            # via javascript execution
            page_source = sb.execute_script(
                "return document.documentElement.outerHTML;"
            )
            logging.info(f"(JS) Initial page source length: {len(page_source)}")
            html_content = normalize_surrogates(page_source)
            logging.info(f"(JS) Normalized page source length: {len(html_content)}")

            # via SeleniumBase's get_page_source() method
            page_source = sb.get_page_source()
            logging.info(f"Initial page source length: {len(page_source)}")
            html_content = normalize_surrogates(page_source)
            logging.info(f"Normalized page source length: {len(html_content)}")

            # Refresh the page if html_content too short or empty
            if not html_content or len(html_content) < 30500:
                logging.info("Page content seems incomplete, refreshing the page...")
                sb.refresh()
                sb.sleep(2)
                page_source = sb.get_page_source()
                logging.info(f"Initial page source length: {len(page_source)}")
                html_content = normalize_surrogates(page_source)
                logging.info(f"Normalized page source length: {len(html_content)}")

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
        filename="/tmp/sbase_fetcher.log",
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
    parser.add_argument(
        "--captcha-timeout",
        type=float,
        default=15,
        metavar="SECONDS",
        help="Maximum seconds per CAPTCHA attempt (default: 15)",
    )
    parser.add_argument(
        "--captcha-attempts",
        type=int,
        default=2,
        metavar="COUNT",
        help="Total number of CAPTCHA attempts (default: 2)",
    )

    args = parser.parse_args()

    if args.captcha_timeout <= 0:
        parser.error("--captcha-timeout must be greater than zero")
    if args.captcha_attempts < 1:
        parser.error("--captcha-attempts must be at least one")

    # Validate URL format
    if not args.url.startswith(("http://", "https://")):
        print("Error: URL must start with http:// or https://", file=sys.stderr)
        sys.exit(1)

    # Fetch the page
    success = fetch_page(
        args.url,
        args.output,
        captcha_timeout_seconds=args.captcha_timeout,
        captcha_attempts=args.captcha_attempts,
    )

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
