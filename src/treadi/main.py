import kivy

kivy.require("2.3.1")

from kivy.animation import Animation
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config

Config.set("graphics", "resizable", False)
Config.set("input", "mouse", "mouse,disable_multitouch")
from kivy.core.window import Window

Window.size = (500, 558)
from kivy.properties import ColorProperty
from kivy.properties import NumericProperty
from kivy.properties import ObjectProperty

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.stacklayout import StackLayout
from kivy.uix.widget import Widget
from kivy.uix.screenmanager import ScreenManager, Screen

import urllib
import webbrowser
import requests
import threading
import time
import logging
import pathlib

from gql import gql, Client
from gql.transport.requests import RequestsHTTPTransport

from . import auth
from . import config
from .data import Issue
from .data import is_same_issue
from .issue_cache import IssueCache
from .issue_loader import IssueLoader
from .filter import parse as parse_filter
from .screens.issue_screen import IssueScreen
from .screens.login_screen import LoginScreen
from .screens.repo_loading_screen import RepoLoadingScreen
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
            self.sm.transition.direction = "left"
            self.sm.current = "repos"
        else:
            raise RuntimeError(
                f"TODO more graceful response to login failure {token_response}"
            )

    def build(self):
        # Window.always_on_top = True

        self.sm = ScreenManager()
        config.create_or_update_config()

        token_response = auth.cycle_cached_token()
        if not self.make_client_from_response(token_response):
            # Ask user to login
            login_screen = LoginScreen()
            login_screen.bind(token_response=self.on_login_result)
            self.sm.add_widget(login_screen)

        self.sm.add_widget(RepoPickerScreen(name="repos"))
        self.sm.add_widget(IssueScreen(name="issues"))

        return self.sm


def main():
    TreadIApp().run()


if __name__ == "__main__":
    main()
