import sys
import time
from random import randint
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException

from crawler import browser


class Login(object):
    def __init__(self, browser):
        self.browser = browser

    def safe_find_element_by_id(self, elem_id):
        try:
            return self.browser.find_element(By.ID,elem_id)
        except NoSuchElementException:
            return None

    def login(self, email, password):
        try:
            self.browser.get("https://www.facebook.com")
            self.browser.maximize_window()

            time.sleep(randint(3, 5))

            # filling the form
            #self.browser.find_element_by_name('email').send_keys(email)
            #self.browser.find_element_by_name('pass').send_keys(password)

            self.browser.find_element(By.NAME, 'email').send_keys(email)

            time.sleep(randint(4, 5))

            self.browser.find_element(By.NAME, 'pass').send_keys(password)

            time.sleep(randint(5, 8))

            # clicking on login button
            # self.browser.find_element_by_id('loginbutton').click()
            # self.browser.find_element_by_id('u_0_5_C2').click()
            self.browser.find_element(By.NAME, 'login').click()

            # if your account uses multi factor authentication
            mfa_code_input = self.safe_find_element_by_id('approvals_code')

            if mfa_code_input is None:
                return
            else:
                print("mfa_code_input::::::   "+mfa_code_input)

            mfa_code_input.send_keys(input("Enter MFA code: "))
            self.browser.find_element(By.ID,'checkpointSubmitButton').click()

            # there are so many screens asking you to verify things. Just skip them all
            while self.safe_find_element_by_id('checkpointSubmitButton') is not None:
                dont_save_browser_radio = self.safe_find_element_by_id('u_0_3')
                if dont_save_browser_radio is not None:
                    dont_save_browser_radio.click()

                self.browser.find_element(By.ID,'checkpointSubmitButton').click()

        except Exception as e:
            print("There's some error in log in.")
            print(e)
            print(sys.exc_info()[2])
            exit()


if __name__ == "__main__":
    browsers = browser.Browser(0).getBrowser()
    browsers.get("https://www.facebook.com/")