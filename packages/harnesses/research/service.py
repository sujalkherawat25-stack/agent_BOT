from dataclasses import dataclass
from hashlib import sha256
import html
import re
from urllib.parse import urlparse

import httpx


@dataclass
class VerifiedSource:
    url: str
    title: str | None
    snippet: str | None
    content_hash: str
    verified: bool


def _title(body: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", body, re.I | re.S)
    return html.unescape(re.sub(r"\s+", " ", match.group(1)).strip())[:500] if match else None


async def retrieve_sources(urls: list[str], *, allow_external: bool = False) -> list[VerifiedSource]:
    """Fetch only URLs explicitly supplied by the user after network opt-in."""
    if not allow_external:
        raise PermissionError("External research requests are disabled")
    async with httpx.AsyncClient(timeout=15, follow_redirects=True, headers={"User-Agent": "MementoResearch/1.0"}) as client:
        unique: list[VerifiedSource] = []
        seen: set[str] = set()
        for url in urls:
            parsed = urlparse(url)
            if parsed.scheme not in {"http", "https"} or parsed.netloc in seen:
                continue
            seen.add(parsed.netloc)
            try:
                response = await client.get(url)
                if response.status_code >= 400 or not response.text.strip():
                    continue
                body = response.text[:2_000_000]
                unique.append(VerifiedSource(url=str(response.url), title=_title(body), snippet=re.sub(r"\s+", " ", body)[:600], content_hash=sha256(body.encode("utf-8", "ignore")).hexdigest(), verified=True))
            except (httpx.HTTPError, UnicodeError):
                continue
            if len(unique) >= max_sources:
                break
        return unique
