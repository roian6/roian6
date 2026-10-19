import base64
import binascii
import errno
import http.client
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Final


SOURCE: Final = "https://tokscale.ai/api/embed/roian6/svg?template=graph&color=blue&theme=dark&sort=cost&rank=plain&tokens=compact&cost=compact"
API: Final = "https://api.github.com/repos/roian6/roian6/contents/tokscale.svg"
READ: Final = API + "?ref=profile-assets"
MAX_SVG: Final = 256 * 1024
MAX_JSON: Final = 512 * 1024
SVG: Final = "{http://www.w3.org/2000/svg}"
ELEMENTS: Final = {SVG + tag for tag in ("svg", "defs", "style", "g", "rect", "text", "title")}
ATTRIBUTES: Final = frozenset((
    "data-template", "width", "height", "viewBox", "fill", "role", "aria-label",
    "x", "y", "rx", "stroke", "font-family", "font-size", "font-weight", "text-anchor",
    "data-fit-max-width", "data-contribution-panel", "data-bottom", "data-card-footer-y",
))


class CardError(Exception):
    def __init__(self, message: str, retryable: bool = False, status: int = 0) -> None:
        super().__init__(message)
        self.retryable = retryable
        self.status = status


def validate_svg(body: bytes) -> bytes:
    if not body or len(body) > MAX_SVG:
        raise CardError("Source SVG is empty or exceeds 256 KiB")
    try:
        text = body.decode("utf-8")
        declaration = re.match(r"\ufeff?\s*<\?xml\s+[^?]*\?>", text)
        if declaration:
            encoding = re.search(r"encoding\s*=\s*['\"]([^'\"]+)['\"]", declaration[0])
            if encoding and encoding[1].lower() != "utf-8":
                raise CardError("Source must declare UTF-8")
            text = text[declaration.end():]
        if re.search(r"<!\s*(?:DOCTYPE|ENTITY)|<\?", text, re.IGNORECASE):
            raise CardError("Source contains prohibited XML declarations")
        root = ET.fromstring(body)
    except (UnicodeDecodeError, ET.ParseError):
        raise CardError("Source is not valid UTF-8 SVG", retryable=True) from None
    if root.tag != SVG + "svg":
        raise CardError("Source is not SVG", retryable=True)
    for element in root.iter():
        if element.tag not in ELEMENTS or any(key not in ATTRIBUTES for key in element.attrib):
            raise CardError("Source contains unsupported SVG elements or attributes")
        for paint in (element.get("fill"), element.get("stroke")):
            if paint is not None and not re.fullmatch(r"none|#[0-9a-fA-F]{3,8}|rgba?\([\d.,%\s]+\)", paint):
                raise CardError("Source contains unsupported paint or a resource reference")
        if element.tag == SVG + "style" and (
            len(element) or re.sub(r"\s+", "", element.text or "") != "text{font-variant-numeric:tabular-nums}"
        ):
            raise CardError("Source contains unsupported CSS")
    labels = ["".join(e.itertext()).strip() for e in root.iter(SVG + "text")]
    if re.search(r"error|fail(?:ed|ure)?|unavailable|unable|not found|try again|rate limit|unauthorized|forbidden|went wrong",
                 " ".join(root.itertext()), re.IGNORECASE):
        raise CardError("Source contains an error card", retryable=True)
    if (root.get("data-template") != "graph" or root.get("width") != "680"
            or root.get("aria-label") != "Tokscale contribution graph for @roian6"):
        raise CardError("Source account, template or width does not match")
    height = root.get("height", "")
    if not re.fullmatch(r"\d+(?:\.\d+)?", height) or not 100 <= float(height) <= 2000:
        raise CardError("Source height is outside the supported card range")
    panels = [e for e in root.iter(SVG + "g") if e.get("data-contribution-panel") == "true"]
    if (not {"@roian6", "Tokscale", "Tokens", "Cost", "Contribution activity"}.issubset(labels)
            or len(panels) != 1 or not any(
                re.fullmatch(r"\d{4}-\d{2}-\d{2}\s+.+\s+level [0-4]", e.text or "")
                for e in panels[0].iter(SVG + "title"))):
        raise CardError("Source lacks a successful contribution graph", retryable=True)
    return body


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def request_bytes(request: urllib.request.Request, limit: int) -> bytes:
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    try:
        with opener.open(request, timeout=45) as response:
            if response.status != 200:
                raise CardError(f"Unexpected HTTP status {response.status}", status=response.status)
            body = response.read(limit + 1)
    except urllib.error.HTTPError as error:
        with error:
            raise CardError(f"HTTP {error.code}", error.code == 429 or 500 <= error.code <= 599,
                            error.code) from None
    except (urllib.error.URLError, OSError, http.client.HTTPException) as error:
        reason = error.reason if isinstance(error, urllib.error.URLError) else error
        transient = isinstance(reason, (TimeoutError, ConnectionError, http.client.IncompleteRead,
                                        http.client.BadStatusLine))
        if isinstance(reason, OSError):
            transient = transient or reason.errno in {
                errno.ECONNRESET, errno.ECONNREFUSED, errno.ECONNABORTED, errno.ETIMEDOUT,
                errno.EHOSTUNREACH, errno.ENETUNREACH, errno.EPIPE, socket.EAI_AGAIN,
            }
        if isinstance(reason, ssl.SSLError):
            transient = False
        raise CardError("Network request failed" if transient else "Network or TLS configuration failed",
                        retryable=transient) from None
    if len(body) > limit:
        raise CardError("Response exceeds the size limit")
    return body


