"""
Guptchar Unified Entrypoint.
Launch either the command-line extractor or the FastAPI server & web console.
"""

import argparse
import sys
import uvicorn

from guptchar.cli import main as cli_main


def main():
    parser = argparse.ArgumentParser(
        description="Guptchar Core Data Extraction Engine (V1.0)",
        add_help=False,
    )
    parser.add_argument("mode", nargs="?", default="cli", choices=["cli", "serve"], help="Execution mode ('cli' or 'serve')")

    args, unknown = parser.parse_known_args()

    if args.mode == "serve":
        serve_parser = argparse.ArgumentParser(description="Start Guptchar FastAPI Server")
        serve_parser.add_argument("--host", default="0.0.0.0", help="Host interface to bind")
        serve_parser.add_argument("--port", type=int, default=8000, help="Port to bind")
        serve_args = serve_parser.parse_args(unknown)

        print(f"[*] Starting Guptchar FastAPI Server on http://{serve_args.host}:{serve_args.port}")
        uvicorn.run("guptchar.api.server:app", host=serve_args.host, port=serve_args.port, reload=False)
    else:
        # Pass remaining arguments to CLI runner
        sys.argv = [sys.argv[0]] + unknown
        cli_main()


if __name__ == "__main__":
    main()
