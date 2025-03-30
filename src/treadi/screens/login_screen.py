import webbrowser

from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen

from .. import auth


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
