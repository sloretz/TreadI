from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.screenmanager import Screen

from .. import config
from ..repo_loader import parse_repository_list
from .repo_loading_screen import RepoLoadingScreen


class RepoButton(Button):
    """RepoPickerScreen button.

    This is a class so I can customize in kv language.
    """

    def __init__(self, repo_picker, *args, **kwargs):
        self._repo_picker = repo_picker
        self._display_name = kwargs["text"]
        super().__init__(*args, **kwargs)

    def on_release(self):
        self._repo_picker.use_repo_list(self._display_name)


class RepoPickerScreen(Screen):

    def __init__(self, *args, **kwargs):
        self._config = config.Config()
        super().__init__(*args, **kwargs)

    def on_pre_enter(self):
        for name in self._config.repository_list_names():
            btn = RepoButton(repo_picker=self, text=name)
            self.ids.stack.add_widget(btn)

    def use_repo_list(self, display_name):
        repo_list = self._config.repository_list(display_name)
        repo_loader = parse_repository_list(
            repo_list.content,
            # TODO pass this into repo loader
            gql_client=App.get_running_app().gql_client,
        )
        self.manager.switch_to(RepoLoadingScreen(repo_loader))
