"""Browser-enabled business intelligence sample agent.

This script shows how to combine the Bedrock Agentcore runtime with the
`strands-agent` orchestration library to gather structured business details
from a website. The heavy lifting (navigating pages) is delegated to the
Bedrock browser tool, while Python code handles parsing the collected HTML.

The script is intentionally lightweight and designed for instructional
purposes. It is not production hardened and omits advanced crawling features
such as robots.txt handling, throttling, or JavaScript execution.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import re
import uuid
from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence, Set

import boto3
from botocore.config import Config
from bs4 import BeautifulSoup

from strands import Agent, MemoryStore, Task, TaskContext  # type: ignore

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


@dataclass
class PageSnapshot:
    """Represents a single HTML page fetched via the browser tool."""

    url: str
    html: str
    title: str = ""
    outgoing_links: Sequence[str] = field(default_factory=tuple)

    @classmethod
    def from_html(cls, url: str, html: str) -> "PageSnapshot":
        soup = BeautifulSoup(html, "html5lib")
        title_tag = soup.find("title")
        title = title_tag.text.strip() if title_tag else ""
        links: Set[str] = set()
        for anchor in soup.find_all("a", href=True):
            href = anchor["href"].strip()
            if href.startswith("#"):
                continue
            links.add(href)
        return cls(url=url, html=html, title=title, outgoing_links=tuple(sorted(links)))


@dataclass
class BusinessSummary:
    """Structured business data assembled from one or more pages."""

    abn: Optional[str] = None
    emails: Set[str] = field(default_factory=set)
    phones: Set[str] = field(default_factory=set)
    addresses: Set[str] = field(default_factory=set)
    description: Optional[str] = None

    def merge(self, other: "BusinessSummary") -> None:
        if other.abn and not self.abn:
            self.abn = other.abn
        self.emails.update(other.emails)
        self.phones.update(other.phones)
        self.addresses.update(other.addresses)
        if other.description and not self.description:
            self.description = other.description

    def to_dict(self) -> dict:
        return {
            "abn": self.abn,
            "emails": sorted(self.emails),
            "phones": sorted(self.phones),
            "addresses": sorted(self.addresses),
            "description": self.description,
        }


class BusinessInfoParser:
    """Extracts business metadata from HTML content."""

    ABN_PATTERN = re.compile(r"\b\d{2}\s?\d{3}\s?\d{3}\s?\d{3}\b")
    EMAIL_PATTERN = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
    PHONE_PATTERN = re.compile(r"\+?\d[\d\s().-]{6,}\d")
    ADDRESS_HINTS = ("street", "st", "road", "rd", "ave", "avenue", "drive", "dr", "suite", "level")

    def parse(self, page: PageSnapshot) -> BusinessSummary:
        soup = BeautifulSoup(page.html, "html5lib")
        text = soup.get_text(" ")
        summary = BusinessSummary()

        abn_match = self.ABN_PATTERN.search(text)
        if abn_match:
            summary.abn = abn_match.group().replace(" ", "")

        summary.emails.update(email.lower() for email in self.EMAIL_PATTERN.findall(text))
        summary.phones.update(self._normalize_phone(number) for number in self.PHONE_PATTERN.findall(text))

        for paragraph in soup.find_all("p"):
            candidate = paragraph.get_text(" ").strip()
            if not candidate:
                continue
            lowered = candidate.lower()
            if any(hint in lowered for hint in self.ADDRESS_HINTS) and len(candidate) < 160:
                summary.addresses.add(candidate)
            if not summary.description and 40 <= len(candidate) <= 320:
                summary.description = candidate

        if not summary.description and page.title:
            summary.description = page.title

        return summary

    @staticmethod
    def _normalize_phone(number: str) -> str:
        cleaned = re.sub(r"[^\d+]", "", number)
        if cleaned.startswith("61") and len(cleaned) == 11:
            cleaned = "+" + cleaned
        if cleaned.startswith("0") and len(cleaned) == 10:
            cleaned = "+61" + cleaned[1:]
        return cleaned


class BedrockBrowserSession:
    """Lightweight wrapper around the Bedrock Agentcore browser tool."""

    def __init__(self, client, *, agent_id: str, agent_alias_id: str, session_id: Optional[str] = None) -> None:
        self._client = client
        self._agent_id = agent_id
        self._agent_alias_id = agent_alias_id
        self._session_id = session_id or str(uuid.uuid4())

    @property
    def session_id(self) -> str:
        return self._session_id

    async def open_url(self, url: str) -> PageSnapshot:
        logger.info("Opening %s", url)
        payload = {
            "actionGroup": "browser",
            "apiPath": "/open",
            "httpMethod": "POST",
            "requestBody": {"url": url},
        }
        response = await self._invoke_tool(payload)
        html = response.get("body", {}).get("text", "")
        return PageSnapshot.from_html(url, html)

    async def follow_link(self, link: str) -> PageSnapshot:
        logger.info("Following link %s", link)
        payload = {
            "actionGroup": "browser",
            "apiPath": "/navigate",
            "httpMethod": "POST",
            "requestBody": {"link": link},
        }
        response = await self._invoke_tool(payload)
        url = response.get("body", {}).get("url", link)
        html = response.get("body", {}).get("text", "")
        return PageSnapshot.from_html(url, html)

    async def _invoke_tool(self, tool_request: dict) -> dict:
        loop = asyncio.get_running_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.invoke_agent_tool(
                agentId=self._agent_id,
                agentAliasId=self._agent_alias_id,
                sessionId=self._session_id,
                toolName="browser",
                toolInput=tool_request,
            ),
        )
        # The runtime returns a streaming payload; convert it into a dictionary.
        if hasattr(response, "get"):
            body = response.get("toolResponse", {})
            if isinstance(body, dict):
                return body
        return {}


class BusinessSiteTask(Task):
    """`strands-agent` task coordinating the crawl and extraction."""

    def __init__(
        self,
        *,
        browser: BedrockBrowserSession,
        parser: BusinessInfoParser,
        seed_url: str,
        max_pages: int,
        preferred_paths: Optional[Sequence[str]] = None,
    ) -> None:
        super().__init__(name="business-site-crawl")
        self._browser = browser
        self._parser = parser
        self._seed_url = seed_url
        self._max_pages = max_pages
        self._preferred_paths = preferred_paths or ("about", "contact", "team", "services")
        self._visited: Set[str] = set()
        self._queue: list[str] = [seed_url]
        self._summary = BusinessSummary()

    async def run(self, context: TaskContext) -> BusinessSummary:  # type: ignore[override]
        while self._queue and len(self._visited) < self._max_pages:
            url = self._queue.pop(0)
            if url in self._visited:
                continue
            self._visited.add(url)

            if url == self._seed_url:
                page = await self._browser.open_url(url)
            else:
                page = await self._browser.follow_link(url)

            self._summary.merge(self._parser.parse(page))
            self._enqueue_links(page.outgoing_links)

            if self._is_summary_complete():
                break

        return self._summary

    def _enqueue_links(self, links: Iterable[str]) -> None:
        prioritized: list[str] = []
        secondary: list[str] = []
        for link in links:
            lowered = link.lower()
            if any(keyword in lowered for keyword in self._preferred_paths):
                prioritized.append(link)
            else:
                secondary.append(link)
        for candidate in prioritized + secondary:
            if candidate not in self._visited and candidate not in self._queue:
                self._queue.append(candidate)

    def _is_summary_complete(self) -> bool:
        return bool(self._summary.abn and self._summary.emails and self._summary.addresses)


class BusinessCrawlerAgent(Agent):
    """Minimal `strands-agent` wrapper around the crawling task."""

    def __init__(self, memory: Optional[MemoryStore] = None) -> None:
        super().__init__(name="business-crawler", memory=memory)

    async def handle(self, task: BusinessSiteTask, context: TaskContext) -> BusinessSummary:  # type: ignore[override]
        return await task.run(context)


async def run_agent(args: argparse.Namespace) -> None:
    session = boto3.session.Session(profile_name=args.profile if args.profile else None)
    client = session.client(
        "bedrock-agent-runtime",
        region_name=args.region,
        config=Config(retries={"max_attempts": 3, "mode": "standard"}),
    )

    browser = BedrockBrowserSession(
        client,
        agent_id=args.agent_id,
        agent_alias_id=args.agent_alias_id,
    )
    parser = BusinessInfoParser()
    task = BusinessSiteTask(
        browser=browser,
        parser=parser,
        seed_url=args.url,
        max_pages=args.max_pages,
    )

    agent = BusinessCrawlerAgent()
    result = await agent.handle(task, TaskContext())
    print(json.dumps(result.to_dict(), indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bedrock browser agent sample")
    parser.add_argument("--url", required=True, help="Root business website to crawl")
    parser.add_argument("--agent-id", default=os.environ.get("BEDROCK_AGENT_ID"), help="Bedrock agent identifier")
    parser.add_argument(
        "--agent-alias-id",
        default=os.environ.get("BEDROCK_AGENT_ALIAS_ID"),
        help="Bedrock agent alias identifier",
    )
    parser.add_argument(
        "--region",
        default=os.environ.get("AWS_REGION", "us-west-2"),
        help="AWS Region hosting the Bedrock agent",
    )
    parser.add_argument("--profile", default=os.environ.get("AWS_PROFILE"), help="Optional AWS credential profile")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum number of pages to inspect")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if not args.agent_id or not args.agent_alias_id:
        raise SystemExit("Both --agent-id and --agent-alias-id (or corresponding environment variables) are required")
    asyncio.run(run_agent(args))


if __name__ == "__main__":
    main()
