import re
from urllib.parse import urlsplit


def get_domain(url: str) -> str:
    """Return the hostname from a bare target or HTTP(S) URL."""
    if not isinstance(url, str):
        return ""

    url = url.strip()
    if not url or not url.isprintable() or " " in url or "\\" in url:
        return ""

    scheme = re.match(r"[A-Za-z][A-Za-z0-9+.-]*://", url)
    if scheme:
        if scheme.group().lower() not in {"http://", "https://"}:
            return ""
    elif not url.startswith("//"):
        url = f"//{url}"

    try:
        target = urlsplit(url)
        if target.port == 0:
            return ""
        return target.hostname or ""
    except ValueError:
        return ""
