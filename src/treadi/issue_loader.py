from concurrent.futures import ThreadPoolExecutor

import threading
import time
import logging
from gql import gql
from dateutil.parser import isoparse

from .data import Issue
from .data import Repository


def _make_issue(repo, gh_data):
    if gh_data["author"] is None:
        # https://github.com/ghost
        author = "ghost"
    else:
        author = gh_data["author"]["login"]
    return Issue(
        repo=repo,
        author=author,
        created_at=isoparse(gh_data["createdAt"]),
        updated_at=isoparse(gh_data["updatedAt"]),
        number=int(gh_data["number"]),
        title=gh_data["title"],
        url=gh_data["url"],
        is_read=bool(gh_data["isReadByViewer"]),
    )


FRAGMENT_ISSUE = """
fragment issueFields on Issue {
    author {
        login
    }
    createdAt
    number
    title
    updatedAt
    url
    isReadByViewer
}
"""
FRAGMENT_PR = """
fragment prFields on PullRequest {
    author {
        login
    }
    createdAt
    number
    title
    updatedAt
    url
    isReadByViewer
}
"""

INITIAL_ISSUE_QUERY = """
issues(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}, states: [OPEN]) {
    nodes {
        ...issueFields
    }
    pageInfo {
        endCursor
        hasNextPage
    }
}
"""
SUBSEQUENT_ISSUE_QUERY = """
issues(first: 100, after: "%s" orderBy: {field: UPDATED_AT, direction: DESC}, states: [OPEN]) {
    nodes {
        ...issueFields
    }
    pageInfo {
        endCursor
        hasNextPage
    }
}
"""
INITIAL_PR_QUERY = """
pullRequests(first: 100, orderBy: {field: UPDATED_AT, direction: DESC}, states: [OPEN]) {
        nodes {
            ...prFields
        }
        pageInfo {
            endCursor
            hasNextPage
        }
    }
"""
SUBSEQUENT_PR_QUERY = """
pullRequests(first: 100, after: "%s" orderBy: {field: UPDATED_AT, direction: DESC}, states: [OPEN]) {
        nodes {
            ...prFields
        }
        pageInfo {
            endCursor
            hasNextPage
        }
    }
"""


class IssueLoader:

    def __init__(self, gql_client, repos, cache, progress_callback):
        self._client = gql_client
        self._repos = repos
        self._cache = cache
        self._lock = threading.Lock()
        self._logger = logging.getLogger("IssueLoader")
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._submit(self._load_all_issues, repos, progress_callback)

    def _submit(self, *args):
        f = self._executor.submit(*args)
        f.add_done_callback(self._log_exception)

    def _log_exception(self, future):
        try:
            future.result()
        except:
            self._logger.exception("Exception in IssueLoader background thread")

    def _load_all_issues(self, repos, progress_callback=None):
        num_repos_at_start = len(repos)
        # Make a copy to not modify caller
        repos = list(repos)

        REPOS_PER_QUERY = 10

        # These dicts indicate if repos have more issues or PRs to query
        issue_page_info = {}
        pr_page_info = {}
        for r in repos:
            # Use "None" to mean we haven't queried anything yet
            issue_page_info[r] = None
            pr_page_info[r] = None

        # Outer loop runs until it finishes exploring all issues and PRs
        # on all repos
        next_queries = []
        issue_count = 0
        pr_count = 0
        while issue_page_info or pr_page_info:
            # This loop looks for repos that still need to be explored
            for r in repos:
                issue_query = None
                pr_query = None
                if r in issue_page_info:
                    ipi = issue_page_info[r]
                    if ipi is None:
                        # Initial query has no page info
                        issue_query = INITIAL_ISSUE_QUERY
                    elif ipi["hasNextPage"]:
                        # Continuing query starts from previous page
                        issue_query = SUBSEQUENT_ISSUE_QUERY % ipi["endCursor"]
                if r in pr_page_info:
                    prpi = pr_page_info[r]
                    if prpi is None:
                        # Initial query has no page info
                        pr_query = INITIAL_PR_QUERY
                    elif prpi["hasNextPage"]:
                        # Continuqing query starts from previous page
                        pr_query = SUBSEQUENT_PR_QUERY % prpi["endCursor"]

                if issue_query or pr_query:
                    repo_query = (
                        f'r{id(r)}: repository(owner: "{r.owner}", name: "{r.name}")'
                    )
                    repo_query += "{"
                    if issue_query:
                        repo_query += issue_query
                    if pr_query:
                        repo_query += pr_query
                    repo_query += "}"
                    next_queries.append(repo_query)

                if len(next_queries) == REPOS_PER_QUERY or r == repos[-1]:
                    # Found enough repos, ditch the for loop
                    break

            # Execute the next query
            joined_queries = "\n".join(next_queries)
            query_str = f"""
                query {{
                    {joined_queries}
                }}
                """
            next_queries = []
            # It's an error to include unused fragments,
            # so only include a fragment if it's used.
            if issue_page_info:
                query_str += FRAGMENT_ISSUE
            if pr_page_info:
                query_str += FRAGMENT_PR
            query = gql(query_str)
            result = self._client.execute(query)

            # Figure out what repos the query included,
            # and add the issues and PRs to the upcomming list
            for r in repos:
                key = f"r{id(r)}"
                if key not in result:
                    # Query didn't include this repo
                    continue
                repo_result = result[key]
                if "issues" in repo_result:
                    for issue in repo_result["issues"]["nodes"]:
                        self._cache.insert(_make_issue(r, issue))
                        issue_count += 1
                    if repo_result["issues"]["pageInfo"]["hasNextPage"]:
                        issue_page_info[r] = repo_result["issues"]["pageInfo"]
                    else:
                        del issue_page_info[r]
                if "pullRequests" in repo_result:
                    for pr in repo_result["pullRequests"]["nodes"]:
                        self._cache.insert(_make_issue(r, pr))
                        pr_count += 1
                    if repo_result["pullRequests"]["pageInfo"]["hasNextPage"]:
                        pr_page_info[r] = repo_result["pullRequests"]["pageInfo"]
                    else:
                        del pr_page_info[r]
            if progress_callback:
                i_max = pr_max = num_repos_at_start
                progress_callback(
                    (i_max - len(issue_page_info) + pr_max - len(pr_page_info))
                    / (i_max + pr_max)
                )
        if progress_callback:
            self._logger.info(f"Loaded {issue_count} issues and {pr_count} PRs")
        # TODO submit work to regularly check for new issues
