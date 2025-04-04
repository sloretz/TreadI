from dataclasses import dataclass

from enum import Enum
import requests
import urllib

from . import CLIENT_ID

import keyring


SERVICE = "TreadI"
REFRESH_TOKEN_USERNAME = "GithubRefreshToken"
PAT_TOKEN_USERNAME = "GithubPersonalAccessToken"


def get_refresh_token():
    refresh_token = keyring.get_password(SERVICE, REFRESH_TOKEN_USERNAME)
    if refresh_token is not None:
        keyring.delete_password(SERVICE, REFRESH_TOKEN_USERNAME)
    return refresh_token


def store_refresh_token(refresh_token):
    keyring.set_password(SERVICE, REFRESH_TOKEN_USERNAME, refresh_token)


def load_personal_access_token():
    # Returns None if no PAT is stored in the keyring
    return keyring.get_password(SERVICE, PAT_TOKEN_USERNAME)


@dataclass
class DeviceFlow:

    device_code: str
    user_code: str
    verification_uri: str
    interval: int
    expires_in: int


def start_device_flow(*, client_id=CLIENT_ID):
    url = "https://github.com/login/device/code"
    r = requests.post(url, data={"client_id": client_id})
    if r.status_code != 200:
        raise RuntimeError(f"TODO Handle device code request failure {r}")
    response = urllib.parse.parse_qs(r.text)

    return DeviceFlow(
        device_code=response["device_code"][0],
        user_code=response["user_code"][0],
        verification_uri=response["verification_uri"][0],
        # Plus 1 because I get a bunch erroneous slow_down errors.
        # Even the official gh CLI gets these
        # https://github.com/cli/cli/issues/9370
        interval=int(response["interval"][0]) + 1,
        expires_in=int(response["expires_in"][0]),
    )


class Status(Enum):
    # The user gave TreadI the access it needs
    ACCESS_GRANTED = 1
    # Waiting for the user to make a decision
    AUTHORIZATION_PENDING = 10
    # User took too long. The process needs to be started over
    EXPIRED_TOKEN = 12
    # User denied TreadI access
    ACCESS_DENIED = 13
    # Refresh token is invalid
    INCORRECT_CLIENT_CREDENTIALS = 51
    # Something else that TreadI doesn't handle specifically
    OTHER_ERROR = 100
    # Not a github error, this means there's no cached refresh token
    NO_TOKEN = 1001


@dataclass
class TokenResponse:
    status: Status
    access_token: str = None
    refresh_token: str = None


def ask_for_token(device_flow, *, client_id=CLIENT_ID):
    data = {
        "client_id": client_id,
        "device_code": device_flow.device_code,
        "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
    }
    r = requests.post("https://github.com/login/oauth/access_token", data=data)
    if r.status_code != 200:
        return TokenResponse(status=Status.OTHER_ERROR)
    response = urllib.parse.parse_qs(r.text)
    print(response)
    if "interval" in response:
        device_flow.interval = int(response["interval"][0])
    if "error" in response.keys():
        match response["error"][0]:
            case "slow_down" | "authorization_pending":
                return TokenResponse(status=Status.AUTHORIZATION_PENDING)
            case "access_denied":
                return TokenResponse(status=Status.ACCESS_DENIED)
            case _:
                return TokenResponse(status=Status.OTHER_ERROR)
    return TokenResponse(
        status=Status.ACCESS_GRANTED,
        access_token=response["access_token"][0],
        refresh_token=response["refresh_token"][0],
    )


def refresh_access_token(refresh_token, *, client_id=CLIENT_ID):
    data = {
        "client_id": client_id,
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
    }
    r = requests.post("https://github.com/login/oauth/access_token", data=data)
    if r.status_code != 200:
        return TokenResponse(status=Status.OTHER_ERROR)
    response = urllib.parse.parse_qs(r.text)
    if "error" in response.keys():
        match response["error"][0]:
            case "incorrect_client_credentials":
                return TokenResponse(status=Status.INCORRECT_CLIENT_CREDENTIALS)
            case _:
                return TokenResponse(status=Status.OTHER_ERROR)
    return TokenResponse(
        status=Status.ACCESS_GRANTED,
        access_token=response["access_token"][0],
        refresh_token=response["refresh_token"][0],
    )


def cycle_cached_token():
    rt = get_refresh_token()
    if rt is None:
        return TokenResponse(status=Status.NO_TOKEN)
    response = refresh_access_token(rt)
    if response.status == Status.ACCESS_GRANTED:
        store_refresh_token(response.refresh_token)
    return response


def get_personal_access_token() -> TokenResponse:
    pat = load_personal_access_token()
    if pat is None:
        return TokenResponse(status=Status.NO_TOKEN)

    return TokenResponse(status=Status.ACCESS_GRANTED, access_token=pat)
