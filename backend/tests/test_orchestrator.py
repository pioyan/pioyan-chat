"""Tests for Orchestrator service — routing instructions to agents."""

import pytest

from app.services.orchestrator import Orchestrator


class TestOrchestratorRouting:
    """Tests for Orchestrator.route_instruction()."""

    @pytest.fixture
    def agents(self) -> dict[str, str]:
        """Sample agent mapping: {agent_id: agent_name}."""
        return {
            "aaaa00000000000000000001": "code-bot",
            "aaaa00000000000000000002": "test-bot",
            "aaaa00000000000000000003": "docs-bot",
        }

    async def test_mention_routes_to_specific_agent(self, agents):
        result = await Orchestrator.route_instruction("@code-bot fix the login bug", agents)
        assert result["target_agent_ids"] == ["aaaa00000000000000000001"]
        assert result["instruction"] == "fix the login bug"
        assert result["is_orchestrated"] is False

    async def test_mention_routes_multiple_agents(self, agents):
        result = await Orchestrator.route_instruction(
            "@code-bot @test-bot implement and test login", agents
        )
        assert set(result["target_agent_ids"]) == {
            "aaaa00000000000000000001",
            "aaaa00000000000000000002",
        }
        assert result["is_orchestrated"] is False

    async def test_no_mention_delegates_to_first_agent(self, agents):
        result = await Orchestrator.route_instruction("Refactor the database layer", agents)
        assert len(result["target_agent_ids"]) == 1
        assert result["target_agent_ids"][0] == "aaaa00000000000000000001"
        assert result["is_orchestrated"] is True

    async def test_no_agents_available_returns_empty(self):
        result = await Orchestrator.route_instruction("Help me code", {})
        assert result["target_agent_ids"] == []
        assert result["is_orchestrated"] is True

    async def test_unrecognized_mention_falls_back(self, agents):
        """@unknown-bot not in agents → orchestrator fallback."""
        result = await Orchestrator.route_instruction("@unknown-bot do something", agents)
        # Falls back to orchestrator since the mention doesn't match
        assert result["is_orchestrated"] is True
        assert len(result["target_agent_ids"]) == 1

    async def test_clean_text_preserves_instruction(self, agents):
        result = await Orchestrator.route_instruction("@code-bot please fix  the  spacing", agents)
        assert result["instruction"] == "please fix the spacing"

    async def test_empty_message(self, agents):
        result = await Orchestrator.route_instruction("", agents)
        assert result["is_orchestrated"] is True
        assert result["instruction"] == ""
