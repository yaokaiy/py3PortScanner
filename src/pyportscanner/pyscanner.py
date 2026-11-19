import concurrent.futures
import socket
import time
from collections import deque
from contextlib import closing
from threading import TIMEOUT_MAX

from pyportscanner.etc.helper import get_domain


# Default order gives priority to common web, administration, and mail ports.
_DEFAULT_TCP_PORTS = (
    443, 80, 22, 53, 25, 3389, 445, 8080, 8443, 587, 993, 465,
    110, 143, 995, 21, 23, 139, 389, 636, 3306, 5432, 6379, 5900,
)


def _require_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")


class PortScanner:
    """Check TCP ports on a single IPv4 host."""

    def __init__(
        self,
        target_ports: list[int] | int | None = None,
        thread_limit: int = 100,
        timeout: float = 10,
        verbose: bool = False,
    ) -> None:
        self.thread_limit = thread_limit
        self.timeout_val = timeout
        self._verbose = verbose

        if target_ports is None:
            self.targets = sorted(_DEFAULT_TCP_PORTS)
        elif isinstance(target_ports, list):
            for port in target_ports:
                _require_int(port, "Port")
                if not 1 <= port <= 65535:
                    raise ValueError(f"Port must be between 1 and 65535: {port}")
            self.targets = list(dict.fromkeys(target_ports))
        else:
            self.targets = self.extract_list(target_ports)

    @property
    def timeout_val(self) -> float:
        """Per-socket timeout in seconds."""
        return self._timeout

    @timeout_val.setter
    def timeout_val(self, timeout: float) -> None:
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)):
            raise TypeError("Timeout must be a number")
        if not 0 < timeout < TIMEOUT_MAX:
            raise ValueError("Timeout must be positive, finite, and within the platform limit")
        self._timeout = timeout

    @property
    def thread_limit(self) -> int:
        """Maximum number of concurrent port checks."""
        return self._thread_limit

    @thread_limit.setter
    def thread_limit(self, thread_limit: int) -> None:
        _require_int(thread_limit, "Thread limit")
        if not 1 <= thread_limit <= 50000:
            raise ValueError("Thread limit must be between 1 and 50000")
        self._thread_limit = thread_limit

    def extract_list(self, target_port_rank: int) -> list[int]:
        """Select the first k default ports by priority and sort by port number."""
        _require_int(target_port_rank, "Port count")
        if target_port_rank <= 0:
            raise ValueError("Port count must be positive")
        return sorted(_DEFAULT_TCP_PORTS[:target_port_rank])

    def get_target_ports(self) -> list[int]:
        """Return a copy of the selected ports."""
        return self.targets.copy()

    def get_top_k_ports(self, k: int) -> list[int]:
        """Return up to k of the built-in ports."""
        return self.extract_list(k)

    def scan(self, objective: str, message: str = "") -> dict[int, str]:
        """Return a mapping from TCP ports to 'OPEN' or 'CLOSE'."""
        if not isinstance(message, str):
            raise TypeError("Message must be a string")

        host = get_domain(objective)
        if not host or not self.targets:
            return {}

        try:
            ip = socket.gethostbyname(host)
        except (OSError, UnicodeError):
            if self._verbose:
                print(f"Target {host} could not be resolved to IPv4.")
            return {}

        if self._verbose:
            print(f"Checking {host} ({ip})")
        return self._scan_ports(ip, message)

    def _scan_ports(self, ip: str, message: str) -> dict[int, str]:
        results = dict.fromkeys(self.targets, "CLOSE")
        pending: deque[concurrent.futures.Future[tuple[int, str]]] = deque()
        thread_limit = self.thread_limit

        with concurrent.futures.ThreadPoolExecutor(max_workers=thread_limit) as executor:
            for port in results:
                pending.append(executor.submit(self._check_port, ip, port, message))
                while len(pending) >= thread_limit:
                    self._collect_results(results, pending)
                    if len(pending) >= thread_limit:
                        time.sleep(0.01)

            while pending:
                self._collect_results(results, pending)
                if pending:
                    time.sleep(0.01)

        if self._verbose:
            for port, status in sorted(results.items()):
                if status == "OPEN":
                    print(f"{port}/TCP  {status}")

        return results

    @staticmethod
    def _collect_results(
        results: dict[int, str],
        pending: deque[concurrent.futures.Future[tuple[int, str]]],
    ) -> None:
        for _ in range(len(pending)):
            task = pending.popleft()
            if task.done():
                port, status = task.result()
                results[port] = status
            else:
                pending.append(task)

    def _check_port(self, ip: str, port: int, message: str) -> tuple[int, str]:
        address = (ip, port)
        payload = message.encode("utf-8", errors="replace")
        status = "CLOSE"

        try:
            with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as tcp:
                timeout = self.timeout_val
                tcp.settimeout(timeout)
                if payload:
                    try:
                        with closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as udp:
                            udp.settimeout(timeout)
                            udp.sendto(payload, address)
                    except OSError:
                        # Continue the TCP check without sending another notification.
                        payload = b""
                if tcp.connect_ex(address) == 0:
                    status = "OPEN"
                    if payload:
                        tcp.sendall(payload)
        except OSError:
            pass
        return port, status
