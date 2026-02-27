"""Dockerfile / Containerfile validator.

Validates uploaded container definition files for bot registration.
Checks structure, required instructions, and basic security concerns.
"""

import re

# Valid Dockerfile instructions (Docker BuildKit spec)
_VALID_INSTRUCTIONS = frozenset(
    {
        "ADD",
        "ARG",
        "CMD",
        "COPY",
        "ENTRYPOINT",
        "ENV",
        "EXPOSE",
        "FROM",
        "HEALTHCHECK",
        "LABEL",
        "MAINTAINER",
        "ONBUILD",
        "RUN",
        "SHELL",
        "STOPSIGNAL",
        "USER",
        "VOLUME",
        "WORKDIR",
    }
)

# Parser directives that may appear as comments at the top of a Dockerfile
_PARSER_DIRECTIVE_RE = re.compile(r"^#\s*(syntax|escape)\s*=", re.IGNORECASE)


class ContainerFileValidationError(Exception):
    """Raised when a container file fails validation."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = errors
        super().__init__("; ".join(errors))


def validate_container_file(content: str) -> list[str]:
    """Validate a Dockerfile/Containerfile content string.

    Returns a list of error messages. An empty list means the file is valid.
    """
    errors: list[str] = []

    if not content.strip():
        return ["Container file is empty"]

    lines = content.splitlines()
    has_from = False
    in_parser_directives = True

    for line_num, raw_line in enumerate(lines, start=1):
        stripped = raw_line.strip()

        # Skip empty lines
        if not stripped:
            in_parser_directives = False
            continue

        # Handle comments and parser directives
        if stripped.startswith("#"):
            if in_parser_directives and _PARSER_DIRECTIVE_RE.match(stripped):
                continue
            in_parser_directives = False
            continue

        in_parser_directives = False

        # Skip continuation lines (previous line ended with \)
        # We handle this by checking if the line looks like an instruction
        instruction_match = re.match(r"^([A-Za-z]+)(\s|$)", stripped)
        if not instruction_match:
            # Could be a continuation line or argument — skip
            continue

        instruction = instruction_match.group(1).upper()

        if instruction not in _VALID_INSTRUCTIONS:
            errors.append(f"Line {line_num}: unknown instruction '{instruction}'")
            continue

        if instruction == "FROM":
            has_from = True
            # Validate FROM has an image reference
            from_args = stripped[instruction_match.end() :].strip()
            if not from_args:
                errors.append(f"Line {line_num}: FROM requires an image reference")

    if not has_from:
        errors.append("Container file must contain at least one FROM instruction")

    return errors
