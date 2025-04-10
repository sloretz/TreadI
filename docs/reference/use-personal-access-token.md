---
title: Personal access tokens
parent: Reference
---

TreadI needs to make API requests on your behalf in order to load issues and pull requests.
The default authentication method uses TreadI's [Github App](https://docs.github.com/en/apps/overview).
However, this only gives TreadI read access to public repositories.

If you want to use TreadI with private repositories, then you must use a [personal access token](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens).

## Create a personal access token for TreadI

Navigate to [https://github.com/settings/tokens](https://github.com/settings/tokens).

In the top right, click "Generate new token", then click the "Fine-grained, repo-scoped" option.

![Github Generate new token button](docs/images/generate-new-token.png)

Give the token a memorable name, like `TreadI Personal Access Token`.

![Github Token name input box](docs/images/new-token-name.png)

Under the `Repository access section`, choose `Only select repositories`, and choose the repositories you want to give TreadI access to.

![Github Repository Access section](docs/images/new-token-only-select-repositories.png)

Click `Generate token`.

Copy the generated token text.
It should begin with text like `github_pat_`.

![Github new token value](docs/images/new-token-value.png)

## Give Treadi the personal access token

TreadI saves and loads tokens using the [keyring package](https://pypi.org/project/keyring/).
Save the new token by running the following command in a terminal:

```
keyring set TreadI GithubPersonalAccessToken
```

The command will ask you for the `password`.
The `password` is the value of the personal access token you just created.
Paste the token into the prompt and hit `[Enter]` to store it.

TreadI will use this personal access token when you restart it.

## Delete a personal access token

If you decide you want TreadI to stop using a personal access token, then you must delete the token from the keyring.
Delete the token by running the following command:

```
keyring del TreadI GithubPersonalAccessToken
```
