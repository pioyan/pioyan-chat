"""Unit tests for Dockerfile / Containerfile validator."""

from app.bots.validator import validate_container_file


class TestValidateContainerFile:
    def test_valid_simple_dockerfile(self):
        content = 'FROM python:3.13-slim\nRUN pip install flask\nCMD ["python", "app.py"]\n'
        errors = validate_container_file(content)
        assert errors == []

    def test_valid_multistage_dockerfile(self):
        content = (
            "FROM node:22 AS build\n"
            "RUN npm ci\n"
            "FROM node:22-slim\n"
            "COPY --from=build /app /app\n"
            'CMD ["node", "index.js"]\n'
        )
        errors = validate_container_file(content)
        assert errors == []

    def test_empty_file(self):
        errors = validate_container_file("")
        assert len(errors) == 1
        assert "empty" in errors[0].lower()

    def test_whitespace_only(self):
        errors = validate_container_file("   \n  \n  ")
        assert len(errors) == 1
        assert "empty" in errors[0].lower()

    def test_missing_from(self):
        errors = validate_container_file('RUN echo hello\nCMD ["bash"]\n')
        assert any("FROM" in e for e in errors)

    def test_unknown_instruction(self):
        errors = validate_container_file("FROM ubuntu\nINVALID foo\n")
        assert any("INVALID" in e for e in errors)

    def test_from_without_image(self):
        errors = validate_container_file("FROM \n")
        assert any("image reference" in e.lower() for e in errors)

    def test_comments_are_allowed(self):
        content = "# This is a comment\nFROM python:3.13\n# Another comment\nRUN echo hi\n"
        errors = validate_container_file(content)
        assert errors == []

    def test_parser_directive(self):
        content = "# syntax=docker/dockerfile:1\nFROM python:3.13\n"
        errors = validate_container_file(content)
        assert errors == []

    def test_all_valid_instructions(self):
        content = (
            "FROM ubuntu:22.04\n"
            "ARG DEBIAN_FRONTEND=noninteractive\n"
            "ENV APP_HOME=/app\n"
            "WORKDIR /app\n"
            "COPY . .\n"
            "ADD extra.tar.gz /opt/\n"
            "RUN apt-get update\n"
            "EXPOSE 8080\n"
            "VOLUME /data\n"
            "USER app\n"
            "LABEL version=1.0\n"
            "HEALTHCHECK CMD curl -f http://localhost/\n"
            "STOPSIGNAL SIGTERM\n"
            'SHELL ["/bin/bash", "-c"]\n'
            'ENTRYPOINT ["python"]\n'
            'CMD ["app.py"]\n'
        )
        errors = validate_container_file(content)
        assert errors == []

    def test_case_insensitive_instructions(self):
        content = 'from python:3.13\nrun echo hello\ncmd ["python"]\n'
        # Lowercase instructions are not standard but we match case-insensitively
        # Actually our regex matches [A-Za-z]+ so it should work
        errors = validate_container_file(content)
        assert errors == []
