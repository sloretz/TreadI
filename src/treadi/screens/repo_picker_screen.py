from importlib.metadata import version

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.button import Button
from kivy.uix.popup import Popup
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


class RepoPickerScreenHelpPopup(Popup):

    def __init__(self, config):
        self._version = version("TreadI")
        self._config = config
        super().__init__()


class RepoPickerScreen(Screen):

    def __init__(self, *args, **kwargs):
        self._popup = None
        self._config = config.Config()
        if "name" not in kwargs:
            kwargs["name"] = "repo-picker-screen"
        super().__init__(*args, **kwargs)

    def on_pre_enter(self):
        for name in self._config.repository_list_names():
            btn = RepoButton(repo_picker=self, text=name)
            self.ids.stack.add_widget(btn)
        Window.bind(on_key_down=self.on_key_down)

    def on_pre_leave(self):
        Window.unbind(on_key_down=self.on_key_down)

    def on_key_down(self, window, key, scancode, codepoint, modifiers):
        if key == 47 and "shift" in modifiers:  # ? KEY
            if self._popup is None:
                self._popup = RepoPickerScreenHelpPopup(self._config)
                self._popup.bind(on_dismiss=self._forget_popup)
                self._popup.open(animation=False)
                print("Opening popup")
            else:
                self._popup.dismiss(animation=False)

    def _forget_popup(self, _):
        self._popup = None

    def use_repo_list(self, display_name):
        repo_list = self._config.repository_list(display_name)
        repo_loader = parse_repository_list(
            repo_list.content,
            # TODO pass this into repo loader
            gql_client=App.get_running_app().gql_client,
        )
        self.manager.switch_to(RepoLoadingScreen(repo_loader), direction="left")
        App.get_running_app().title += f": {display_name}"
