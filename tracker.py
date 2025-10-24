import requests
import datetime
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.clock import Clock

API_URL = "https://api.sunrise-sunset.org/json"

class SunTracker(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=20, spacing=10, **kwargs)
        
        self.location_input = TextInput(hint_text="Enter location (lat,lon)", multiline=False)
        self.add_widget(self.location_input)

        self.info_label = Label(text="Enter coordinates and tap Fetch.")
        self.add_widget(self.info_label)

        self.fetch_btn = Button(text="Fetch Sunrise/Sunset")
        self.fetch_btn.bind(on_press=self.get_sun_times)
        self.add_widget(self.fetch_btn)

        self.alert_label = Label(text="")
        self.add_widget(self.alert_label)

    def get_sun_times(self, instance):
        try:
            lat, lon = map(float, self.location_input.text.split(","))
        except ValueError:
            self.info_label.text = "Please enter valid coordinates like: 40.7128,-74.0060"
            return

        params = {"lat": lat, "lng": lon, "formatted": 0}
        res = requests.get(API_URL, params=params).json()

        if res["status"] == "OK":
            sunrise_utc = datetime.datetime.fromisoformat(res["results"]["sunrise"])
            sunset_utc = datetime.datetime.fromisoformat(res["results"]["sunset"])

            # Convert to local time
            now = datetime.datetime.now()
            offset = datetime.datetime.now() - datetime.datetime.utcnow()
            sunrise_local = sunrise_utc + offset
            sunset_local = sunset_utc + offset

            self.info_label.text = (
                f"🌅 Sunrise: {sunrise_local.strftime('%I:%M %p')}\n"
                f"🌇 Sunset:  {sunset_local.strftime('%I:%M %p')}"
            )

            # Schedule alerts (5 minutes before)
            sunrise_alert = sunrise_local - datetime.timedelta(minutes=5)
            sunset_alert = sunset_local - datetime.timedelta(minutes=5)
            now = datetime.datetime.now()

            if sunrise_alert > now:
                delay = (sunrise_alert - now).total_seconds()
                Clock.schedule_once(lambda dt: self.send_alert("Sunrise soon! Stay indoors!"), delay)
            if sunset_alert > now:
                delay = (sunset_alert - now).total_seconds()
                Clock.schedule_once(lambda dt: self.send_alert("Sunset coming — time to go out!"), delay)
        else:
            self.info_label.text = "Error fetching data."

    def send_alert(self, message):
        self.alert_label.text = f"⚠️ {message}"

class VampireSunApp(App):
    def build(self):
        return SunTracker()

if __name__ == "__main__":
    VampireSunApp().run()
