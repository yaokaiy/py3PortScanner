import socket
import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import Mock, patch

from pyportscanner import PortScanner, pyscanner


class PortScannerTest(unittest.TestCase):
    def test_public_import(self):
        self.assertIs(PortScanner, pyscanner.PortScanner)

    def test_port_selection(self):
        all_ports = PortScanner().get_target_ports()
        self.assertEqual(len(all_ports), 24)
        self.assertEqual(all_ports, sorted(set(all_ports)))
        self.assertEqual(PortScanner(1).get_target_ports(), [443])
        self.assertEqual(PortScanner(2).get_target_ports(), [80, 443])
        self.assertEqual(PortScanner().get_top_k_ports(100), all_ports)

    def test_explicit_ports_are_copied_and_deduplicated(self):
        ports = [8443, 8000, 8443]
        scanner = PortScanner(ports)
        ports.clear()
        result = scanner.get_target_ports()
        self.assertEqual(result, [8443, 8000])
        result.clear()
        self.assertEqual(scanner.get_target_ports(), [8443, 8000])

    def test_invalid_ports(self):
        for argument in ([True], ["80"], [80.0], True, 1.0, "80", (80,)):
            with self.subTest(argument=argument), self.assertRaises(TypeError):
                PortScanner(argument)
        for argument in ([0], [-1], [65536], 0, -1):
            with self.subTest(argument=argument), self.assertRaises(ValueError):
                PortScanner(argument)
        with self.assertRaises(ValueError):
            PortScanner().get_top_k_ports(-1)

    def test_invalid_thread_limits(self):
        for limit, error in ((0, ValueError), (50001, ValueError), (True, TypeError), (2.0, TypeError)):
            with self.subTest(limit=limit), self.assertRaises(error):
                PortScanner(thread_limit=limit)
        scanner = PortScanner(thread_limit=2)
        with self.assertRaises(ValueError):
            scanner.thread_limit = 0
        self.assertEqual(scanner.thread_limit, 2)

    def test_timeouts(self):
        scanner = PortScanner(timeout=0.25)
        self.assertEqual(scanner.timeout_val, 0.25)
        for timeout in (0, -1, float("inf"), float("nan"), 10**1000):
            with self.subTest(timeout=timeout), self.assertRaises(ValueError):
                scanner.timeout_val = timeout
        with self.assertRaises(TypeError):
            PortScanner(timeout=True)
        self.assertEqual(scanner.timeout_val, 0.25)

    @patch("pyportscanner.pyscanner.socket.gethostbyname")
    def test_empty_scan_and_invalid_targets_do_not_resolve(self, resolve):
        self.assertEqual(PortScanner([]).scan("localhost"), {})
        self.assertEqual(PortScanner([8000]).scan("https://[::1"), {})
        resolve.assert_not_called()

    @patch("pyportscanner.pyscanner.socket.gethostbyname")
    def test_resolution_failure(self, resolve):
        for error in (socket.gaierror, UnicodeError):
            with self.subTest(error=error):
                resolve.reset_mock()
                resolve.side_effect = error
                self.assertEqual(PortScanner([8000]).scan("https://localhost:9000/check"), {})
                resolve.assert_called_once_with("localhost")

    @patch("pyportscanner.pyscanner.socket.socket")
    @patch("pyportscanner.pyscanner.socket.gethostbyname", return_value="127.0.0.1")
    def test_tcp_results_with_one_worker(self, resolve, create_socket):
        connection = create_socket.return_value
        connection.connect_ex.side_effect = [0, 1]
        scanner = PortScanner([8000, 8443], thread_limit=1, timeout=0.25, verbose=True)
        output = StringIO()
        with redirect_stdout(output):
            self.assertEqual(scanner.scan("https://localhost:9000"), {8000: "OPEN", 8443: "CLOSE"})
        resolve.assert_called_once_with("localhost")
        self.assertEqual(
            [call.args[0] for call in connection.connect_ex.call_args_list],
            [("127.0.0.1", 8000), ("127.0.0.1", 8443)],
        )
        self.assertEqual(connection.close.call_count, 2)
        self.assertEqual(connection.settimeout.call_args.args, (0.25,))
        self.assertIn("8000/TCP", output.getvalue())
        self.assertNotIn("8443/TCP", output.getvalue())

    @patch("pyportscanner.pyscanner.socket.socket")
    @patch("pyportscanner.pyscanner.socket.gethostbyname", return_value="127.0.0.1")
    def test_socket_is_closed_on_setup_and_connect_failure(self, resolve, create_socket):
        connection = create_socket.return_value
        for operation in (connection.settimeout, connection.connect_ex):
            with self.subTest(operation=operation):
                connection.reset_mock(side_effect=True)
                operation.side_effect = OSError
                self.assertEqual(PortScanner([8000]).scan("localhost"), {8000: "CLOSE"})
                connection.close.assert_called_once_with()

    @patch("pyportscanner.pyscanner.socket.socket")
    @patch("pyportscanner.pyscanner.socket.gethostbyname", return_value="127.0.0.1")
    def test_socket_creation_failure(self, resolve, create_socket):
        create_socket.side_effect = OSError
        self.assertEqual(PortScanner([8000]).scan("localhost"), {8000: "CLOSE"})

    @patch("pyportscanner.pyscanner.socket.socket")
    @patch("pyportscanner.pyscanner.socket.gethostbyname", return_value="127.0.0.1")
    def test_legacy_message_is_sent_over_udp_and_open_tcp(self, resolve, create_socket):
        tcp = Mock()
        udp = Mock()
        tcp.connect_ex.return_value = 0
        create_socket.side_effect = [tcp, udp]
        self.assertEqual(PortScanner([8000]).scan("localhost", "héllo"), {8000: "OPEN"})
        udp.sendto.assert_called_once_with("héllo".encode(), ("127.0.0.1", 8000))
        tcp.sendall.assert_called_once_with("héllo".encode())
        tcp.close.assert_called_once_with()
        udp.close.assert_called_once_with()

    def test_loopback_listener(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
            try:
                listener.bind(("127.0.0.1", 0))
            except PermissionError as error:
                self.skipTest(f"Loopback bind is unavailable: {error}")
            listener.listen()
            host, port = listener.getsockname()
            scanner = PortScanner([port], timeout=0.5)
            self.assertEqual(scanner.scan(host), {port: "OPEN"})
