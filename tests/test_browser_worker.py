import socket
import unittest
from unittest.mock import patch

from home_agent.browser_proxy import PublicProxy
from home_agent.browser_worker import create_worker


class WorkerTests(unittest.TestCase):
    def test_worker_rejects_code_credentials_and_private_urls_before_execution(self):
        with patch("home_agent.browser_worker.run_browser") as runner:
            client = create_worker(runner).test_client()
            for payload in [
                {"url": "https://127.0.0.1"},
                {"url": "https://example.com", "javascript": "fetch('secret')"},
                {
                    "url": "https://example.com",
                    "actions": [{"type": "evaluate", "selector": "body"}],
                },
                {"url": "https://example.com/login"},
            ]:
                self.assertGreaterEqual(
                    client.post("/observe", json=payload).status_code, 400
                )
            runner.assert_not_called()

    def test_proxy_blocks_private_dns_and_pins_actual_connection_to_public_ip(self):
        with PublicProxy() as proxy:
            address = proxy.server.server_address
            with patch(
                "home_agent.browser_proxy.public_addresses",
                return_value=["93.184.216.34"],
            ), patch(
                "home_agent.browser_proxy.socket.create_connection",
                side_effect=OSError(),
            ) as connect:
                # Use socket.socket directly so the assertion observes only outbound connections.
                with socket.socket() as client:
                    client.connect(address)
                    client.sendall(b"CONNECT example.com:443 HTTP/1.1\r\n\r\n")
                    self.assertIn(b"403", client.recv(1024))
                connect.assert_called_once_with(("93.184.216.34", 443), timeout=10)
            with patch("home_agent.browser_proxy.socket.create_connection") as connect:
                with socket.socket() as client:
                    client.connect(address)
                    client.sendall(b"CONNECT 169.254.169.254:443 HTTP/1.1\r\n\r\n")
                    self.assertIn(b"403", client.recv(1024))
                connect.assert_not_called()
