# API reference

```python
from pyportscanner import PortScanner
```

## PortScanner

```python
PortScanner(target_ports=None, thread_limit=100, timeout=10, verbose=False)
```

| Parameter | Default | Behavior |
| --- | --- | --- |
| `target_ports` | `None` | Pass a list of ports from 1 to 65535, a positive integer count, or `None` for the built-in list. An explicit list preserves its order and skips duplicates. An empty list performs no checks. |
| `thread_limit` | `100` | Maximum concurrent TCP checks. Accepts integers from 1 to 50,000. |
| `timeout` | `10` | Per-socket timeout in seconds. Accepts positive finite numbers within the platform limit, including fractional values. |
| `verbose` | `False` | Print the resolved host and the open TCP ports. |

A value of the wrong type raises `TypeError`. Out-of-range numbers raise `ValueError`.

### Scan a target

```python
scanner.scan(objective, message="")
```

`objective` accepts an IPv4 address, hostname, or HTTP(S) URL. A URL provides the hostname. The scanner uses the ports supplied through `target_ports`.

| Result | Meaning |
| --- | --- |
| `{8000: "OPEN"}` | A TCP connection to port 8000 succeeded. |
| `{8000: "CLOSE"}` | A TCP connection to port 8000 failed, timed out, or encountered a socket error. |
| `{}` | The port list was empty, the target was invalid, or the hostname could not be resolved to IPv4. |

The optional legacy `message` argument attempts to send UTF-8 text in a UDP datagram. If the UDP send succeeds, it also attempts to send the text over a successful TCP connection. The result reflects the TCP connection even if a notification fails.

### Inspect or adjust a scanner

- `get_target_ports()` returns a copy of the selected ports.
- `get_top_k_ports(k)` and its legacy alias `extract_list(k)` return up to `k` built-in ports. The library selects them in priority order, then returns them in numeric order.
- Set `thread_limit` or `timeout_val` to adjust subsequent checks. Both properties apply the constructor's validation rules.

## Try it locally

The [loopback example](../examples/PortScanExample.py) opens a TCP listener on an available local port and checks it through the installed library.

```sh
python examples/PortScanExample.py
```
