from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Repository:
    owner: str = ""
    name: str = ""


@dataclass
class Issue:
    repo: Repository = Repository
    author: str = ""
    created_at: datetime = None
    updated_at: datetime = None
    number: int = 0
    title: str = ""
    url: str = ""
    is_pr: bool = False


@dataclass
class PullRequest(Issue):
    is_pr: bool = True
    approved: bool = False
    changes_requested: bool = False
    draft: bool = False


def is_same_issue(l, r):
    return l.repo == r.repo and l.number == r.number
