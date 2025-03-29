import treadi.config as tc

import pytest
from unittest.mock import patch


def test_initialize_config(tmp_path):
    tc._initialize_config_dir(tmp_path)

    assert (tmp_path / "TreadI.config.version.txt").exists()
    assert (tmp_path / "TreadI.config.version.txt").is_file()
    assert (tmp_path / "repository_lists.d").exists()
    assert (tmp_path / "repository_lists.d").is_dir()
    assert (tmp_path / "repository_lists.d" / "README.md").exists()
    assert (tmp_path / "repository_lists.d" / "README.md").is_file()
    assert (tmp_path / "repository_lists.d" / "25_Public_repos_I_own.txt").exists()
    assert (tmp_path / "repository_lists.d" / "25_Public_repos_I_own.txt").is_file()

    content = (
        tmp_path / "repository_lists.d" / "25_Public_repos_I_own.txt"
    ).read_text()
    assert "@me" in content


def test_config_repo_list_names(tmp_path):
    tc._initialize_config_dir(tmp_path)
    with patch("treadi.config.config_dir", lambda: tmp_path):
        c = tc.Config()
        assert "Public repos I own" in c.repository_list_names()


def test_config_repo_list(tmp_path):
    tc._initialize_config_dir(tmp_path)
    with patch("treadi.config.config_dir", lambda: tmp_path):
        c = tc.Config()
        repo_list = c.repository_list("Public repos I own")
        assert repo_list.rank == 25
        assert repo_list.display_name == "Public repos I own"
        assert "@me" in repo_list.content
