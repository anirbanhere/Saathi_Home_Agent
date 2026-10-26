import argparse
import logging
import os

from .server import make_server
from .service import DEFAULT_DB, HomeAgent


def main():
    parser = argparse.ArgumentParser(description="Run the loopback-only Home Agent demo.")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--db", default=os.environ.get("HOME_AGENT_DB", str(DEFAULT_DB)))
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    try:
        server = make_server(HomeAgent(args.db), args.port)
    except OSError:
        parser.exit(1, f"Cannot start on port {args.port}. Stop the existing server or choose --port 8766.\n")
    print(f"Home Agent: http://127.0.0.1:{server.server_port}", flush=True)
    print("Local demo only. Train fixtures and payment sandboxes; no external services enabled by default.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
