# Contributing

Use Python 3.11 or newer in a virtual environment. From the repository root, install the editable package and run the tests.

```sh
python -m pip install -e .
python -m unittest discover -s tests -v
python examples/PortScanExample.py
```

The package lives in `src/pyportscanner/`, the API reference is in `docs/`, and runnable examples are in `examples/`. Use a loopback listener or socket mocks to reproduce networking issues.

When [reporting a bug](https://github.com/yaokaiy/py3PortScanner/issues/new), include the package version, Python version, operating system, the smallest example that reproduces the issue, and the expected result.
