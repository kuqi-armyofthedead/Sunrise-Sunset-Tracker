import requests
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.window import Window

API_URL = "https://api.sunrise-sunset.org/json"


class SunTracker(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)

        Window.clearcolor = (0.1, 0.1, 0.1, 1)  # dark mode background
        self.location_input = TextInput(
            hint_text="Enter location as 'lat,lon' (e.g. 40.7128,-74.0060)",
            multiline=False,
            size_hint_y=None,
            height=40
        )
        self.add_widget(self.location_input)

        self.fetch_btn = Button(
            text="Fetch Sunrise & Sunset Times",
            size_hint_y=None,
            height=50,
            background_color=(0.2, 0.6, 0.9, 1)
        )
        self.fetch_btn.bind(on_press=self.get_sun_times)
        self.add_widget(self.fetch_btn)

        self.info_label = Label(
            text="Enter coordinates and tap Fetch.",
            halign="center",
            valign="middle"
        )
        self.add_widget(self.info_label)

        self.alert_label = Label(
            text="",
            color=(1, 0.8, 0, 1),
            font_size='18sp',
            bold=True
        )
        self.add_widget(self.alert_label)

    def get_sun_times(self, instance):
        """Fetch sunrise and sunset data for given lat/lon."""
        coords = self.location_input.text.strip()

        if not coords:
            self.info_label.text = "❗ Please enter coordinates."
            return

        try:
            lat, lon = map(float, coords.split(","))
        except ValueError:
            self.info_label.text = "⚠️ Invalid format! Use: 40.7128,-74.0060"
            return

        self.info_label.text = "⏳ Fetching data..."
        Clock.schedule_once(lambda dt: self.fetch_data(lat, lon), 0)

    def fetch_data(self, lat, lon):
        """Run API call (in a separate thread-safe Kivy way)."""
        try:
            response = requests.get(API_URL, params={"lat": lat, "lng": lon, "formatted": 0}, timeout=10)
            response.raise_for_status()
            data = response.json()
        except (requests.RequestException, ValueError) as e:
            self.info_label.text = f"❌ Error: {e}"
            return

        if data.get("status") != "OK":
            self.info_label.text = "⚠️ API returned an error."
            return

        results = data["results"]
        self.display_results(results)

    def display_results(self, results):
        """Display sunrise/sunset in local time and schedule alerts."""
        try:
            sunrise_utc = datetime.datetime.fromisoformat(results["sunrise"].replace("Z", "+00:00"))
            sunset_utc = datetime.datetime.fromisoformat(results["sunset"].replace("Z", "+00:00"))

            # Convert UTC → Local time
            offset = datetime.datetime.now() - datetime.datetime.utcnow()
            sunrise_local = sunrise_utc + offset
            sunset_local = sunset_utc + offset

            self.info_label.text = (
                f"🌅 Sunrise: {sunrise_local.strftime('%I:%M %p')}\n"
                f"🌇 Sunset:  {sunset_local.strftime('%I:%M %p')}"
            )

            # Schedule alerts 5 minutes before events
            now = datetime.datetime.now()
            events = [
                (sunrise_local - datetime.timedelta(minutes=5), "🌄 Sunrise soon! Stay indoors!"),
                (sunset_local - datetime.timedelta(minutes=5), "🌆 Sunset coming — time to go out!")
            ]

            for alert_time, message in events:
                if alert_time > now:
                    delay = (alert_time - now).total_seconds()
                    Clock.schedule_once(lambda dt, msg=message: self.send_alert(msg), delay)

        except Exception as e:
            self.info_label.text = f"⚠️ Failed to parse data: {e}"

    def send_alert(self, message):
        """Show alert message."""
        self.alert_label.text = f"⚠️ {message}"


class VampireSunApp(App):
    def build(self):
        self.title = "Vampire Sun Tracker 🧛"
        return SunTracker()


if __name__ == "__main__":
    VampireSunApp().run()
