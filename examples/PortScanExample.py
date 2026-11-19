"""Try a TCP port check against a temporary listener on this machine."""

import socket

from pyportscanner import PortScanner


def main() -> None:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as listener:
        listener.bind(("127.0.0.1", 0))
        listener.listen()
        host, port = listener.getsockname()
        scanner = PortScanner(target_ports=[port], timeout=0.5)
        print(scanner.scan(host))


if __name__ == "__main__":
    main()
