"""GitHub integration service — agent discovery and repository operations."""

import re
from urllib.parse import quote

import httpx

_GITHUB_URL_RE = re.compile(r"^https://github\.com/([\w.\-]+)/([\w.\-]+?)(?:\.git)?/?$")


class GitHubService:
    """Thin wrapper around GitHub REST API for agent-related operations."""

    API_BASE = "https://api.github.com"

    def __init__(self, token: str) -> None:
        self._token = token
        self._headers = {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }

    # ── Public helpers ────────────────────────────────────────

    @staticmethod
    def parse_repo_url(url: str) -> tuple[str, str]:
        """Extract (owner, repo_name) from a GitHub URL.

        Raises ValueError if the URL is not a valid GitHub repo URL.
        """
        m = _GITHUB_URL_RE.match(url)
        if not m:
            raise ValueError(f"Invalid GitHub repository URL: {url}")
        return m.group(1), m.group(2)

    # ── Agent discovery ───────────────────────────────────────

    async def discover_agents(self, owner: str, repo: str) -> list[dict[str, str]]:
        """Discover agent definition files in .github/agents/ of a repo.

        Returns a list of dicts: [{"name": ..., "path": ..., "content": ...}]
        """
        files = await self._list_directory(owner, repo, ".github/agents")
        if not files:
            return []

        agents: list[dict[str, str]] = []
        for f in files:
            name = f["name"]
            path = f["path"]
            # Only process .md files (skip README.md)
            if not name.endswith(".md") or name.upper() == "README.MD":
                continue
            content = await self._get_file_content(owner, repo, path)
            agent_name = name.removesuffix(".md")
            agents.append({"name": agent_name, "path": path, "content": content})

        return agents

    async def get_agent_definition(self, owner: str, repo: str, path: str) -> str:
        """Get the content of a single agent definition file."""
        return await self._get_file_content(owner, repo, path)

    # ── Low-level GitHub API calls ────────────────────────────

    async def _list_directory(self, owner: str, repo: str, path: str) -> list[dict] | None:
        """List files in a directory via GitHub Contents API.

        Returns None if the directory does not exist (404).
        """
        url = f"{self.API_BASE}/repos/{quote(owner)}/{quote(repo)}/contents/{quote(path, safe='/')}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    async def _get_file_content(self, owner: str, repo: str, path: str) -> str:
        """Get the decoded text content of a file via GitHub Contents API."""
        url = f"{self.API_BASE}/repos/{quote(owner)}/{quote(repo)}/contents/{quote(path, safe='/')}"
        headers = {**self._headers, "Accept": "application/vnd.github.v3.raw"}
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.text

    async def create_branch(self, owner: str, repo: str, branch_name: str, base_sha: str) -> dict:
        """Create a new branch (git ref) in the repo."""
        url = f"{self.API_BASE}/repos/{quote(owner)}/{quote(repo)}/git/refs"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self._headers,
                json={"ref": f"refs/heads/{branch_name}", "sha": base_sha},
            )
        resp.raise_for_status()
        return resp.json()

    async def create_pull_request(
        self,
        owner: str,
        repo: str,
        title: str,
        body: str,
        head: str,
        base: str,
    ) -> dict:
        """Create a pull request."""
        url = f"{self.API_BASE}/repos/{quote(owner)}/{quote(repo)}/pulls"
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                url,
                headers=self._headers,
                json={"title": title, "body": body, "head": head, "base": base},
            )
        resp.raise_for_status()
        return resp.json()

    async def get_default_branch_sha(self, owner: str, repo: str) -> str:
        """Get the SHA of the default branch's HEAD."""
        url = f"{self.API_BASE}/repos/{quote(owner)}/{quote(repo)}"
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, headers=self._headers)
        resp.raise_for_status()
        data = resp.json()
        default_branch = data["default_branch"]

        ref_url = (
            f"{self.API_BASE}/repos/{quote(owner)}/{quote(repo)}/git/ref/heads/{default_branch}"
        )
        async with httpx.AsyncClient() as client:
            resp = await client.get(ref_url, headers=self._headers)
        resp.raise_for_status()
        return resp.json()["object"]["sha"]
