import threading

from treadi.data import Repository
from treadi.repo_loader import parse_repository_list


def test_parse_all_directives():
    content = """
    owned-by:@me
    org:ros2
    vcstool:https://foobar.com/some.repos
    my-org/MyRepo
    """
    repo_loader = parse_repository_list(content, gql_client="fake")
    assert len(repo_loader.repo_loaders) == 4


def test_single_repo_directives():
    content = """
    sloretz/baz.foo
    my-org/MyRepo
    cool/story_bro
    """
    repo_loader = parse_repository_list(content, gql_client="fake")
    e = threading.Event()
    repo_loader.begin_loading(lambda _: e.set())
    e.wait()

    assert Repository(owner="sloretz", name="baz.foo") in repo_loader.repos()
    assert Repository(owner="my-org", name="MyRepo") in repo_loader.repos()
    assert Repository(owner="cool", name="story_bro") in repo_loader.repos()
