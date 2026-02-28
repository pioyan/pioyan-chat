"""Tests for mention parser — extracting @agent-name from messages."""

from app.services.mention_parser import MentionParser


class TestMentionParser:
    """Tests for mention extraction."""

    def test_single_mention_at_start(self):
        result = MentionParser.parse("@coder write a test")
        assert result.mentioned_names == ["coder"]
        assert result.clean_text == "write a test"

    def test_single_mention_inline(self):
        result = MentionParser.parse("hey @reviewer check this")
        assert result.mentioned_names == ["reviewer"]
        assert result.clean_text == "hey check this"

    def test_multiple_mentions(self):
        result = MentionParser.parse("@coder and @reviewer collaborate on this")
        assert result.mentioned_names == ["coder", "reviewer"]
        assert "collaborate on this" in result.clean_text

    def test_no_mentions(self):
        result = MentionParser.parse("just a normal message")
        assert result.mentioned_names == []
        assert result.clean_text == "just a normal message"

    def test_mention_with_hyphen(self):
        result = MentionParser.parse("@feature-builder implement login")
        assert result.mentioned_names == ["feature-builder"]

    def test_mention_with_underscore(self):
        result = MentionParser.parse("@code_reviewer check it")
        assert result.mentioned_names == ["code_reviewer"]

    def test_email_not_treated_as_mention(self):
        result = MentionParser.parse("send to user@example.com")
        assert result.mentioned_names == []

    def test_empty_message(self):
        result = MentionParser.parse("")
        assert result.mentioned_names == []
        assert result.clean_text == ""

    def test_mention_only(self):
        result = MentionParser.parse("@coder")
        assert result.mentioned_names == ["coder"]
        assert result.clean_text == ""

    def test_match_agents_returns_ids(self):
        available_agents = {
            "agent1": "coder",
            "agent2": "reviewer",
            "agent3": "tester",
        }
        result = MentionParser.parse("@coder write a test")
        matched = result.match_agents(available_agents)
        assert matched == ["agent1"]

    def test_match_agents_no_match(self):
        available_agents = {"agent1": "coder"}
        result = MentionParser.parse("@unknown do something")
        matched = result.match_agents(available_agents)
        assert matched == []

    def test_match_agents_multiple(self):
        available_agents = {
            "agent1": "coder",
            "agent2": "reviewer",
        }
        result = MentionParser.parse("@coder @reviewer check and fix")
        matched = result.match_agents(available_agents)
        assert set(matched) == {"agent1", "agent2"}
