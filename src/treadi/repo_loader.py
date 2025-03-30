import abc
import pathlib
import threading
import time
from gql import gql
import requests
import lark
from yaml import safe_load as load_yaml

from .data import Repository


GRAMMAR = (pathlib.Path(__file__).parent.resolve() / "repository_list.lark").read_text()
PARSER = lark.Lark(GRAMMAR, parser="lalr")


class RepoLoaderTransformer(lark.Transformer):

    def __init__(self, *, gql_client):
        # TODO I would rather pass gql_client into begin_loading
        self._gql_client = gql_client

    def start(self, args):
        return SequentialRepoLoaders(repo_loaders=args)

    def directive(self, args):
        return args[0]

    def org_directive(self, args):
        return OrgRepoLoader(organization=args[0], gql_client=self._gql_client)

    def owned_by_directive(self, args):
        if args[0] == "@me":
            return CurrentUserRepoLoader(gql_client=self._gql_client)
        return UserRepoLoader(args[0], gql_client=self._gql_client)

    def vcstool_directive(self, args):
        return VcsRepoLoader(url=args[0])

    def single_repo_directive(self, args):
        return SingleRepoLoader(owner=args[0], name=args[1])


class RepoLoader(abc.ABC):

    def __init__(self):
        self._done_callback = None
        self._repos = None
        self._thread = threading.Thread(target=self._load_repos, daemon=True)

    def begin_loading(self, done_callback):
        self._done_callback = done_callback
        self._thread.start()

    @abc.abstractmethod
    def load_repos(self) -> tuple[Repository]: ...

    def _load_repos(self):
        self._repos = self.load_repos()
        self._done_callback(self._repos)
        self._done_callback = None

    def repos(self) -> tuple[Repository]:
        return self._repos

    def cleanup(self):
        self._thread.join()
        self._thread = None


def parse_repository_list(content: str, *, gql_client) -> RepoLoader:
    """Parse the content of a repository list and return a RepoLoader for it."""
    # TODO use a transformer to turn repo list into a Rz
    tree = PARSER.parse(content)
    return RepoLoaderTransformer(gql_client=gql_client).transform(tree)


class SingleRepoLoader(RepoLoader):

    def __init__(self, owner, name):
        self._repository = Repository(name=name, owner=owner)
        super().__init__()

    def load_repos(self):
        return tuple([self._repository])


class SequentialRepoLoaders(RepoLoader):
    """Invokes multiple repo loaders in a chain."""

    def __init__(self, repo_loaders):
        self.repo_loaders = repo_loaders
        super().__init__()

    def load_repos(self):
        repos = []
        for loader in self.repo_loaders:
            repos.extend(loader.load_repos())
        repos = tuple(set(repos))
        return repos


class CurrentUserRepoLoader(RepoLoader):

    def __init__(self, gql_client):
        self._client = gql_client
        super().__init__()

    def load_repos(self):
        repos = []

        def _query(after=""):
            query = gql(
                """
                query($after: String!) {
                    viewer {
                        repositories(after: $after, first: 100, visibility: PUBLIC, affiliations: [OWNER], isArchived: false) {
                            nodes {
                                nameWithOwner
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                        }
                    }
                }
                """
            )
            result = self._client.execute(query, variable_values={"after": after})
            return result

        q = None
        while q is None or q["viewer"]["repositories"]["pageInfo"]["hasNextPage"]:
            if q is None:
                q = _query("")
            else:
                q = _query(q["viewer"]["repositories"]["pageInfo"]["endCursor"])
            for r in q["viewer"]["repositories"]["nodes"]:
                owner, name = r["nameWithOwner"].split("/")
                repos.append(Repository(name=name, owner=owner))
        return tuple(repos)


class UserRepoLoader(RepoLoader):

    def __init__(self, username, gql_client):
        self._username = username
        self._client = gql_client
        super().__init__()

    def load_repos(self):
        repos = []

        def _query(after=""):
            query = gql(
                """
                query($username: String!, $after: String!) {
                    user(login: $username) {
                        repositories(after: $after, first: 100, visibility: PUBLIC, affiliations: [OWNER], isArchived: false) {
                            nodes {
                                nameWithOwner
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                        }
                    }
                }
                """
            )
            result = self._client.execute(
                query, variable_values={"username": self._username, "after": after}
            )
            return result

        q = None
        while q is None or q["user"]["repositories"]["pageInfo"]["hasNextPage"]:
            if q is None:
                q = _query("")
            else:
                q = _query(q["user"]["repositories"]["pageInfo"]["endCursor"])
            for r in q["user"]["repositories"]["nodes"]:
                owner, name = r["nameWithOwner"].split("/")
                repos.append(Repository(name=name, owner=owner))
        return tuple(repos)


class OrgRepoLoader(RepoLoader):

    def __init__(
        self,
        organization,
        gql_client,
    ):
        self._client = gql_client
        self.organization = organization
        super().__init__()

    def load_repos(self):
        repos = []

        def _query(after=""):
            query = gql(
                """
                query($after: String!, $organization: String!) {
                    organization(login: $organization) {
                        repositories(after: $after, first: 100, visibility: PUBLIC, isArchived: false) {
                            nodes {
                                nameWithOwner
                            }
                            pageInfo {
                                endCursor
                                hasNextPage
                            }
                        }
                    }
                }
                """
            )
            result = self._client.execute(
                query,
                variable_values={"after": after, "organization": self.organization},
            )
            return result

        q = None
        while q is None or q["organization"]["repositories"]["pageInfo"]["hasNextPage"]:
            if q is None:
                q = _query("")
            else:
                q = _query(q["organization"]["repositories"]["pageInfo"]["endCursor"])
            for r in q["organization"]["repositories"]["nodes"]:
                owner, name = r["nameWithOwner"].split("/")
                repos.append(Repository(name=name, owner=owner))
        return tuple(repos)


class VcsRepoLoader(RepoLoader):

    def __init__(self, url):
        self.url = url
        super().__init__()

    def load_repos(self):
        repos = []

        r = requests.get(self.url)
        if r.status_code != 200:
            raise RuntimeError(f"TODO Handle VCS Repose download failure {r}")

        repos_file = load_yaml(r.text)
        if "repositories" not in repos_file:
            raise RuntimeError(f"TODO handle invalid repos file {repos_file}")

        for repo_data in repos_file["repositories"].values():
            if "url" not in repo_data:
                raise RuntimeError(f"TODO handle invalid repos file {repos_file}")
            url = repo_data["url"]
            if not url.startswith("https://github.com/"):
                continue
            url = url[len("https://github.com/") :]
            if url.endswith(".git"):
                url = url[: -len(".git")]
            if url.count("/") != 1:
                raise RuntimeError("Unable to parse url: {repo_data['url']}")
            owner, name = url.split("/")
            repos.append(Repository(name=name, owner=owner))

        return tuple(repos)
