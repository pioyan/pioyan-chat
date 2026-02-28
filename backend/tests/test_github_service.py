"""Tests for GitHub service — agent discovery and repo operations."""

from unittest.mock import AsyncMock, patch

import pytest

from app.services.github_service import GitHubService


class TestParseRepoUrl:
    """Tests for parse_repo_url utility."""

    def test_valid_url(self):
        owner, name = GitHubService.parse_repo_url("https://github.com/owner/repo")
        assert owner == "owner"
        assert name == "repo"

    def test_valid_url_with_trailing_slash(self):
        owner, name = GitHubService.parse_repo_url("https://github.com/owner/repo/")
        assert owner == "owner"
        assert name == "repo"

    def test_valid_url_with_dotgit(self):
        owner, name = GitHubService.parse_repo_url("https://github.com/owner/repo.git")
        assert owner == "owner"
        assert name == "repo"

    def test_invalid_url_raises(self):
        with pytest.raises(ValueError, match="Invalid GitHub"):
            GitHubService.parse_repo_url("https://gitlab.com/owner/repo")

    def test_no_repo_name_raises(self):
        with pytest.raises(ValueError, match="Invalid GitHub"):
            GitHubService.parse_repo_url("https://github.com/owner")


class TestDiscoverAgents:
    """Tests for discover_agents — reads .github/agents/ from a repo."""

    async def test_discover_agents_success(self):
        mock_files = [
            {"name": "feature-builder.md", "path": ".github/agents/feature-builder.md"},
            {"name": "code-reviewer.md", "path": ".github/agents/code-reviewer.md"},
            {"name": "README.md", "path": ".github/agents/README.md"},
        ]
        mock_contents = {
            ".github/agents/feature-builder.md": "# Feature Builder\nYou build features.",
            ".github/agents/code-reviewer.md": "# Code Reviewer\nYou review code.",
        }

        service = GitHubService(token="test-token")

        with (
            patch.object(
                service, "_list_directory", new_callable=AsyncMock, return_value=mock_files
            ),
            patch.object(
                service,
                "_get_file_content",
                new_callable=AsyncMock,
                side_effect=lambda owner, repo, path: mock_contents.get(path, ""),
            ),
        ):
            agents = await service.discover_agents("owner", "repo")

        assert len(agents) == 2
        assert agents[0]["name"] == "feature-builder"
        assert agents[0]["path"] == ".github/agents/feature-builder.md"
        assert "You build features." in agents[0]["content"]
        assert agents[1]["name"] == "code-reviewer"

    async def test_discover_agents_no_agents_dir(self):
        service = GitHubService(token="test-token")

        with patch.object(service, "_list_directory", new_callable=AsyncMock, return_value=None):
            agents = await service.discover_agents("owner", "repo")

        assert agents == []

    async def test_discover_agents_filters_non_md(self):
        mock_files = [
            {"name": "agent.md", "path": ".github/agents/agent.md"},
            {"name": "config.yml", "path": ".github/agents/config.yml"},
        ]

        service = GitHubService(token="test-token")

        with (
            patch.object(
                service, "_list_directory", new_callable=AsyncMock, return_value=mock_files
            ),
            patch.object(
                service,
                "_get_file_content",
                new_callable=AsyncMock,
                return_value="# Agent\nSystem prompt.",
            ),
        ):
            agents = await service.discover_agents("owner", "repo")

        assert len(agents) == 1
        assert agents[0]["name"] == "agent"


class TestGetAgentDefinition:
    """Tests for get_agent_definition."""

    async def test_get_definition(self):
        service = GitHubService(token="test-token")

        with patch.object(
            service,
            "_get_file_content",
            new_callable=AsyncMock,
            return_value="# My Agent\nYou are a helpful agent.",
        ):
            content = await service.get_agent_definition(
                "owner", "repo", ".github/agents/my-agent.md"
            )

        assert content == "# My Agent\nYou are a helpful agent."
