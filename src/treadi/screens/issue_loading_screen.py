from kivy.app import App
from kivy.clock import Clock
from kivy.properties import NumericProperty
from kivy.uix.screenmanager import Screen

from ..issue_loader import IssueLoader


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
