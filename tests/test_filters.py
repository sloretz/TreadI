import copy

from treadi.data import Issue
from treadi.data import PullRequest
from treadi.data import Repository
import treadi.filter as tf

REPO_ROS_ROSDITRO = Repository(
    owner="ros",
    name="rosdistro",
)
REPO_ROS2_ROS2 = Repository(
    owner="ros2",
    name="ros2",
)
ISSUE_ROS_ROSDISTRO = Issue(
    repo=REPO_ROS_ROSDITRO,
    author="sloretz",
    created_at=None,
    updated_at=None,
    number=42,
    title="fix stuff",
    url="",
    is_pr=False,
)
PR_ROS_ROSDISTRO = PullRequest(
    repo=REPO_ROS_ROSDITRO,
    author="ghost",
    created_at=None,
    updated_at=None,
    number=1,
    title="break stuff",
    url="",
    is_pr=True,
)
DRAFT_PR_ROS_ROSDISTRO = PullRequest(
    repo=REPO_ROS_ROSDITRO,
    author="ghost",
    created_at=None,
    updated_at=None,
    number=1,
    title="break stuff",
    url="",
    is_pr=True,
    draft=True,
)
APPROVED_PR_ROS_ROSDISTRO = PullRequest(
    repo=REPO_ROS_ROSDITRO,
    author="ghost",
    created_at=None,
    updated_at=None,
    number=1,
    title="break stuff",
    url="",
    is_pr=True,
    approved=True,
)
CHANGES_REQUESTED_PR_ROS_ROSDISTRO = PullRequest(
    repo=REPO_ROS_ROSDITRO,
    author="ghost",
    created_at=None,
    updated_at=None,
    number=1,
    title="break stuff",
    url="",
    is_pr=True,
    changes_requested=True,
)


def test_require_pr():
    for f in [tf.parse("is:pr"), tf.parse("type:pr")]:
        assert f(PR_ROS_ROSDISTRO)
        assert not f(ISSUE_ROS_ROSDISTRO)


def test_require_issue():
    for f in [tf.parse("is:issue"), tf.parse("type:issue")]:
        assert f(ISSUE_ROS_ROSDISTRO)
        assert not f(PR_ROS_ROSDISTRO)


def test_require_author():
    f = tf.parse("author:sloretz")
    assert f(ISSUE_ROS_ROSDISTRO)
    f = tf.parse("author:bob")
    assert not f(ISSUE_ROS_ROSDISTRO)


def test_require_repo():
    assert tf.RequireRepo("ros", "rosdistro")(ISSUE_ROS_ROSDISTRO)
    assert not tf.RequireRepo("ros2", "ros2")(ISSUE_ROS_ROSDISTRO)


def test_require_draft_if_pr():
    f = tf.parse("is:draft")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert not f(PR_ROS_ROSDISTRO)
    assert f(DRAFT_PR_ROS_ROSDISTRO)


def test_invert_require_draft_if_pr():
    f = tf.parse("-is:draft")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert f(PR_ROS_ROSDISTRO)
    assert not f(DRAFT_PR_ROS_ROSDISTRO)


def test_require_approved_if_pr():
    f = tf.parse("review:approved")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert not f(PR_ROS_ROSDISTRO)
    assert f(APPROVED_PR_ROS_ROSDISTRO)


def test_invert_require_approved_if_pr():
    f = tf.parse("-review:approved")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert f(PR_ROS_ROSDISTRO)
    assert not f(APPROVED_PR_ROS_ROSDISTRO)


def test_require_changes_requested_if_pr():
    f = tf.parse("review:changes_requested")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert not f(PR_ROS_ROSDISTRO)
    assert f(CHANGES_REQUESTED_PR_ROS_ROSDISTRO)


def test_invert_require_changes_requested_if_pr():
    f = tf.parse("-review:changes_requested")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert f(PR_ROS_ROSDISTRO)
    assert not f(CHANGES_REQUESTED_PR_ROS_ROSDISTRO)


def test_require_no_review_if_pr():
    f = tf.parse("review:none")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert f(PR_ROS_ROSDISTRO)
    assert not f(APPROVED_PR_ROS_ROSDISTRO)
    assert not f(CHANGES_REQUESTED_PR_ROS_ROSDISTRO)


def test_multiple():
    f = tf.parse("author:sloretz is:issue")
    assert f(ISSUE_ROS_ROSDISTRO)
    assert not f(PR_ROS_ROSDISTRO)
