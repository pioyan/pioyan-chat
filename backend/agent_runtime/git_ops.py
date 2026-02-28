"""Git operations for the agent runtime — clone, branch, commit, push, PR."""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)


class GitOpsError(Exception):
    """Structured error for git operations."""

    def __init__(self, operation: str, message: str, returncode: int | None = None) -> None:
        self.operation = operation
        self.returncode = returncode
        super().__init__(f"git {operation} failed: {message}")


class GitOps:
    """Git operations executed inside the agent container."""

    def __init__(self, repo_dir: str = "/workspace/repo") -> None:
        self.repo_dir = Path(repo_dir)

    def clone(self, repo_url: str, branch: str = "main", token: str | None = None) -> None:
        """Clone a repository into the workspace.

        Raises:
            GitOpsError: If clone fails (network, auth, or invalid repo).
        """
        if token:
            # Insert token into HTTPS URL for auth
            url = repo_url.replace("https://", f"https://x-access-token:{token}@")
        else:
            url = repo_url

        self.repo_dir.mkdir(parents=True, exist_ok=True)
        try:
            self._run(["git", "clone", "--branch", branch, "--depth", "50", url, str(self.repo_dir)])
        except subprocess.CalledProcessError as exc:
            # Sanitize token from error message
            err_msg = (exc.stderr or "").replace(token or "", "***")
            raise GitOpsError("clone", err_msg, exc.returncode) from exc
        self._run(["git", "config", "user.name", "pioyan-bot"], cwd=self.repo_dir)
        self._run(["git", "config", "user.email", "bot@pioyan-chat.local"], cwd=self.repo_dir)

    def create_branch(self, branch_name: str) -> None:
        """Create and checkout a new branch."""
        self._run(["git", "checkout", "-b", branch_name], cwd=self.repo_dir)

    def commit_all(self, message: str) -> str | None:
        """Stage all changes and commit. Returns commit SHA or None if nothing to commit."""
        self._run(["git", "add", "-A"], cwd=self.repo_dir)

        # Check if there are changes to commit
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            cwd=self.repo_dir,
            capture_output=True,
        )
        if result.returncode == 0:
            return None  # Nothing to commit

        self._run(["git", "commit", "-m", message], cwd=self.repo_dir)
        sha = self._run(["git", "rev-parse", "HEAD"], cwd=self.repo_dir, capture=True).strip()
        return sha

    def push(self, branch_name: str) -> None:
        """Push a branch to origin.

        Raises:
            GitOpsError: If push fails (auth, network, or remote rejection).
        """
        try:
            self._run(["git", "push", "-u", "origin", branch_name], cwd=self.repo_dir)
        except subprocess.CalledProcessError as exc:
            raise GitOpsError("push", exc.stderr or str(exc), exc.returncode) from exc

    def create_pr(
        self,
        title: str,
        body: str,
        base: str = "main",
    ) -> str | None:
        """Create a pull request using GitHub CLI. Returns PR URL or None.

        Raises:
            GitOpsError: If PR creation fails (auth or API error).
        """
        try:
            output = self._run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--title",
                    title,
                    "--body",
                    body,
                    "--base",
                    base,
                    "--head",
                    self._current_branch(),
                ],
                cwd=self.repo_dir,
                capture=True,
            )
            return output.strip()
        except subprocess.CalledProcessError as exc:
            err_msg = exc.stderr or str(exc)
            logger.error("Failed to create PR: %s", err_msg)
            raise GitOpsError("create_pr", err_msg, exc.returncode) from exc

    def get_diff_summary(self) -> str:
        """Get a short summary of uncommitted changes."""
        output = self._run(["git", "diff", "--stat"], cwd=self.repo_dir, capture=True)
        return output.strip()

    def _current_branch(self) -> str:
        """Return the name of the current branch."""
        return self._run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=self.repo_dir,
            capture=True,
        ).strip()

    def _run(
        self,
        cmd: list[str],
        cwd: Path | None = None,
        capture: bool = False,
    ) -> str:
        """Run a subprocess command."""
        logger.debug("Running: %s", " ".join(cmd))
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
            timeout=120,
        )
        if capture:
            return result.stdout
        return ""
