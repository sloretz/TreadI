---
title: Personal access tokens
parent: Reference
---

In order to load issues and pull requests, TreadI needs to query Github's API on your behalf.
By default you authenticate through TreadI's [Github App](https://docs.github.com/en/apps/overview).
However, **this only gives TreadI read access to public repositories**.

If you want to use TreadI with a private repository, then you must give TreadI a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) that grants read access to that repository.

## Create a personal access token

Navigate to [https://github.com/settings/tokens](https://github.com/settings/tokens).

In the top right, click "Generate new token", then click the "Fine-grained, repo-scoped" option.

<img src="{{site.baseurl}}/images/generate-new-token.png" alt="Github Generate new token button" width="256"/>

Give the token a memorable name, like `TreadI Personal Access Token`.

<img src="{{site.baseurl}}/images/new-token-name.png" alt="Github Token name input box" width="512"/>

Under the `Repository access section`, choose `Only select repositories`, and choose the repositories you want to give TreadI read access to.

<img src="{{site.baseurl}}/images/new-token-only-select-repositories.png" alt="Github Repository Access section" width="512"/>

Click `Generate token`.

Copy the generated token.

<img src="{{site.baseurl}}/images/new-token-value.png" alt="Github new token value" width="512"/>

## Give Treadi your personal access token

TreadI uses the [keyring package](https://pypi.org/project/keyring/) to store Github tokens.
Store the new token by running the following command in a terminal:

```
keyring set TreadI GithubPersonalAccessToken
```

When the command asks you for a `password`, paste the value of the personal access token you created.
Hit `[Enter]` to store it.

TreadI will use this personal access token as soon as you restart it.

## Delete your personal access token

If you've saved a personal access token, then TreadI will always try to use it, even if the token expires.

If you want TreadI to stop using your personal access token, then you must delete it from your keyring.
Delete the token by running the following command:

```
keyring del TreadI GithubPersonalAccessToken
```
