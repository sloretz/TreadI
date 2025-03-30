from kivy.clock import Clock
from kivy.uix.screenmanager import Screen

from .issue_loading_screen import IssueLoadingScreen


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
