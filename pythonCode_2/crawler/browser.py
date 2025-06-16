import logging
import os
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.firefox.service import Service


class Browser:
    logger = logging.getLogger('django.project.requests')
    selenium_retries = 0

    def __init__(self, proxyUse):
        self.proxyUse = proxyUse
        # if self.proxyUse == 1:
        #     self.ProxyPort = ProxyInfo().getProxy()

    def get_option(self):
        options = FirefoxOptions()

        # New lines for direct login with existing Firefox profile
        firefox_profile_path = r"....."

        # Set the Firefox profile for Selenium
        profile = webdriver.FirefoxProfile(firefox_profile_path)
        profile.set_preference("dom.webnotifications.enabled", False)
        profile.set_preference("app.update.enabled", False)
        profile.update_preferences()

        options.profile = profile  # Apply the profile to options

        return options

    def get_proxy(self):
        # This part is not necessary for your current setup since we're using the profile directly
        # firefox_capabilities = webdriver.DesiredCapabilities.FIREFOX
        # firefox_capabilities['marionette'] = True
        #
        # firefox_capabilities['proxy'] = {
        #     "proxyType": "MANUAL",
        #     "httpProxy": self.ProxyPort,
        #     "ftpProxy": self.ProxyPort,
        #     "sslProxy": self.ProxyPort
        # }
        # return firefox_capabilities
        pass

    def getBrowser(self):
        print("getBrowser")
        dir_path = os.path.dirname(os.path.realpath(__file__))
        print("dir_path:", dir_path)

        GECKODRIVER = 'E:\\geckodriver.exe'
        print("GECKODRIVER: ", GECKODRIVER)

        # Commenting out unnecessary lines
        # PROFILE = webdriver.FirefoxProfile()
        # PROFILE.set_preference("dom.webnotifications.enabled", False)
        # PROFILE.set_preference("app.update.enabled", False)
        # PROFILE.update_preferences()

        options = self.get_option()

        service = Service(executable_path=GECKODRIVER)
        browser = webdriver.Firefox(service=service, options=options)
        return browser


if __name__ == "__main__":
    browser = Browser(0).getBrowser()
    browser.get("https://www.facebook.com/")  # Directly open Facebook using the logged-in profile
