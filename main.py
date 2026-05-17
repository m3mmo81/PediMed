from kivy.app import App
from kivy.uix.browser import WebView

class PediMedApp(App):
    def build(self):
        browser = WebView()
        browser.loadUrl('https://pedimed-cqpzmf9jxtueqkplhpyppn.streamlit.app/')
        return browser

if __name__ == '__main__':
    PediMedApp().run()
