"""
Guptchar CLI Interface.
Command-line runner for high-precision lead-generation and data extraction.
"""

import argparse
import logging
import sys

from guptchar.pipeline import GuptcharPipeline

BANNER = r"""
   ____              _       _                 
  / ___|_   _ _ __ _| |_ ___| |__   __ _ _ __  
 | |  _| | | | '_ \_  __/ __| '_ \ / _` | '__| 
 | |_| | |_| | |_) || || (__| | | | (_| | |    
  \____|\__,_| .__/  \__\___|_| |_|\__,_|_|    
             |_|                               
  >> Guptchar Core Data Extraction Engine (V1.0) <<
"""


def setup_logging(verbose: bool = False):
    """Configure console logging format."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S",
    )


def main():
    """CLI Entrypoint for Guptchar."""
    parser = argparse.ArgumentParser(
        description="Guptchar Core Data Extraction Engine (V1.0) - High-Precision Lead Generation",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--country",
        "-c",
        type=str,
        default="United States",
        help="Target Country (e.g., 'United States')",
    )
    parser.add_argument(
        "--city",
        "-C",
        type=str,
        required=True,
        help="Target City (e.g., 'New York')",
    )
    parser.add_argument(
        "--sector",
        "-s",
        "--query",
        type=str,
        required=True,
        help="Target Sector or Keyword (e.g., 'Hedge Funds', 'Financial Compliance')",
    )
    parser.add_argument(
        "--limit",
        "-l",
        type=int,
        default=5,
        help="Maximum number of business entities to extract",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Disable automatic JSON export",
    )
    parser.add_argument(
        "--no-pdf",
        action="store_true",
        help="Disable automatic PDF dossier export",
    )
    parser.add_argument(
        "--json-output",
        type=str,
        default=None,
        help="Custom file path for JSON export",
    )
    parser.add_argument(
        "--pdf-output",
        type=str,
        default=None,
        help="Custom file path for PDF export",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in visible mode (default is headless)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose debug logging",
    )

    args = parser.parse_args()

    setup_logging(args.verbose)
    print(BANNER)
    print(f"Target Region : {args.city}, {args.country}")
    print(f"Target Sector : {args.sector}")
    print(f"Entity Limit  : {args.limit}")
    print("-" * 55)

    pipeline = GuptcharPipeline(headless=not args.no_headless)

    try:
        results = pipeline.run(
            country=args.country,
            city=args.city,
            sector_keyword=args.sector,
            limit=args.limit,
            export_json_file=not args.no_json,
            export_pdf_file=not args.no_pdf,
            json_output_path=args.json_output,
            pdf_output_path=args.pdf_output,
        )

        leads = results.get("leads", [])
        print("\n" + "=" * 65)
        print(f"EXTRACTION COMPLETE: Extracted {len(leads)} entities in {results.get('elapsed_seconds')}s")
        print("=" * 65)

        for i, lead in enumerate(leads, 1):
            print(f"\n[{i}] {lead['company_name']}")
            print(f"    Website: {lead['website']}")
            print(f"    Generic Contact Phone: {lead['generic_contact_number']}")
            print(f"    Primary Email: {lead['primary_email']}")
            print(f"    Address: {lead['address']}")
            print(f"    Summary: {lead['one_sentence_description']}")
            execs = lead.get("executives_and_contacts", [])
            print(f"    Executives Indexed: {len(execs)}")
            for ex in execs:
                print(f"      - {ex['name']} ({ex['title']}) | Ph: {ex['phone']} | Src: {ex['source']}")

        print("\n" + "-" * 65)
        if results.get("json_file"):
            print(f"[+] JSON Export Saved: {results['json_file']}")
        if results.get("pdf_file"):
            print(f"[+] PDF Dossier Saved: {results['pdf_file']}")
        print("-" * 65 + "\n")

    except KeyboardInterrupt:
        print("\n[!] Execution cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Pipeline execution error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
