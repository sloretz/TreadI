---
title: Filter Syntax
parent: Reference
---

Filter issues and pull requests by typing a filter string into the box at the top of TreadI's issue screen.

The filter syntax is similar to [Github search syntax](https://docs.github.com/en/search-github/searching-on-github/searching-issues-and-pull-requests).

* TOC
{:toc}

## Filter Syntax

### Only show issues and PRs from one user

*Example: Show all issues and PRs created by the user [sloretz](https://github.com/sloretz).*

```
author:sloretz
```

### Only show issues

*Example:*

```
is:issue
```

Alternatively, you may use `type` instead of `is`.

```
type:issue
```

### Only show pull reuests

*Example:*

```
is:pr
```

Alternatively, you may use `type` instead of `is`.

```
type:pr
```

### Only show draft pull requests

Note, this does NOT exclude issues.

*Example: Show issues and draft pull requests*

```
is:draft
```

Combine with `is:pr` to show only draft pull requests

*Example: Show only draft pull requests*

```
is:pr is:draft
```

### Only show issues and pull requests from one organization

*Example: Show only issues and PRs from the [ros2 organization](https://github.com/ros2)*

```
org:ros2
```

### Only show issues and pull requests from one repository

*Example: Show only issues and PRs from the [ros/rosdistro repository](https://github.com/ros/rosdistro)*

```
repo:ros/rosdistro
```

### Invert a filter

Invert any filter by prepending a `-` character.

*Example: Exclude draft PRs*

```
-is:draft
```

### Combine multiple filters

Combine filters by putting a space between them.

*Example: Show PRs created by `sloretz` that are in any repository except `ros/rosdistro`*

```
is:pr author:sloretz -repo:ros/rosdistro
```