def fetch_svg() -> bytes:
    for attempt in range(3):
        try:
            request = urllib.request.Request(SOURCE, headers={"Accept": "image/svg+xml"}, method="GET")
            return validate_svg(request_bytes(request, MAX_SVG))
        except CardError as error:
            if not error.retryable or attempt == 2:
                raise
            time.sleep(attempt + 1)
    raise AssertionError("Unreachable retry state")


@dataclass(frozen=True, slots=True)
class Asset:
    content: bytes
    sha: str


def github_request(token: str, payload: bytes | None = None) -> bytes:
    request = urllib.request.Request(
        READ if payload is None else API, data=payload,
        headers={"Authorization": "Bearer " + token, "Accept": "application/vnd.github+json",
                 "X-GitHub-Api-Version": "2022-11-28", "Content-Type": "application/json",
                 "Cache-Control": "no-cache", "User-Agent": "tokscale-profile-card"},
        method="GET" if payload is None else "PUT",
    )
    return request_bytes(request, MAX_JSON)


def read_asset(token: str) -> Asset:
    raw = github_request(token)
    try:
        value = json.loads(raw)
        if (not isinstance(value, dict) or value.get("type") != "file"
                or value.get("encoding") != "base64" or value.get("path") != "tokscale.svg"
                or value.get("name") != "tokscale.svg" or "submodule_git_url" in value
                or not isinstance(value.get("content"), str)
                or not isinstance(value.get("sha"), str)
                or not re.fullmatch(r"[0-9a-f]{40}", value["sha"])):
            raise CardError("GitHub target must be the existing normal base64 file")
        content = base64.b64decode(value["content"].replace("\n", ""), validate=True)
        if type(value.get("size")) is not int or value["size"] != len(content) or len(content) > MAX_SVG:
            raise CardError("GitHub target has inconsistent or excessive size")
        return Asset(content, value["sha"])
    except (ValueError, UnicodeDecodeError, binascii.Error, RecursionError):
        raise CardError("GitHub returned malformed file content") from None


def refresh(token: str) -> str:
    source = fetch_svg()
    current = read_asset(token)
    if current.content == source:
        return "Tokscale card unchanged"
    bot = {"name": "github-actions[bot]", "email": "41898282+github-actions[bot]@users.noreply.github.com"}
    payload = json.dumps({
        "message": "Update Tokscale card", "branch": "profile-assets", "sha": current.sha,
        "content": base64.b64encode(source).decode("ascii"), "author": bot, "committer": bot,
    }).encode("utf-8")
    try:
        github_request(token, payload)
    except CardError as error:
        if 300 <= error.status < 500 and error.status not in (408, 429):
            raise
    try:
        confirmed = read_asset(token)
    except CardError as error:
        raise CardError(f"Write outcome uncertain: readback failed ({error}); no write retry") from None
    if confirmed.content != source:
        raise CardError("Write outcome uncertain: readback differs; no write retry")
    return "Tokscale card updated and verified"


def main() -> int:
    try:
        if "GITHUB_REPOSITORY" in os.environ and os.environ["GITHUB_REPOSITORY"] != "roian6/roian6":
            raise CardError("Refusing to run outside roian6/roian6")
        token = os.environ.get("GITHUB_TOKEN", "")
        # Provider-issued tokens are opaque: enforce header safety, not a guessed format.
        if (not token or len(token) > 4096
                or any(not 33 <= ord(char) <= 126 for char in token)):
            raise CardError("GITHUB_TOKEN is missing or invalid")
        print(refresh(token))
        return 0
    except CardError as error:
        print(f"Tokscale refresh failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
