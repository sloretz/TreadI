import logging
import webbrowser

from kivy.animation import Animation
from kivy.app import App
from kivy.properties import ColorProperty
from kivy.properties import ObjectProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.screenmanager import Screen

from ..data import Issue
from ..data import is_same_issue
from ..filter import parse as parse_filter


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
