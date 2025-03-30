from pathlib import Path

from platformdirs import user_config_dir

from dataclasses import dataclass
from datetime import datetime

import logging
import re


@dataclass(frozen=True)
class RepositoryList:
    path: Path
    display_name: str
    rank: int
    content: str


def config_dir():
    """Return the root path to TreadI's config directory."""
    return Path(user_config_dir("TreadI"))


def create_or_update_config():
    """Create an initialize the config directory if none exists."""
    cdir = config_dir()
    if cdir.exists():
        # TODO Upgrade config if necessary
        return

    # Create config dir
    cdir.mkdir()
    _initialize_config_dir(cdir)


_REPO_LIST_DIR = "repository_lists.d"
_VERSION_FILE = "TreadI.config.version.txt"
# Increment this any time a built-in config changes
# This enables updating the configs
# Format: "vYYYY_MM_DD.12345"
#   The date gives an idea of how recent information is.
#   If for some reason I need to bump the config version twice in
#   one day, the `.number` at the end lets me increment it again.
#   Most config versions should end in `.0`
_CONFIG_VERSION = "v2025-03-29.0"
# Matches file names of repository list files.
_REPO_LIST_REGEX = re.compile("(?P<rank>[0-9][0-9])_(?P<name>[-a-zA-Z0-9._]+).txt")


def _initialize_config_dir(cdir: Path):
    """Initialize the config directory.

    This expects a directory as an argument, and populates the
    directory with default configuration.
    """
    assert cdir.exists()
    assert cdir.is_dir()

    # Make a version file
    (cdir / _VERSION_FILE).write_text(_CONFIG_VERSION)

    # Create a repository lists directory
    external_repos_d = cdir / _REPO_LIST_DIR
    external_repos_d.mkdir()

    # Copy repository lists into the repository lists directory
    internal_repos_d = Path(__file__).parent.resolve() / _REPO_LIST_DIR
    for internal_file in internal_repos_d.iterdir():
        content = internal_file.read_text()
        header = None
        if internal_file.suffix == ".txt":
            header = (
                "#########\n"
                + "# Built-in repository list\n"
                + "# Any edits may be overwritten the next time you upgrade TreadI\n"
                + f"# TreadI Config version: {_CONFIG_VERSION}\n"
                + "#########\n"
            )
        external_file = external_repos_d / internal_file.name
        if header:
            content = "\n".join([header, content])
        external_file.write_text(content)


def _make_repo_list_display_name(raw_name):
    return raw_name.replace("_", " ").strip()


class Config:

    def __init__(self):
        self._logger = logging.getLogger("Config")

    def repository_list_names(self):
        """Return a list of repository list display names."""
        repo_list_d = config_dir() / _REPO_LIST_DIR
        rank_name = []
        for file in repo_list_d.iterdir():
            if file.name == "README.md":
                continue
            match = _REPO_LIST_REGEX.match(file.name)
            if match is None:
                self._logger.warning(f"Invalid repository list file name: {file.name}")
                continue
            rank_name.append(
                (
                    int(match.group("rank")),
                    _make_repo_list_display_name(match.group("name")),
                )
            )

        # Rely on stable sorting to make rank primary key, and display name secondary
        rank_name.sort(key=lambda i: i[1].lower())
        rank_name.sort(key=lambda i: i[0])
        return [i[1] for i in rank_name]

    def repository_list(self, display_name):
        """Given a display name, return the repository list content.

        raise RuntimeError if a repository list is not found.
        """
        repo_list_d = config_dir() / _REPO_LIST_DIR
        for file in repo_list_d.iterdir():
            match = _REPO_LIST_REGEX.match(file.name)
            if match is None:
                self._logger.warning(f"Invalid repository list file name: {file.name}")
                continue
            found_name = _make_repo_list_display_name(match.group("name"))
            if found_name == display_name:
                return RepositoryList(
                    path=file,
                    display_name=display_name,
                    rank=int(match.group("rank")),
                    content=file.read_text(),
                )
        raise RuntimeError("No such repository list: ", display_name)
