from kivymd.app import MDApp
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.core.clipboard import Clipboard
from kivy.config import Config
from kivymd.uix.expansionpanel import MDExpansionPanel, MDExpansionPanelTwoLine, MDExpansionPanelOneLine
from kivy.uix.screenmanager import ScreenManager, Screen

Config.set('input', 'mouse', 'mouse, multitouch_on_demand')  # eliminate annoying circle drawing on right click

FPS = 25
REFRESH_RATE = 1/FPS


class TimeOverPopup(Popup):
    pass


class FinishedPopup(Popup):
    pass


class ExportOptions(BoxLayout):
    pass


class HomeScreen(Screen):
    pass


class SettingsContent(BoxLayout):
    pass


class WritingWidget(Screen):
    words_count = StringProperty()
    progress_bar = NumericProperty()
    opacity_value = NumericProperty()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.penalty_time_seconds = 10
        self.writing_time_seconds = 600
        self.penalty_time = self.penalty_time_seconds*FPS
        self.total_time = self.writing_time_seconds*FPS

        self.progress_bar = 0
        self.opacity_value = 0
        self.words_count_int = 0
        self.words_count = "0"

        self.timer_total = None
        self.timer_total_seconds = 0

        self.timer_short = None
        self.timer_short_seconds = 0

        self.writing = False

        self.time_over_popup = None
        self.export_menu = ExportOptions()

        self.written_text = ""

    def on_enter(self, *args):
        self.penalty_time_seconds = self.get_penalty_time()
        self.writing_time_seconds = self.get_writing_time()
        self.penalty_time = self.penalty_time_seconds * FPS
        self.total_time = self.writing_time_seconds * FPS

    @staticmethod
    def get_penalty_time():
        app = MDApp.get_running_app()
        penalty_time_seconds = app.penalty_time
        return penalty_time_seconds

    @staticmethod
    def get_writing_time():
        app = MDApp.get_running_app()
        writing_time_minutes = app.writing_time
        return writing_time_minutes*60

    def check_text(self, text_obj):
        if not self.writing:
            self.start_timer_total_time(time_in_seconds=REFRESH_RATE)
            self.writing = True
            print(f"Total time: {self.total_time/FPS/60} minutes")
            print(f"Penalty time: {self.penalty_time/FPS} seconds")
        self.count_words(text=text_obj.text)
        self.start_timer_short(refresh_rate=REFRESH_RATE)

    def count_words(self, text):
        self.words_count_int = len(text.split())
        self.words_count = str(self.words_count_int)

    def start_timer_total_time(self, time_in_seconds):
        self.timer_total = Clock.schedule_interval(self.update_on_total_timer, time_in_seconds)

    def update_on_total_timer(self, dt):
        self.timer_total_seconds += 1
        if self.timer_total_seconds >= self.total_time:
            self.total_time_passed(dt)
        else:
            self.update_progress_bar(current_time=self.timer_total_seconds)

    def update_progress_bar(self, current_time):
        percent = (current_time*100)/self.total_time
        self.progress_bar = percent

    def total_time_passed(self, dt):
        time_over_button = FinishedPopup()
        time_over_button.open()
        self.progress_bar = 100
        self.ids.text_field.focus = False
        self.ids.text_field.disabled = True
        self.writing = False
        self.written_text = self.ids.text_field.text

        Clock.unschedule(self.timer_short)
        Clock.unschedule(self.timer_total)

        app = MDApp.get_running_app()
        writing_screen = app.root.get_screen('writing')
        writing_screen.ids.writing_screen.add_widget(self.export_menu)

    def start_timer_short(self, refresh_rate):
        if self.timer_short:
            Clock.unschedule(self.timer_short)
            self.opacity_value = 0
            self.timer_short_seconds = 0
        self.timer_short = Clock.schedule_interval(self.update_on_short_timer, refresh_rate)

    def update_on_short_timer(self, dt):
        self.timer_short_seconds += 1
        if self.timer_short_seconds >= self.penalty_time:
            self.timer_short_passed(dt)
        else:
            self.update_opacity(current_time=self.timer_short_seconds)

    def update_opacity(self, current_time):
        percent = int((current_time*100)/self.penalty_time)
        self.opacity_value = percent/100

    def timer_short_passed(self, dt):
        time_over_button = TimeOverPopup()
        time_over_button.open()
        self.reset_app(keep_text=False, penalty=True)

    def reset_app(self, keep_text, penalty=False):
        text_field = self.ids.text_field
        if keep_text:
            text_field.text = self.written_text
        else:
            text_field.text = ""

        self.progress_bar = 0
        self.writing = False
        self.ids.text_field.disabled = False
        self.timer_total_seconds = 0

        Clock.unschedule(self.timer_short)
        Clock.unschedule(self.timer_total)
        if not penalty:
            self.remove_export_menu()

    def copy_text(self):
        Clipboard.copy(self.ids.text_field.text)

    def remove_export_menu(self):
        writing_screen = self.ids.writing_screen
        writing_screen.remove_widget(writing_screen.children[0])


class MDExpansionPanelTwoLines:
    pass


class WriteThisApp(MDApp):
    writing_time = NumericProperty(10)
    penalty_time = NumericProperty(10)

    def build(self):
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Teal"

        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        sm.add_widget(WritingWidget(name='writing'))

        return sm

    def on_start(self):
        home_screen = self.root.get_screen('home')
        home_screen.ids.home_screen.add_widget(
            MDExpansionPanel(
                content=SettingsContent(),
                panel_cls=MDExpansionPanelTwoLine(
                    text="SETTINGS"
                )
            )
        )


if __name__ == "__main__":
    WriteThisApp().run()
