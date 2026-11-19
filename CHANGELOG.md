# Changelog

Versions are monotonically increased based on Semantic Versioning.

***

## 0.4.0

- Build and install with `pyproject.toml` on Python 3.11 and newer. The package has no runtime dependencies.
- Replace the bundled Nmap database with a built-in list of 24 TCP ports. Use an explicit list to keep the same targets across upgrades.
- Validate ports, thread limits, and timeouts before starting a check. Fractional timeouts are supported.
- Close sockets after setup and connection errors. Verbose output identifies results as TCP.
- Replace Travis CI with GitHub Actions for tests, wheel and source builds, and distribution metadata checks.
- Release verified distributions to PyPI through GitHub Actions Trusted Publishing.
- Add an API reference, a self-contained loopback example, and a typing marker for installed packages.

## V0.3 (10/09/2018)

### Backward incompatible changes:
No longer compatible with python 2.7.
For a version compatible with python 2.7, refer to [v0.2](https://github.com/YaokaiYang-assaultmaster/PythonPortScanner).

### Deprecations
None

### Changes
Migrate to python version >= 3.0.
Integrate the whole [nmap](https://github.com/nmap/nmap) port list into the project.

## V0.2 (09/12/2017)

### Backward incompatible changes
None

### Deprecations
None

### Changes
Fixed [issue #1](https://github.com/YaokaiYang-assaultmaster/PythonPortScanner/issues/1). 
Specifically, fixed Windows has no `SO_REUSEPORT` for TCP socket error and change message 
encoding to `utf-8` before sending out. 

***

## V0.1 (05/30/2017)

### Backward incompatible changes
None

### Deprecations
None

### Changes
Initialized the whole project. First version finished. 
