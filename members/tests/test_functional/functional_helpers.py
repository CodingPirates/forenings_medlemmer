from selenium.webdriver.common.by import By


def log_in(self, person):
    password = "rioguyp34098gy"
    person.user.set_password(password)
    person.user.email = person.email
    person.user.save()
    person.save()
    # Loads the login page
    self.browser.get(f"{self.live_server_url}/account/login/")

    # Enter username
    field = self.browser.find_element(By.NAME, "username")
    field.send_keys(person.email)

    # Enter username
    field = self.browser.find_element(By.NAME, "password")
    field.send_keys(password)

    # Click log ind button
    self.browser.find_element(By.XPATH, "//input[@type='submit']").click()


def get_text_contains(browser, text):
    return browser.find_elements_by_xpath(f"//*[text()[contains(.,'{text}')]]")
