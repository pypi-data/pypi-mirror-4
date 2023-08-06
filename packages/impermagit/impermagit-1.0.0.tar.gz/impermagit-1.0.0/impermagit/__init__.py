"""
Utilities for creating temporary git repos (for example, in automated
tests of software that integrates with git).
"""

from .repo import Repo, fleeting_repo, GitExeException

__all__ = ["Repo", "fleeting_repo", "GitExeException"]
