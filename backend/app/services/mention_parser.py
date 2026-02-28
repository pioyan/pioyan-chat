"""Mention parser — extract @agent-name references from message text."""

import re
from dataclasses import dataclass, field

# Match @name at word boundary, but NOT email-like patterns (word@word)
# Requires @ at start of string or preceded by whitespace
_MENTION_RE = re.compile(r"(?:^|(?<=\s))@([\w][\w\-]*)")


@dataclass
class MentionResult:
    """Result of parsing mentions from a message."""

    mentioned_names: list[str] = field(default_factory=list)
    clean_text: str = ""

    def match_agents(self, available_agents: dict[str, str]) -> list[str]:
        """Match mentioned names against available agents.

        Args:
            available_agents: {agent_id: agent_name} mapping.

        Returns:
            List of matched agent IDs.
        """
        name_to_id = {name: aid for aid, name in available_agents.items()}
        return [name_to_id[name] for name in self.mentioned_names if name in name_to_id]


class MentionParser:
    """Utility for extracting @mentions from chat messages."""

    @staticmethod
    def parse(text: str) -> MentionResult:
        """Parse a message and extract @mentions.

        Returns MentionResult with:
          - mentioned_names: list of agent names (without @)
          - clean_text: message with mentions removed
        """
        if not text:
            return MentionResult(mentioned_names=[], clean_text="")

        mentions = _MENTION_RE.findall(text)
        clean = _MENTION_RE.sub("", text).strip()
        # Collapse multiple spaces
        clean = re.sub(r"\s+", " ", clean).strip()

        return MentionResult(
            mentioned_names=mentions,
            clean_text=clean,
        )
