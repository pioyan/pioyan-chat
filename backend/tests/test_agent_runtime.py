"""Tests for agent runtime components — CopilotClient and GitOps."""

from unittest.mock import MagicMock, patch


class TestCopilotClient:
    """Tests for the CopilotClient wrapper."""

    async def test_stub_mode_when_sdk_not_installed(self):
        """When copilot-sdk is not installed, should work in stub mode."""
        import sys

        # Temporarily ensure copilot_sdk is not importable
        original = sys.modules.get("copilot_sdk")
        sys.modules["copilot_sdk"] = None

        try:
            # Need to reload the module to pick up the mocked import
            if "agent_runtime.copilot_client" in sys.modules:
                del sys.modules["agent_runtime.copilot_client"]
            from agent_runtime.copilot_client import CopilotClient

            client = CopilotClient(system_prompt="Test prompt")
            await client.initialize()

            result = await client.execute_instruction("Write a hello world")

            assert "stub" in result["summary"].lower()
            assert "Write a hello world" in result["response"]
        finally:
            if original is not None:
                sys.modules["copilot_sdk"] = original
            elif "copilot_sdk" in sys.modules:
                del sys.modules["copilot_sdk"]

    def test_build_system_prompt_without_context(self):
        from agent_runtime.copilot_client import CopilotClient

        client = CopilotClient(system_prompt="You are a coder.")
        prompt = client._build_system_prompt()
        assert "You are a coder." in prompt

    def test_build_system_prompt_with_context(self):
        from agent_runtime.copilot_client import CopilotClient

        client = CopilotClient(system_prompt="You are a coder.")
        prompt = client._build_system_prompt(
            context={
                "repo_info": "https://github.com/owner/repo",
                "file_list": ["main.py", "test.py"],
            }
        )
        assert "owner/repo" in prompt
        assert "main.py" in prompt

    def test_extract_summary(self):
        from agent_runtime.copilot_client import CopilotClient

        summary = CopilotClient._extract_summary(
            {"content": "I added a login button.\n\nDetails follow..."}
        )
        assert summary == "I added a login button."


class TestGitOps:
    """Tests for GitOps (subprocess mocked)."""

    def test_clone_with_token(self):
        from agent_runtime.git_ops import GitOps

        ops = GitOps(repo_dir="/tmp/test-repo")

        with patch.object(ops, "_run") as mock_run:
            ops.clone(
                "https://github.com/owner/repo",
                branch="main",
                token="ghp_test123",
            )

            # Should substitute token into URL
            clone_cmd = mock_run.call_args_list[0][0][0]
            # git clone --branch main --depth 50 <url> <dir>
            url_arg = [a for a in clone_cmd if "github.com" in a][0]
            assert "x-access-token:ghp_test123@" in url_arg

    def test_clone_without_token(self):
        from agent_runtime.git_ops import GitOps

        ops = GitOps(repo_dir="/tmp/test-repo")

        with patch.object(ops, "_run") as mock_run:
            ops.clone("https://github.com/owner/repo", branch="main")

            clone_cmd = mock_run.call_args_list[0][0][0]
            url_arg = [a for a in clone_cmd if "github.com" in a][0]
            assert "x-access-token" not in url_arg

    def test_create_branch(self):
        from agent_runtime.git_ops import GitOps

        ops = GitOps(repo_dir="/tmp/test-repo")

        with patch.object(ops, "_run") as mock_run:
            ops.create_branch("feat/new-feature")

            mock_run.assert_called_once()
            call_args = mock_run.call_args[0][0]
            assert "checkout" in call_args
            assert "-b" in call_args
            assert "feat/new-feature" in call_args

    def test_commit_all_with_changes(self):
        from agent_runtime.git_ops import GitOps

        ops = GitOps(repo_dir="/tmp/test-repo")

        with (
            patch.object(ops, "_run", return_value="abc123\n") as mock_run,
            patch("subprocess.run") as mock_subprocess,
        ):
            # Simulate there are staged changes (exit code 1 = there are diffs)
            mock_subprocess.return_value = MagicMock(returncode=1)

            sha = ops.commit_all("test commit")

            assert sha == "abc123"

    def test_commit_all_no_changes(self):
        from agent_runtime.git_ops import GitOps

        ops = GitOps(repo_dir="/tmp/test-repo")

        with (
            patch.object(ops, "_run") as mock_run,
            patch("subprocess.run") as mock_subprocess,
        ):
            # Simulate no staged changes (exit code 0 = no diffs)
            mock_subprocess.return_value = MagicMock(returncode=0)

            sha = ops.commit_all("test commit")

            assert sha is None

    def test_push(self):
        from agent_runtime.git_ops import GitOps

        ops = GitOps(repo_dir="/tmp/test-repo")

        with patch.object(ops, "_run") as mock_run:
            ops.push("feat/test")

            call_args = mock_run.call_args[0][0]
            assert "push" in call_args
            assert "feat/test" in call_args
