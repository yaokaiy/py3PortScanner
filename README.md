<h1>
  <picture>
    <source srcset="docs/assets/pyportscanner.png">
    <img src="https://raw.githubusercontent.com/yaokaiy/py3PortScanner/master/docs/assets/pyportscanner.png" alt="" width="36" height="36" align="top">
  </picture>
  pyportscanner
</h1>

Check TCP port reachability on a single IPv4 host.

Python 3.11+ · Zero runtime dependencies

[API reference](https://github.com/yaokaiy/py3PortScanner/blob/master/docs/api.md) · [Changelog](https://github.com/yaokaiy/py3PortScanner/blob/master/CHANGELOG.md) · [PyPI](https://pypi.org/project/pyportscanner/)

## Installation

```sh
python -m pip install "pyportscanner>=0.4.0"
```

From a local checkout, run `python -m pip install .` in the repository root.

## Quickstart

Check a local service on port 8000.

```python
from pyportscanner import PortScanner

scanner = PortScanner(target_ports=[8000], timeout=0.5)
print(scanner.scan("127.0.0.1"))
```

```text
{8000: 'OPEN'}
```

The example output assumes a service is listening. The result uses `"CLOSE"` when a connection fails, including when it times out. To try it with a listener that the example starts for you, run `python examples/PortScanExample.py` from an installed checkout.

## Port selection

| Input | Ports checked |
| --- | --- |
| `target_ports=[8000, 8443]` | The listed ports |
| `target_ports=3` | The first three ports in the built-in priority list |
| `target_ports=None` | All 24 built-in ports |

The legacy import `from pyportscanner import pyscanner` still works. Version 0.4 replaces the bundled Nmap service database with the built-in list. Pass explicit ports to keep the same targets across versions.

## Develop

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
```

The Python package lives in `src/pyportscanner/`, the API guide and icon in `docs/`, and runnable usage in `examples/`.

## Build distributions

```sh
python -m pip install build twine
python -m build
python -m twine check --strict dist/*
```

The build writes a wheel and source distribution to `dist/`.

## License

Apache-2.0. See the [license text](https://github.com/yaokaiy/py3PortScanner/blob/master/LICENSE).
