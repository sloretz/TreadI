import kivy

kivy.require("2.3.1")

from kivy.app import App
from kivy.config import Config as KvConfig

KvConfig.set("graphics", "resizable", False)
KvConfig.set("input", "mouse", "mouse,disable_multitouch")
KvConfig.set("kivy", "exit_on_escape", 0)

from kivy.core.window import Window

Window.size = (500, 558)

from kivy.uix.screenmanager import ScreenManager

import logging
import pathlib

from gql import Client
from gql.transport.requests import RequestsHTTPTransport

from . import auth
from . import config
from .issue_cache import IssueCache
from .screens.issue_screen import IssueScreen
from .screens.login_screen import LoginScreen
from .screens.repo_picker_screen import RepoPickerScreen


def make_gql_client(access_token):
    transport = RequestsHTTPTransport(
        url="https://api.github.com/graphql",
        headers={
            "Authorization": f"bearer {access_token}",
        },
        verify=True,
        retries=3,
    )
    schema_path = pathlib.Path(__file__).parent.resolve() / "schema.docs.graphql"
    return Client(transport=transport, schema=schema_path.read_text())


class TreadIApp(App):

    # Globals accessible to all screens
    gql_client = None
    issue_loader = None
    issue_cache = IssueCache()
    sm = None

    def make_client_from_response(self, token_response):
        if token_response.status == auth.Status.ACCESS_GRANTED:
            self.gql_client = make_gql_client(token_response.access_token)
            return True
        return False

    def on_login_result(self, _, token_response):
        if self.make_client_from_response(token_response):
            auth.store_refresh_token(token_response.refresh_token)
            self.switch_to_pick_repos()
        else:
            raise RuntimeError(
                f"TODO more graceful response to login failure {token_response}"
            )

    def switch_to_pick_repos(self, direction="left"):
        """Called to switch to repo picker screen and reset."""
        # This avoids a circular dependency in screen modules
        issue_loader = None
        issue_cache = IssueCache()
        self.sm.transition.direction = direction
        self.sm.switch_to(RepoPickerScreen())

    def build(self):
        # Window.always_on_top = True

        self.sm = ScreenManager()
        config.create_or_update_config()

        token_response = auth.cycle_cached_token()
        if not self.make_client_from_response(token_response):
            # Ask user to login
            login_screen = LoginScreen()
            login_screen.bind(token_response=self.on_login_result)
            self.sm.switch_to(login_screen)
        else:
            self.switch_to_pick_repos()

        return self.sm


def main():
    TreadIApp().run()


if __name__ == "__main__":
    main()
