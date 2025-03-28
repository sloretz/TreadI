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
from .data import Issue
from .data import is_same_issue
from .issue_cache import IssueCache
from .issue_loader import IssueLoader
from .repo_loader import CurrentUserRepoLoader
from .repo_loader import OrgRepoLoader
from .repo_loader import FileRepoLoader
from .repo_loader import SequentialRepoLoaders
from .repo_loader import VcsRepoLoader
from .filter import parse as parse_filter


USERNAME = None
REPOS = None
ISSUES = None


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


class IssueWidget(ButtonBehavior, BoxLayout):

    color = ColorProperty(defaultvalue=[0.6, 0.6, 0.6, 1])

    issue = ObjectProperty(
        Issue(),
        rebind=True,
    )

    def __init__(self, issue, dismiss_callback, **kwargs):
        self.issue = issue
        self.dismiss_callback = dismiss_callback
        super().__init__(**kwargs)

    def on_press(self):
        if self.last_touch.button == "left":
            self.color = [0.6, 0.6, 0.8, 1]

    def on_release(self):
        # Oh yeah, the whole point is to open the issue
        if self.last_touch.button == "left":
            webbrowser.open(self.issue.url)

    def do_dismiss_callback(self):
        # Only dismiss once
        if self.dismiss_callback is not None:
            d = self.dismiss_callback
            self.dismiss_callback = None
            d(self)


class IssueScreen(Screen):

    def __init__(self, *args, **kwargs):
        self._filter = None
        self._logger = logging.getLogger("IssueLoader")
        super().__init__(*args, **kwargs)

    def validate_filter(self):
        # Called when on_validate_text is called on filter TextInput
        filter_str = self.ids.filter.text
        if filter_str.strip() == "":
            self._filter = None
            self.ids.filter.background_color = (1, 1, 1, 1)
        else:
            try:
                self._filter = parse_filter(filter_str.strip())
                self.ids.filter.background_color = (0.9, 1, 0.9, 1)
            except:
                self._logger.exception("Cannot parse filter")
                self._filter = None
                self.ids.filter.background_color = (1, 0.5, 0.5, 1)

        self._refresh_issues()

    def on_text_changing(self):
        # called hen on_text is called on filter TextInput
        # Filters don't apply until the user hits enter, so display as yellow
        self.ids.filter.background_color = (1, 1, 0.9, 1)

    def on_pre_enter(self):
        issue_cache = App.get_running_app().issue_cache
        self._refresh_issues()

    def _refresh_issues(self):
        # Clear and re-add issues
        self.ids.stack.clear_widgets()
        issue_cache = App.get_running_app().issue_cache
        issues = issue_cache.most_recent_issues(n=5, filter=self._filter)
        for i in issues:
            self._add_issue(i)

    def _add_issue(self, issue):
        self.ids.stack.add_widget(IssueWidget(issue, self.dismiss))

    def dismiss(self, issue_widget):
        issue = issue_widget.issue
        issue_cache = App.get_running_app().issue_cache

        issue_cache.dismiss(issue)

        child_issues = []
        for child in self.ids.stack.children:
            if hasattr(child, "issue"):
                child_issues.append(child.issue)

        # aim for 1 additional issue, because one is being dismissed
        consider_issues = issue_cache.most_recent_issues(
            n=1 + len(child_issues), filter=self._filter
        )
        for itc in consider_issues:
            displaying_issue = False
            for chi in child_issues:
                if is_same_issue(itc, chi):
                    displaying_issue = True
                    break
            if not displaying_issue:
                self._add_issue(itc)
                break

        # Animate the dismissed widget shrinking, so new issue reveals from below
        anim = Animation(
            size_hint_y=0, opacity=0, duration=0.125, transition="out_cubic"
        )
        anim.bind(on_complete=lambda *args: self.ids.stack.remove_widget(issue_widget))
        anim.start(issue_widget)


class RepoPickerScreen(Screen):

    def use_all_user_repos(self):
        self.manager.switch_to(
            RepoLoadingScreen(CurrentUserRepoLoader(App.get_running_app().gql_client))
        )

    def use_all_gazebo_repos(self):
        self.manager.switch_to(
            RepoLoadingScreen(
                SequentialRepoLoaders(
                    repo_loaders=[
                        OrgRepoLoader("gazebosim", App.get_running_app().gql_client),
                        OrgRepoLoader(
                            "gazebo-tooling", App.get_running_app().gql_client
                        ),
                        OrgRepoLoader(
                            "gazebo-release", App.get_running_app().gql_client
                        ),
                    ],
                )
            )
        )

    def use_all_rmf_repos(self):
        self.manager.switch_to(
            RepoLoadingScreen(
                OrgRepoLoader("open-rmf", App.get_running_app().gql_client)
            )
        )

    def use_all_infra_repos(self):
        self.manager.switch_to(
            RepoLoadingScreen(
                VcsRepoLoader(
                    "https://raw.githubusercontent.com/ros-infrastructure/ci/refs/heads/main/ros-infrastructure.repos"
                )
            )
        )

    def use_all_ros_repos(self):
        self.manager.switch_to(
            RepoLoadingScreen(
                FileRepoLoader(
                    pathlib.Path(__file__).parent.resolve() / "ros_pmc_repos.txt"
                )
            )
        )


class RepoLoadingScreen(Screen):

    def __init__(self, loader, **kwargs):
        self._loader = loader
        self._loader.begin_loading(self.switch_to_issue_loading)
        super().__init__(**kwargs)

    def switch_to_issue_loading(self, repos):

        def _switch(dt):
            self.manager.switch_to(IssueLoadingScreen(repos))

        Clock.schedule_once(lambda dt: self._loader.cleanup())
        Clock.schedule_once(_switch)


class IssueLoadingScreen(Screen):

    progress = NumericProperty(0.0)

    def __init__(self, repos, **kwargs):
        App.get_running_app().issue_loader = IssueLoader(
            App.get_running_app().gql_client,
            repos,
            App.get_running_app().issue_cache,
            self.update_progress,
        )
        super().__init__(**kwargs)

    def update_progress(self, progress):
        self.progress = progress * 100
        if progress >= 1.0:
            Clock.schedule_once(lambda dt: self.switch_to_issues())

    def switch_to_issues(self):
        # Must only be called on main thread
        self.manager.transition.direction = "left"
        self.manager.current = "issues"


class LoginScreen(Screen):

    device_flow = ObjectProperty(
        auth.DeviceFlow(
            device_code="",
            user_code="",
            verification_uri="",
            interval=0,
            expires_in=0,
        ),
        rebind=True,
    )
    token_response = ObjectProperty()

    def on_enter(self):
        self.start_device_flow()

    def start_device_flow(self):
        self.device_flow = auth.start_device_flow()
        print("Device flow started: ", self.device_flow)
        Clock.schedule_once(lambda dt: self.check_auth(), self.device_flow.interval)

    def open_browser(self, url):
        webbrowser.open(url)

    def check_auth(self):
        response = auth.ask_for_token(self.device_flow)
        match response.status:
            case auth.Status.AUTHORIZATION_PENDING:
                Clock.schedule_once(
                    lambda dt: self.check_auth(), self.device_flow.interval
                )
            case auth.Status.EXPIRED_TOKEN:
                self.start_device_flow()
            case auth.Status.ACCESS_DENIED:
                raise RuntimeError(
                    "TODO nice error message when user denies TreadI App"
                )
            case auth.Status.ACCESS_GRANTED:
                # Listeners on the token_response property are notified here
                self.token_response = response
            case _:
                raise RuntimeError(
                    f"TODO nice error message when other error encountered{response}"
                )


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
