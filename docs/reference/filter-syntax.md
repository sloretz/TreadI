---
title: Filter Syntax
parent: Reference
---

Filter issues and pull requests by typing a filter string into the box at the top of TreadI.

It uses a subset of the [Github search syntax](https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests).

Combine filters by putting a space ` ` between them.
Invert any filter by prepending a `-` character.

**Example:** *Show PRs authored by `sloretz` that are in any repository except `ros/rosdistro`*

```
is:pr author:sloretz -repo:ros/rosdistro
```


## author:USERNAME

Show all issues and PRs opened by the user `USERNAME`.

**Example:** *Show all issues and PRs opened by the user [sloretz](https://github.com/sloretz).*

```
author:sloretz
```

## is:issue

**Example:** *Show only issues*

```
is:issue
```

## is:pr

**Example:** *Show only pull requests*

```
is:pr
```

## is:draft

Only show draft pull requests.
Note, this does NOT exclude issues.

**Example:** *Show issues and draft pull requests*

```
is:draft
```

Combine with `is:pr` to show only draft pull requests

**Example:** *Show only draft pull requests*

```
is:pr is:draft
```

####


* `is:issue` - Show only Issues
* `is:issue` - Show only PRs
* `org:OWNER` - Show only PRs from the given organization or user
* `repo:owner/name` - Show only things from the repo `owner/name`
* `type:issue` - Same as `is:issue`
* `type:pr` - Same as `is:pr`

Invert filters by prepending `-`.

